"""
学习通随堂练习自动化脚本
用法: python create_quiz_playwright.py
"""
import time
from playwright.sync_api import sync_playwright

# 配置参数
PHONE = "YOUR_PHONE"
PASSWORD = YOUR_PASSWORD"
ACTIVITY_LIST_URL = "https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000002&classId=100000007&cpi=300000002&enc=YOUR_ENC"
QUIZ_TITLE = "随堂练习"
QUESTION_TEXT = "1. 函数f(x)=x²的导数是？"


def login(page):
    """登录学习通"""
    page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    inputs = page.locator("input[type='text']").all()
    if inputs:
        inputs[0].fill(PHONE)
    time.sleep(1)
    page.locator("input[type='password']").first.fill(PASSWORD)
    time.sleep(1)
    login_btn = page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first
    login_btn.click()
    time.sleep(15)
    return "四川信息职业技术学院" in page.title()


def enter_activity_list(page):
    """进入活动列表"""
    page.goto(ACTIVITY_LIST_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    return "活动列表" in page.title()


def open_add_menu(page):
    """打开添加活动菜单"""
    page.click(".add-activate-icon")
    time.sleep(3)


def click_quiz(page):
    """点击随堂练习"""
    result = page.evaluate("""
        () => {
            const elements = document.querySelectorAll('.btnTest, li.list');
            for (let el of elements) {
                if (el.textContent && el.textContent.includes('随堂练习') && el.offsetParent !== null) {
                    el.click();
                    return 'Clicked!';
                }
            }
            return 'Not found';
        }
    """)
    print(f"点击随堂练习: {result}")
    time.sleep(5)


def fill_question(page, question):
    """填写题目"""
    question_area = page.locator("textarea, div[contenteditable='true'], .question-content").first
    if question_area:
        question_area.fill(question)
        print(f"已填写题目: {question}")
        time.sleep(1)


def click_start(page):
    """点击立即开始"""
    result = page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('a, button, div');
            for (let btn of buttons) {
                if (btn.textContent && btn.textContent.trim() === '立即开始' && btn.offsetParent !== null) {
                    const rect = btn.getBoundingClientRect();
                    return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                }
            }
            return null;
        }
    """)
    if result:
        page.mouse.click(result['x'], result['y'])
        print("已点击立即开始!")
        time.sleep(5)
        return True
    return False


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
        page = context.new_page()
        page.set_default_timeout(30000)

        # 1. 登录
        print("[1] 登录中...")
        if not login(page):
            print("❌ 登录失败!")
            browser.close()
            return
        print("[1] ✅ 登录成功!")

        # 2. 进入活动列表
        print("[2] 进入活动列表...")
        if not enter_activity_list(page):
            print("❌ 进入活动列表失败!")
            browser.close()
            return
        print("[2] ✅ 进入活动列表!")

        # 3. 打开添加活动菜单
        print("[3] 打开添加活动菜单...")
        open_add_menu(page)

        # 4. 点击随堂练习
        print("[4] 点击随堂练习...")
        click_quiz(page)

        # 5. 填写题目
        print("[5] 填写题目...")
        fill_question(page, QUESTION_TEXT)

        # 6. 点击立即开始
        print("[6] 点击立即开始...")
        if click_start(page):
            print("[6] ✅ 随堂练习已启动!")
        else:
            print("[6] ❌ 点击立即开始失败!")

        # 截图
        page.screenshot(path="quiz_result.png")
        print(f"页面标题: {page.title()}")
        print(f"URL: {page.url}")

        time.sleep(30)
        browser.close()


if __name__ == "__main__":
    main()
