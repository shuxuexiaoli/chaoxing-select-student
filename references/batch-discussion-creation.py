"""
批量创建主题讨论模板（5班并行）
关键经验（2026-05-31验证）：
- 表单需等15秒加载（不是8秒）
- 用Playwright fill()填写话题（JS el.value 不触发框架数据绑定）
- "立即开始"按钮页面上有10个，需过滤hideMyself class且width>0
- 用mouse.click点击，不用page.click("text=立即开始")
- 点击后URL不变但活动已创建
- 批量并行偶尔1-2个失败需单独重试
"""

import threading
import time
from playwright.sync_api import sync_playwright

# ===== 配置 =====
COURSE_PARAMS = {
    "courseId": "200000001",
    "cpi": "300000001",
    "enc": "YOUR_ENC",
    "fid": "3012"
}

CLASSES = [
    {"name": "示例班级A", "classId": "100000001"},
    {"name": "示例班级B", "classId": "100000002"},
    {"name": "示例班级C", "classId": "100000003"},
    {"name": "示例班级D", "classId": "100000004"},
    {"name": "示例班级E", "classId": "100000005"},
]

TOPIC = "不定积分的实际意义"  # 修改为你的讨论话题
PHONE = "YOUR_PHONE"
PWD = "190253"


def click_start_button(page):
    """点击可见的立即开始按钮（过滤hideMyself且width>0）"""
    btns = page.evaluate("""() => {
        const all = document.querySelectorAll('a');
        const result = [];
        for (let el of all) {
            if ((el.textContent||'').trim() === '立即开始' && !el.className.includes('hideMyself')) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    result.push({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
                }
            }
        }
        return result;
    }""")
    if btns:
        page.mouse.click(btns[-1]['x'], btns[-1]['y'])
        return True
    return False


def create_discussion(class_info, results):
    name = class_info["name"]
    cid = class_info["classId"]
    cp = COURSE_PARAMS

    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="msedge", headless=False)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, locale="zh-CN")
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # 登录
        print(f"  [{name}] 登录...")
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
            results[name] = "登录失败"
            p.stop()
            return

        # 进入活动列表
        print(f"  [{name}] 进入活动列表...")
        page.goto(
            f"https://mobilelearn.chaoxing.com/page/active/activeList"
            f"?fid={cp['fid']}&courseId={cp['courseId']}&classId={cid}&cpi={cp['cpi']}&enc={cp['enc']}",
            wait_until="domcontentloaded", timeout=60000
        )
        time.sleep(5)

        # 添加主题讨论
        print(f"  [{name}] 添加主题讨论...")
        page.click(".add-activate-icon")
        time.sleep(3)
        page.locator(".btnDiscuss").first.click()
        time.sleep(15)  # 关键：必须等15秒

        # 填写话题
        print(f"  [{name}] 填写话题...")
        try:
            page.wait_for_selector("#discussTitle", state="visible", timeout=10000)
            page.locator("#discussTitle").fill(TOPIC)
        except:
            page.evaluate(f"""() => {{
                const el = document.getElementById('discussTitle');
                if (el) {{ el.value = '{TOPIC}'; el.dispatchEvent(new Event('input', {{bubbles:true}})); }}
            }}""")
        time.sleep(2)

        # 点击立即开始
        if click_start_button(page):
            time.sleep(5)
            results[name] = "成功"
            print(f"  [{name}] ✅ 完成")
        else:
            results[name] = "未找到按钮"
            print(f"  [{name}] ❌ 未找到立即开始按钮")

        p.stop()

    except Exception as e:
        print(f"  [{name}] ❌ {e}")
        results[name] = f"错误: {e}"


def main():
    print(f"批量创建主题讨论: {TOPIC}")
    print("=" * 50)

    results = {}
    threads = []
    for cls in CLASSES:
        t = threading.Thread(target=create_discussion, args=(cls, results))
        threads.append(t)
        t.start()
        time.sleep(3)  # 错开启动

    for t in threads:
        t.join()

    print("\n结果:")
    for n, r in results.items():
        print(f"  {'✅' if r == '成功' else '❌'} {n}: {r}")


if __name__ == "__main__":
    main()
