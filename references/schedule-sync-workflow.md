# 课表同步工作流（教务系统 → 自动化脚本）

当教务系统的课表发生变化（教室调换、新增/取消课程等）时，需要同步更新以下两个脚本：
- `~/.hermes/scripts/class_reminder.py` — 课前提醒（30分钟前提醒上课）
- `~/.hermes/scripts/auto_signin.py` — 自动签到（课前5分钟创建签到）

Cron任务**不需要修改**，因为脚本内部根据课表动态判断当天是否有课。

## 步骤1：从教务系统读取课表

教务系统已在浏览器中打开（CDP端口9222），通过websocket获取页面内容。

### 切换周次

课表页面的周次下拉框是隐藏的 `<select name="zs">`（不是 `.zc-week-item`）。切换周次：

```python
cmd = {'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': '''
    (function(){
        var s = document.querySelector("select[name='zs']");
        s.value = "15";  // 目标周次
        var event = new Event("change", {bubbles: true});
        s.dispatchEvent(event);
        return "switched to week " + s.value;
    })()
'''}}
ws.send(json.dumps(cmd))
time.sleep(3)  # 等待数据刷新
```

### ⚠️ 不同周次课表可能完全不同！

教室、节数、甚至有无课都会随周次变化。**必须逐周读取**，不能假设所有周次相同。

例如：第14周只有11节课，第17周有14节课（新增了周三1-2、周三7-8、周四7-8、周五9-10）。

### 推荐：用 .lesson div 的 data 属性提取（最可靠）

```python
cmd = {'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': '''
    (function(){
        var els = document.querySelectorAll('.lesson');
        var schedule = [];
        var days = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        for (var i=0;i<els.length;i++) {
            var el = els[i];
            schedule.push({
                day: days[parseInt(el.getAttribute('data-xqj'))||0],
                jie: el.getAttribute('data-jcor'),
                kcmc: el.getAttribute('data-kcmc'),
                cdmc: el.getAttribute('data-cdmc'),
                zcd: el.getAttribute('data-zcd')
            });
        }
        return JSON.stringify(schedule);
    })()
'''}}
```

### 备选：innerText提取（不推荐，tab计数容易出错）

`document.body.innerText` 用tab分隔列，多个连续tab表示空列。解析规则：
- 内容A `	` 内容B = 相邻列
- 内容A `		` 内容B = 中间隔1个空列
- 内容A `				` 内容B = 中间隔3个空列

**常见错误**：把 `		` 后的内容当成紧邻前一列，忽略了空列。

### 批量读取多周课表

## 步骤2：解析并对比

### ⚠️ 关键Pitfall：HTML表格innerText的Tab分隔解析（2026-06-01踩坑）

教务系统课表是HTML表格，`document.body.innerText` 用 **tab字符** 分隔各列。**多个连续tab表示空列**。

**解析规则**：
- 内容A `\t` 内容B = A和B是相邻列的内容
- 内容A `\t\t` 内容B = A和B之间有**1个空列**
- 内容A `\t\t\t\t` 内容B = A和B之间有**3个空列**

**常见错误**：把 `\t\t` 后的内容当成紧邻前一列，实际上中间隔了一个空列。例如：
```
节次1: 示例班级A \t 示例班级E \t\t 示例班级D \t\t\t
```
正确解析：周一=示例班级A, 周二=示例班级E, 周三=空, 周四=示例班级D, 周五=空
**错误解析**：周一=示例班级A, 周二=示例班级E, 周三=示例班级D ← 忽略了空列！

**推荐方法：用JS按单元格提取（避免手动数tab）**：
```python
cmd = {'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': '''
    (function(){
        var rows = document.querySelectorAll("table tr");
        var result = [];
        for(var i=0;i<rows.length;i++){
            var cells = rows[i].querySelectorAll("td, th");
            var row = [];
            for(var j=0;j<cells.length;j++){
                var txt = cells[j].innerText.trim().replace(/\\n/g, "|");
                if(txt) row.push("["+j+"]"+txt);
            }
            if(row.length > 0) result.push("Row"+i+": "+row.join("  ##  "));
        }
        return result.join("\\n");
    })()
'''}}\n```\n\n如果JS提取返回空（表格可能是非标准结构），回退到innerText手动解析，但**必须正确计算tab数量**。

### 最后手段：截图 + vision_analyze

如果JS table解析和innerText都不行，用截图+视觉模型识别：
```python
page.screenshot(path="schedule.png")
# 然后用 vision_analyze 读取截图中特定列的内容
```

### ⚠️ 真实踩坑案例（2026-06-01，两次错误）

用innerText解析时，连续犯了**两次**tab计数错误：

**错误1**：节次1有3个内容（示例班级A、示例班级E、示例班级D），用2个tab分隔。
错误地解析为：周一=示例班级A, 周二=示例班级E, **周三=示例班级D**
正确解析为：周一=示例班级A, 周二=示例班级E, 周三=空, **周四=示例班级D**
原因：`\t\t` 表示**跳过一列**（周三为空），内容属于周四。

**错误2**：节次5有2个内容（示例班级B 0401、示例班级B 0301），用4个tab分隔。
错误地解析为：周一=0401, **周四=0301**
正确解析为：周一=0401, 周二-周四=空, **周五=0301**
原因：`\t\t\t\t` 表示**跳过三列**（周二、周三、周四为空），内容属于周五。

**教训**：永远不要手动数tab。要么用JS按单元格提取，要么用截图+vision_analyze。
```

如果JS提取返回空（表格可能是非标准结构），回退到innerText手动解析，但**必须正确计算tab数量**。

### 解析流程

从页面文本中提取每个节次、每天的班级和教室信息，与脚本中的SCHEDULE对比。

**class_reminder.py 的 SCHEDULE 格式**：
```python
SCHEDULE = [
    (weekday, 'jie', '班级名', '教室', '上课时间', '周次范围'),
    # weekday: 0=周一, 1=周二, ..., 4=周五
    # jie: '1-2', '3-4', '5-6', '7-8'
    # 例:
    (0, '1-2', '示例班级A', '雪峰校区2505', '08:50', '11-18'),
]
```

**auto_signin.py 的 SCHEDULE 格式**：
```python
SCHEDULE = [
    (weekday, 'jie', 'classId', '班级名', '周次范围'),
    # classId 是学习通的班级ID（不是教务系统的）
    # 例:
    (0, '1-2', '100000001', '示例班级A', '11-18'),
]
```

**注意**：两个脚本的SCHEDULE必须保持**相同的课程安排**（同一天同一节次的班级一致），但格式不同。

## 步骤3：更新脚本

对比后识别三类变化：
1. **教室变更** — 只改教室字段
2. **新增课程** — 添加新行（需确认周次范围）
3. **取消课程** — 删除对应行

用 `patch` 工具精确修改，不要重写整个SCHEDULE。

### 教室变更示例
```python
# 旧
(0, '5-6', '示例班级B', '雪峰校区2407', '14:00', '11-18'),
# 新
(0, '5-6', '示例班级B', '雪峰校区0401', '14:00', '11-18'),
```

### 新增课程示例
```python
# 在正确位置插入（按weekday排序，同weekday按jie排序）
(2, '1-2', '示例班级D', '雪峰校区2505', '08:50', '14-18'),
```

### 取消课程示例
直接删除对应行。

## 步骤4：处理每周不同的课表（周次级别差异）

教务系统中，**同一节课在不同周可能教室不同、甚至有无课都不同**。不能用一个简单的周次范围覆盖。

### 方法：多个SCHEDULE条目，按周次范围拆分

```python
# ❌ 错误：用一个范围覆盖，忽略了16周教室不同
(2, '3-4', '示例班级C', '雪峰校区0302', '10:30', '14-18'),

# ✅ 正确：拆分成多个条目
(2, '3-4', '示例班级C', '雪峰校区0302', '10:30', '14-15,17-18'),  # 16周除外
(2, '3-4', '示例班级C', '雪峰校区0401', '10:30', '16'),           # 16周单独
```

### 周次范围语法

`parse_weeks()` 支持的格式：
- `'14-18'` → {14,15,16,17,18}
- `'14-15,17-18'` → {14,15,17,18}（跳过16）
- `'15'` → {15}（单周）

### 逐周验证脚本

更新后用脚本验证每周的课表是否正确：
```python
for week in [14, 15, 16, 17, 18]:
    print(f"=== 第{week}周 ===")
    for wd in range(5):
        for w, jie, cls, room, ts, weeks in SCHEDULE:
            if w == wd and week in parse_weeks(weeks):
                print(f"  {weekday_names[wd]}: 第{jie}节 {cls} {room}")
```

## 步骤5：验证

更新后运行脚本验证无语法错误：
```bash
python -c "import ast; ast.parse(open('class_reminder.py').read()); print('OK')"
python -c "import ast; ast.parse(open('auto_signin.py').read()); print('OK')"
```

## 常见问题

### Q: 教务系统显示的周次范围与脚本中不一致
A: 教务系统只显示当前查询周的课表，无法直接看到完整周次范围。如果某课程在当前周出现但脚本中没有，需要推断周次范围（通常从当前周开始到学期末）。如果某课程在当前周不出现但脚本中有，可能是该周恰好没课，不要轻易删除。

### Q: 新增课程的classId怎么获取？
A: 从学习通的班级列表API获取，或从已有的SCHEDULE中查找相同班级的classId（同一个班级在不同天的classId相同）。

### Q: 节次时间对应关系
| 节次 | 上课时间 | 课前提醒时间 | 签到时间 |
|------|---------|-------------|---------|
| 1-2节 | 08:50 | 08:40 | 08:45 |
| 3-4节 | 10:30 | 10:20 | 10:25 |
| 5-6节 | 14:00 | 13:30 | 13:55 |
| 7-8节 | 15:50 | 15:20 | 15:45 |
| 9-10节 | 19:00 | 18:30 | 18:55 |

### Q: 新增了9-10节（晚间课程）怎么办？
A: 需要：
1. 在 `class_reminder.py` 的 `TIME_SLOT_MAP` 中添加 `'18:30': ['9-10']`
2. 创建 `signin_910.py` wrapper 脚本
3. 创建对应的 cron 任务（18:30 课前提醒 + 18:55 自动签到）

**注意**：9-10节是晚间课程（19:00开始），签到在18:55触发，提醒在18:30触发。

### Q: 周次范围不确定怎么办？
A: 教务系统只显示当前查询周的课表。如果某课程在当前周出现但脚本中没有，推断周次范围（通常从当前周到学期末）。如果某课程在当前周不出现但脚本中有，可能是该周恰好没课，不要轻易删除。**最可靠的方法是逐周读取14-18周，对比每节课在哪些周出现。**

### Q: Cron任务需要改吗？
A: **不需要**。Cron任务按固定时间触发（如8:45），脚本内部根据课表判断是否有课。没有课时脚本输出为空，cron不会发送消息。
