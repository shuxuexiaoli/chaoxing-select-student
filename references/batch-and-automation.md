# 批量操作与自动签到

## 批量创建主题讨论（5班级并行）

关键经验（2026-05-31 验证）：

1. 并行执行：每个线程独立 Playwright 实例，错开 3 秒启动
2. 表单等待：主题讨论表单需 10-15 秒加载（`#discussTitle` 从 hidden 变 visible）
3. 按钮点击：用 `page.evaluate` 获取按钮坐标 → `page.mouse.click(x, y)`
4. 成功判断：URL 不变 ≠ 失败，需重新加载列表验证

```python
# 批量模式模板
import threading
from playwright.sync_api import sync_playwright

CLASSES = [
    {"name": "示例班级A", "classId": "100000001"},
    {"name": "示例班级B", "classId": "100000002"},
    # ...
]

def create_for_class(class_info, results):
    name = class_info["name"]
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="msedge", headless=False)
        # ... 登录 → 进入活动列表 → 添加活动 → 填写 → 点击立即开始
        results[name] = "成功"
        p.stop()
    except Exception as e:
        results[name] = f"错误: {e}"

results = {}
threads = []
for cls in CLASSES:
    t = threading.Thread(target=create_for_class, args=(cls, results))
    threads.append(t)
    t.start()
    time.sleep(3)  # 错开启动

for t in threads:
    t.join()
```

## 自动签到（cron + no_agent）

脚本模式：`no_agent=True` + `script` 字段直接运行 Python 脚本。

结构：
- `auto_signin.py`：主脚本，接受命令行参数 `JIE`（节次如 "1-2"）
- `signin_12.py` 等包装脚本：`subprocess.run([sys.executable, "auto_signin.py", "1-2"])`
- 4 个 cron job 分别在上课前 5 分钟触发

课表数据格式：
```python
SCHEDULE = [
    (weekday, jie, classId, className, week_range),
    # weekday: 0=周一, jie: '1-2'/'3-4'/'5-6'/'7-8'
]
```

签到流程：登录 → 导航到活动列表 → `.add-activate-icon` → `.btnSignIn` → 填标题 → 点立即开始

**headless 模式**：cron 任务使用 `headless=True`（无头浏览器），不需要显示窗口。

## 课表时间（2026-05-31 更新）

- 第1-2节：8:50-10:20
- 第3-4节：10:30-12:00
- 第5-6节：14:00-15:30
- 第7-8节：15:50-17:20

课前提醒：每节课前 10 分钟
自动签到：每节课前 5 分钟
