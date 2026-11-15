"""
批量发送主题讨论话题到5个班级（固定模板）
用法：修改 TOPIC 和 CLASSES 后运行

关键点：
1. 使用 force_click_start 而非过滤 width>0（更可靠）
2. 主题讨论表单必须等15秒
3. 每步后调用 close_popups
4. 并行执行，错开3秒启动
"""
import time
import threading
from playwright.sync_api import sync_playwright

# ============ 配置区 ============

TOPIC = "替换为你的讨论话题"

CLASSES = [
    {"name": "示例班级A", "classId": "100000001"},
    {"name": "示例班级B", "classId": "100000002"},
    {"name": "示例班级C", "classId": "100000003"},
    {"name": "示例班级D", "classId": "100000004"},
    {"name": "示例班级E", "classId": "100000005"},
]

COURSE_PARAMS = {
    "courseId": "200000001",
    "cpi": "300000001",
    "enc": "YOUR_ENC",
    "fid": "3012",
}

PHONE = "YOUR_PHONE"
PASSWORD = *** close_popups(page):
    page.evaluate("""() => {
        document.querySelectorAll('.popDiv,.maskDiv,.popBottom,.pick-container,.popPermission,.popMove,.popCellShowHide').forEach(el => el.style.display='none');
    }""")
    time.sleep(1)

def force_click_start(page):
    """强制显示并点击立即开始按钮"""
    result = page.evaluate("""() => {
        for (let el of document.querySelectorAll('a,button,div')) {
            if ((el.textContent||'').trim() === '立即开始') {
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
    return result == 'clicked'

def create_discussion(class_info, results):
    name = class_info["name"]
    cid = class_info["classId"]
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_context(viewport={"width":1280,"height":800}, locale="zh-CN").new_page()
        page.set_default_timeout(30000)

        # 登录
        page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        page.locator("input[type='text']").first.fill(PHONE)
        time.sleep(1)
        page.locator("input[type='password']").first.fill(PASSWORD)
        time.sleep(1)
        page.locator("button[type='submit'],a.submitBtn,.loginBtn,button:has-text('登录'),a:has-text('登录')").first.click()
        time.sleep(15)

        if "四川信息职业技术学院" not in page.title():
            results[name] = "登录失败"
            p.stop()
            return

        # 进入活动列表
        url = f"https://mobilelearn.chaoxing.com/page/active/activeList?fid={COURSE_PARAMS['fid']}&courseId={COURSE_PARAMS['courseId']}&classId={cid}&cpi={COURSE_PARAMS['cpi']}&enc={COURSE_PARAMS['enc']}"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        close_popups(page)

        # 添加活动 -> 主题讨论
        page.click(".add-activate-icon")
        time.sleep(3)
        close_popups(page)
        page.evaluate("() => { const b=document.querySelector('li.btnDiscuss'); if(b) b.click(); }")
        time.sleep(15)  # 必须等15秒
        close_popups(page)

        # 填写话题
        try:
            page.wait_for_selector("#discussTitle", state="visible", timeout=10000)
            page.locator("#discussTitle").fill(TOPIC)
        except:
            page.evaluate('() => { const el=document.getElementById("discussTitle"); if(el){el.value="' + TOPIC + '";el.dispatchEvent(new Event("input",{bubbles:true}));} }')
        time.sleep(2)
        close_popups(page)

        # 点击立即开始
        if force_click_start(page):
            time.sleep(5)
            results[name] = "成功"
        else:
            results[name] = "未找到按钮"
        p.stop()
    except Exception as e:
        results[name] = f"错误: {e}"

def main():
    print(f"话题: {TOPIC}")
    results = {}
    threads = []
    for cls in CLASSES:
        t = threading.Thread(target=create_discussion, args=(cls, results))
        threads.append(t)
    for t in threads:
        t.start()
        time.sleep(3)
    for t in threads:
        t.join()
    print("\n=== 结果 ===")
    for n, r in results.items():
        print(f"  {'✅' if r=='成功' else '❌'} {n}: {r}")
    print(f"成功: {sum(1 for r in results.values() if r=='成功')}/{len(CLASSES)}")

if __name__ == "__main__":
    main()
