# 学习通作业（Homework）创建指南

## 重要：作业不在移动端活动列表中

学习通移动端（mobilelearn.chaoxing.com）的"添加活动"菜单中**没有"作业"选项**。
作业功能**只能通过PC端学习通**的课程管理页面访问。

## 作业页面访问流程

### 方式1：通过课程页面点击"作业"标签（推荐）

```
登录 → 我的课程 → 点击课程卡片（在iframe中） → 点击"作业"标签
```

**关键URL：**
```
课程页面: https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={courseId}&edit=true&enc={enc}
作业页面: https://mooc1-1.chaoxing.com/mooc-ans/work/getAllWork?classId={classId}&courseId={courseId}&isdisplaytable=2&mooc=1&ut=t&enc={enc}&cpi={cpi}&openc={openc}
```

### 方式2：直接导航（需先建立session）

**⚠️ 必须先进入课程页面建立session，否则直接访问作业URL会报"无权限"。**

```python
# 1. 先进入课程页面（建立session）
page.goto(f"https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={courseId}&edit=true&enc={enc}",
          wait_until="domcontentloaded", timeout=60000)
time.sleep(8)

# 2. 然后点击"作业"标签
page.evaluate("""() => {
    const links = document.querySelectorAll('a');
    for (const a of links) {
        if (a.textContent.trim() === '作业') {
            a.click(); return 'clicked';
        }
    }
    return 'not found';
}""")
time.sleep(8)
```

## 作业管理页面

作业管理页面显示：
- **顶部导航**：首页、活动、统计、资料、通知、**作业**、考试、讨论、管理
- **操作按钮**：新建作业、建文件夹、作业库
- **班级选择**：可切换班级（如示例考试班）
- **视图切换**：列表视图
- **回收站**

## 创建新作业

点击"新建作业"按钮（调用 `toCreateWork()` JavaScript函数）进入作业编辑页面。

### 作业编辑页面功能

**标题区：**
- 标题输入框（默认"新建作业{timestamp}"）
- "设置"按钮（配置发布时间、截止时间、作答规则等）
- "预览"按钮
- "保存并返回"按钮

**题目区：**
- 题型按钮：单选题、多选题、填空题、判断题、简答题、更多>
- 题库选题（从平台题库挑选）
- 智能导入（导入已有题目）

**统计栏：**
- 题量（实时更新）
- 总分（默认100分）

### 创建作业的Playwright流程

```python
# 1. 进入课程页面
page.goto(f"https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={courseId}&edit=true&enc={enc}",
          wait_until="domcontentloaded", timeout=60000)
time.sleep(8)

# 2. 点击"作业"标签
page.evaluate("""() => {
    const links = document.querySelectorAll('a');
    for (const a of links) {
        if (a.textContent.trim() === '作业') { a.click(); return; }
    }
}""")
time.sleep(8)

# 3. 点击"新建作业"
page.evaluate("toCreateWork()")
time.sleep(8)

# 4. 修改标题
page.locator("input[name='title'], input[placeholder*='标题']").first.fill("测试作业")

# 5. 添加题目（点击题型按钮）
# 例如点击"单选题"
page.evaluate("""() => {
    const btns = document.querySelectorAll('a, span, div');
    for (const b of btns) {
        if (b.textContent.trim() === '单选题') { b.click(); return; }
    }
}""")
time.sleep(3)

# 6. 填写题目内容、选项、答案...

# 7. 设置发布时间等
page.evaluate("""() => {
    const btns = document.querySelectorAll('a, span, div');
    for (const b of btns) {
        if (b.textContent.trim() === '设置') { b.click(); return; }
    }
}""")
time.sleep(3)

# 8. 保存
page.evaluate("""() => {
    const btns = document.querySelectorAll('a, span, div');
    for (const b of btns) {
        if (b.textContent.trim() === '保存并返回') { b.click(); return; }
    }
}""")
time.sleep(5)
```

## 已知课程的作业URL

### 高等数学（进阶）- 示例考试班
```
课程页面: https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId=200000002&edit=true&enc=YOUR_ENC
作业页面: https://mooc1-1.chaoxing.com/mooc-ans/work/getAllWork?classId=100000007&courseId=200000002&isdisplaytable=2&mooc=1&ut=t&enc=YOUR_ENC&cpi=300000002&openc=YOUR_ENC
```

## Pitfalls

### Pitfall HW1: 直接访问作业URL会报"无权限"
必须先通过课程页面建立session，再访问作业页面。不能直接goto作业URL。

### Pitfall HW2: 课程卡片在iframe中
课程列表在 `mooc1-1.chaoxing.com/visit/courses` iframe中。点击课程卡片需要用 `frame.evaluate()` 或直接提取链接URL导航。

### Pitfall HW3: 作业页面的"新建作业"按钮
"新建作业"按钮的onclick是 `toCreateWork()`，不是普通的链接。需要用 `page.evaluate("toCreateWork()")` 调用。

### Pitfall HW4: 用户可能用非标准代码称呼班级
用户说"72024949是班级的代码"，但实际classId是100000007。需要通过API确认真实classId：
```python
result = page.evaluate("""async () => {
    const resp = await fetch('/v2/apis/class/getClassList?courseId=200000002&isHaveAuth=1&isfiled=');
    const data = await resp.json();
    return data.data.map(c => ({id: c.id, name: c.name, enc: c.classEnc}));
}""")
```
