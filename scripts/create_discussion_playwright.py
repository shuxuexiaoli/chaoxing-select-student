"""
学习通主题讨论活动创建脚本（Playwright版）
用法：python create_discussion_playwright.py

关键经验（2026-06-08验证）：
- 每个步骤后必须调用close_popups()关闭弹窗，否则后续操作被阻塞
- 点击.btnDiscuss后必须等15秒，表单才能完全渲染
- 讨论话题输入框是 textarea#discussTitle，不是input
- "立即开始"按钮需强制显示（el.style.display='block'）再点击
- 点击后URL不变，弹窗关闭，活动出现在列表中即表示成功
"""
import time
from playwright.sync_api import sync_playwright

TOPIC = "不定积分的实际意义"
PHONE = "YOUR_PHONE"
PWD=*** close_popups(page):
    """关闭所有弹窗 — 每个步骤后必须调用（2026-06-08验证）"""
    page.evaluate("""() => {
        document.querySelectorAll('.popDiv,.maskDiv,.popBottom,.pick-container,.popPermission,.popMove,.popCellShowHide').forEach(el => el.style.display='none');
    }""")
    time.sleep(1)


def login(page):
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


def create_discussion(page, class_id, course_id, cpi, enc, fid, topic):
    """为一个班级创建主题讨论并立即开始"""
    # 进入活动列表
    url = (
        f"https://mobilelearn.chaoxing.com/page/active/activeList"
        f"?fid={fid}&courseId={course_id}&classId={class_id}&cpi={cpi}&enc={enc}"
    )
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    close_popups(page)

    # 添加活动
    page.click(".add-activate-icon")
    time.sleep(3)
    close_popups(page)

    # 点击主题讨论（精确选择器，避免误点已有活动）
    page.evaluate("() => { const b=document.querySelector('li.btnDiscuss'); if(b) b.click(); }")
    time.sleep(15)  # 关键：必须等15秒让表单渲染
    close_popups(page)

    # 填写话题（textarea#discussTitle）
    try:
        page.wait_for_selector("#discussTitle", state="visible", timeout=10000)
        page.locator("#discussTitle").fill(topic)
    except:
        # 备选：JS直接赋值
        page.evaluate(f"""() => {{
            const el = document.getElementById('discussTitle');
            if (el) {{ el.value = "{topic}"; el.dispatchEvent(new Event('input', {{bubbles:true}})); }}
        }}""")
    time.sleep(2)
    close_popups(page)

    # 点击"立即开始"（强制显示+点击，2026-06-08验证最可靠）
    result = page.evaluate("""() => {
        for (let el of document.querySelectorAll('a,button,div')) {
            if ((el.textContent||'').trim()==='立即开始') {
                el.style.display='block';
                el.style.visibility='visible';
                el.style.width='auto';
                el.style.height='auto';
                el.style.opacity='1';
                el.click();
                return 'clicked';
            }
        }
        return 'not found';
    }""")
    if result == 'clicked':
        time.sleep(5)
        return True
    return False


def main():
    # 经济数学课程参数
    COURSE_ID = "200000001"
    CPI = "300000001"
    ENC = "YOUR_ENC"
    FID = "3012"
    CLASSES = [
        {"name": "示例班级A", "classId": "100000001"},
        {"name": "示例班级B", "classId": "100000002"},
        {"name": "示例班级C", "classId": "100000003"},
        {"name": "示例班级D", "classId": "100000004"},
        {"name": "示例班级E", "classId": "100000005"},
    ]

    p = sync_playwright().start()
    browser = p.chromium.launch(channel="msedge", headless=False)
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, locale="zh-CN")
    page = ctx.new_page()
    page.set_default_timeout(30000)

    login(page)

    for cls in CLASSES:
        name = cls["name"]
        print(f"[{name}] 创建主题讨论: {TOPIC}")
        ok = create_discussion(page, cls["classId"], COURSE_ID, CPI, ENC, FID, TOPIC)
        print(f"[{name}] {'✅ 成功' if ok else '❌ 失败'}")

    # 不关闭浏览器
    print("全部完成")


if __name__ == "__main__":
    main()
