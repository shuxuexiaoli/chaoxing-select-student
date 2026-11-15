"""
学习通抢答活动创建脚本（Playwright版）
使用方法：直接运行此脚本，或导入其中的函数使用
"""
from playwright.sync_api import sync_playwright
import time


def login_chaoxing(page, phone="YOUR_PHONE", password=YOUR_PASSWORD"):
    """登录学习通，成功标志：页面标题变为"四川信息职业技术学院" """
    page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    inputs = page.locator("input[type='text']").all()
    if inputs:
        inputs[0].fill(phone)
    time.sleep(1)
    page.locator("input[type='password']").first.fill(password)
    time.sleep(1)
    login_btn = page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first
    login_btn.click()
    time.sleep(15)  # 等待登录完成
    return "四川信息职业技术学院" in page.title()


def enter_course(page, course_id, enc, cpi):
    """直接导航到课程页面"""
    course_url = f"https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={course_id}&edit=true&enc={enc}&v=2&cpi={cpi}&baseEducation=0"
    page.goto(course_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    return "高等数学" in page.title() or "经济数学" in page.title()


def enter_activity_list(page, course_id, class_id, cpi, enc, fid=YOUR_FID):
    """直接导航到指定班级的活动列表"""
    activity_url = f"https://mobilelearn.chaoxing.com/page/active/activeList?fid={fid}&courseId={course_id}&classId={class_id}&cpi={cpi}&enc={enc}"
    page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    return "活动列表" in page.title()


def open_add_activity_menu(page):
    """点击添加活动按钮打开菜单"""
    page.click(".add-activate-icon")
    time.sleep(3)


def click_quick_answer(page):
    """点击抢答选项"""
    result = page.evaluate("""
        () => {
            const elements = document.querySelectorAll('.btnQuickAnswer, li.list');
            for (let el of elements) {
                if (el.textContent && el.textContent.includes('抢答') && el.offsetParent !== null) {
                    el.click();
                    return 'Clicked!';
                }
            }
            return 'Not found';
        }
    """)
    time.sleep(3)
    return "Clicked" in result


def fill_content_and_start(page, content="请抢答"):
    """填写抢答内容并点击立即开始"""
    # 填写抢答内容
    input_field = page.locator("input[placeholder*='请输入抢答内容'], textarea[placeholder*='请输入抢答内容']").first
    if input_field:
        input_field.fill(content)
        time.sleep(1)
    
    # 点击立即开始按钮（在弹窗中查找）
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
        time.sleep(5)
        return True
    return False


def create_quick_answer(page, content="请抢答"):
    """完整流程：打开菜单 -> 点击抢答 -> 填写内容 -> 开始活动"""
    open_add_activity_menu(page)
    if click_quick_answer(page):
        return fill_content_and_start(page, content)
    return False


# 使用示例
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
        page = context.new_page()
        page.set_default_timeout(30000)
        
        if login_chaoxing(page):
            if enter_course(page, "200000002", "13c0bfec572bb3435c1d29bbd19487e5", "300000002"):
                if enter_activity_list(page, "200000002", "100000007", "300000002", "9efe87cda9f0672e3ca7da9d3872007a"):
                    if create_quick_answer(page, "请抢答：什么是导数？"):
                        print("抢答活动已成功创建并启动！")
                        time.sleep(30)  # 保持浏览器打开30秒
        
        browser.close()
