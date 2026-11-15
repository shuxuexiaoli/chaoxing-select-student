# 批量主题讨论自动发送方案（带进度跟踪）

## 方案概述
- 每天自动发送1个主题讨论到5个班级
- 共26个话题，26天完成
- 使用cron定时任务（每天8:00）
- 进度保存在JSON文件中，支持断点续传

## 文件结构
```
~/.hermes/scripts/auto_discussion.py     # 主脚本（cron调用）
D:\BaiduSyncdisk\龙虾文件\scripts\auto_discussion.py  # 备份脚本
D:\BaiduSyncdisk\龙虾文件\教学资料\discussion_progress.json  # 进度文件
D:\BaiduSyncdisk\龙虾文件\教学资料\主题讨论题目.md  # 话题列表
```

## 进度跟踪JSON格式
```json
{
  "current_index": 0,
  "completed": [
    {
      "index": 0,
      "results": {
        "示例班级A": "成功",
        "示例班级B": "成功",
        "示例班级C": "成功",
        "示例班级D": "成功",
        "示例班级E": "成功"
      }
    }
  ]
}
```

## 脚本关键代码

### 弹窗关闭函数（必须在点击"立即开始"前调用）
```python
def close_popups(page):
    """关闭所有弹窗（权限设置、通讯录等）"""
    page.evaluate("""() => {
        const popups = document.querySelectorAll('.popDiv, .maskDiv, .popBottom, .pick-container');
        for (let el of popups) {
            el.style.display = 'none';
        }
        const cancelBtns = document.querySelectorAll('a, button, div');
        for (let el of cancelBtns) {
            if ((el.textContent||'').trim() === '取消') {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0) { el.click(); }
            }
        }
    }""")
    time.sleep(1)
```

### 点击"立即开始"按钮（强制显示+JS点击）
```python
def click_start_button(page):
    """强制显示并点击立即开始按钮"""
    close_popups(page)
    
    result = page.evaluate("""() => {
        const all = document.querySelectorAll('a, button, div');
        for (let el of all) {
            if ((el.textContent||'').trim() === '立即开始') {
                el.style.display = 'block';
                el.style.visibility = 'visible';
                el.style.width = 'auto';
                el.style.height = 'auto';
                el.style.opacity = '1';
                el.click();
                return 'clicked';
            }
        }
        return 'not found';
    }""")
    
    if result == 'clicked':
        time.sleep(3)
        # 检查确认弹窗
        page.evaluate("""() => {
            const all = document.querySelectorAll('a, button, div');
            for (let el of all) {
                const text = (el.textContent||'').trim();
                if (text === '确定' || text === '确认') {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0) { el.click(); return; }
                }
            }
        }""")
        return True
    return False
```

### 创建主题讨论完整流程
```python
def create_discussion(page, topic):
    """创建单个主题讨论"""
    # 1. 进入活动列表
    page.goto(activity_list_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    
    # 2. 关闭弹窗
    close_popups(page)
    
    # 3. 点击添加活动
    page.click(".add-activate-icon")
    time.sleep(3)
    close_popups(page)
    
    # 4. 点击主题讨论
    page.evaluate("""() => {
        const els = document.querySelectorAll('.btnDiscuss, li.list');
        for (let el of els) {
            if (el.textContent && el.textContent.includes('主题讨论') && el.offsetParent !== null) {
                el.click(); return;
            }
        }
    }""")
    time.sleep(8)
    close_popups(page)
    
    # 5. 填写话题
    try:
        page.wait_for_selector("#discussTitle", state="visible", timeout=15000)
        page.locator("#discussTitle").fill(topic)
    except:
        page.evaluate(f"""() => {{
            const el = document.getElementById('discussTitle');
            if (el) {{ el.value = {json.dumps(topic)}; el.dispatchEvent(new Event('input', {{bubbles:true}})); }}
        }}""")
    time.sleep(2)
    
    # 6. 点击立即开始
    return click_start_button(page)
```

## Cron任务设置
```python
cronjob(
    action='create',
    name='经济数学主题讨论自动发送',
    schedule='0 8 * * *',  # 每天早上8:00
    prompt='运行经济数学主题讨论自动发送脚本，为5个班级发送1个主题讨论...',
    script='auto_discussion.py',
    deliver='weixin:o9cq80925DA-gRppBzmVoEEhKEEs@im.wechat'
)
```

## 重试单个班级
如果某个班级发送失败，可以单独重试：
```python
# 创建单独重试脚本
def resend_single_class(class_info, topic):
    p = sync_playwright().start()
    browser = p.chromium.launch(channel="msedge", headless=False)  # 非headless便于调试
    # ... 登录、导航、创建讨论 ...
    # 使用 close_popups() + click_start_button() 
    p.stop()
```

## 关键Pitfalls
1. **弹窗遮挡**：页面上可能有权限设置弹窗、通讯录弹窗等覆盖按钮，必须先调用 `close_popups()`
2. **强制显示**：被遮挡的按钮 `width=0`，需要用JS强制设置 `display/visibility/width/height/opacity`
3. **JS点击**：用 `el.click()` 而不是 `mouse.click`，因为按钮可能被遮挡
4. **确认弹窗**：点击"立即开始"后可能弹出确认框，需要检查并点击"确定"
5. **话题格式**：用户偏好一句话精简版，与学生生活相关
