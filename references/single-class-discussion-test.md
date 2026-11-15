# 单班级测试脚本模板

测试某个班级的主题讨论发送时，创建一个简化版脚本（只针对1个班级），而不是运行完整的5班批量脚本。

## 使用场景
- 新课程/新班级首次测试
- 调试特定班级的发送问题
- 验证课程参数是否正确

## 模板结构

```python
"""
单班级主题讨论测试脚本
"""
import time
import json
from playwright.sync_api import sync_playwright

# 课程参数（根据目标课程修改）
COURSE_PARAMS = {
    "courseId": "200000002",      # 高等数学进阶
    "cpi": "300000002",
    "enc": "YOUR_ENC",
    "fid": "3012"
}

# 目标班级（只填1个）
CLASS = {"name": "示例考试班", "classId": "100000007"}

# 登录信息
PHONE = "YOUR_PHONE"
PWD = "190253"

# 测试话题
TOPIC = "测试主题讨论：你每天花多少时间在数学上？请分享你的学习方法。"


def main():
    name = CLASS["name"]
    cid = CLASS["classId"]
    cp = COURSE_PARAMS

    print(f"{'='*60}")
    print(f"测试班级：{name}")
    print(f"话题：{TOPIC}")
    print(f"{'='*60}\n")

    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # 登录
        print(f"[{name}] 登录...")
        page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        inputs = page.locator("input[type='text']").all()
        if inputs:
            inputs[0].fill(PHONE)
        time.sleep(1)
        page.locator("input[type='password']").first.fill(PWD)
        time.sleep(1)
        page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first.click()
        time.sleep(15)

        if "四川信息职业技术学院" not in page.title():
            print(f"[{name}] ❌ 登录失败")
            p.stop()
            return

        # 进入活动列表
        print(f"[{name}] 进入活动列表...")
        page.goto(
            f"https://mobilelearn.chaoxing.com/page/active/activeList"
            f"?fid={cp['fid']}&courseId={cp['courseId']}&classId={cid}&cpi={cp['cpi']}&enc={cp['enc']}",
            wait_until="domcontentloaded", timeout=60000
        )
        time.sleep(5)

        # 添加主题讨论
        print(f"[{name}] 添加主题讨论...")
        page.click(".add-activate-icon")
        time.sleep(3)
        page.evaluate("""() => {
            const els = document.querySelectorAll('.btnDiscuss, li.list');
            for (let el of els) {
                if (el.textContent && el.textContent.includes('主题讨论') && el.offsetParent !== null) {
                    el.click(); return;
                }
            }
        }""")
        time.sleep(8)

        # 填写话题
        print(f"[{name}] 填写话题...")
        try:
            page.wait_for_selector("#discussTitle", state="visible", timeout=15000)
            page.locator("#discussTitle").fill(TOPIC)
        except:
            page.evaluate(f"""() => {{
                const el = document.getElementById('discussTitle');
                if (el) {{ el.value = {json.dumps(TOPIC)}; el.dispatchEvent(new Event('input', {{bubbles:true}})); }}
            }}""")
        time.sleep(2)

        # 关闭弹窗
        page.evaluate("""() => {
            const popups = document.querySelectorAll('.popDiv, .maskDiv, .popBottom, .pick-container');
            for (let el of popups) { el.style.display = 'none'; }
        }""")
        time.sleep(1)

        # 点击立即开始
        print(f"[{name}] 点击立即开始...")
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
            print(f"[{name}] ✅ 点击成功")
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
            time.sleep(3)
            print(f"[{name}] ✅ 测试完成！")
        else:
            print(f"[{name}] ❌ 未找到立即开始按钮")

        p.stop()

    except Exception as e:
        print(f"[{name}] ❌ 错误: {e}")


if __name__ == "__main__":
    main()
```

## 关键点
- `headless=True` 用于测试（不需要看浏览器）
- 使用 `json.dumps(topic)` 处理中文话题内容
- 关闭弹窗后再点击"立即开始"
- 结果发送到微信（通过cron deliver参数）
