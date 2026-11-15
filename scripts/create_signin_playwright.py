"""
学习通签到活动创建脚本（Playwright版）
用法：python create_signin_playwright.py
"""
import time
from playwright.sync_api import sync_playwright

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
    time.sleep(15)
    return "四川信息职业技术学院" in page.title()

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

def click_signin(page):
    """点击签到选项"""
    # 方法1：使用CSS选择器
    try:
        page.click(".btnSignIn")
        time.sleep(3)
        return True
    except:
        pass
    
    # 方法2：使用JavaScript查找可见的签到选项
    result = page.evaluate("""
        () => {
            const elements = document.querySelectorAll('.btnSignIn, li.list');
            for (let el of elements) {
                if (el.textContent && el.textContent.includes('签到') && el.offsetParent !== null) {
                    el.click();
                    return true;
                }
            }
            return false;
        }
    """)
    time.sleep(3)
    return result

def fill_title_and_start(page, title="课堂签到"):
    """填写签到标题并点击立即开始"""
    # 填写标题
    try:
        input_field = page.locator("input[placeholder*='请输入标题'], input[placeholder*='标题']").first
        if input_field:
            input_field.fill(title)
            time.sleep(1)
    except:
        pass
    
    # 点击立即开始（在弹窗中）
    result = page.evaluate("""
        () => {
            const popups = document.querySelectorAll('.popup, .modal, .dialog, div[class*="pop"], div[class*="modal"]');
            for (let popup of popups) {
                if (popup.offsetParent !== null) {
                    const buttons = popup.querySelectorAll('a, button, div');
                    for (let btn of buttons) {
                        if (btn.textContent && btn.textContent.trim() === '立即开始') {
                            const rect = btn.getBoundingClientRect();
                            return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                        }
                    }
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

def main():
    # 配置参数
    PHONE = "YOUR_PHONE"
    PASSWORD = YOUR_PASSWORD"
    COURSE_ID = "200000002"  # 高等数学（进阶）
    CLASS_ID = "100000007"   # 示例考试班
    CPI = "300000002"
    ENC = "9efe87cda9f0672e3ca7da9d3872007a"
    FID = "3012"
    SIGNIN_TITLE = "课堂签到"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
        page = context.new_page()
        page.set_default_timeout(30000)
        
        try:
            # 1. 登录
            print("[1] 登录学习通...")
            if not login_chaoxing(page, PHONE, PASSWORD):
                print("❌ 登录失败！")
                return
            print("✅ 登录成功！")
            
            # 2. 进入活动列表
            print("[2] 进入示例考试班活动列表...")
            if not enter_activity_list(page, COURSE_ID, CLASS_ID, CPI, ENC, FID):
                print("❌ 进入活动列表失败！")
                return
            print("✅ 进入活动列表成功！")
            
            # 3. 打开添加活动菜单
            print("[3] 打开添加活动菜单...")
            open_add_activity_menu(page)
            print("✅ 菜单已打开！")
            
            # 4. 点击签到
            print("[4] 选择签到活动...")
            if not click_signin(page):
                print("❌ 点击签到失败！")
                return
            print("✅ 已选择签到！")
            
            # 5. 填写标题并开始
            print(f"[5] 填写标题'{SIGNIN_TITLE}'并开始签到...")
            if not fill_title_and_start(page, SIGNIN_TITLE):
                print("❌ 开始签到失败！")
                return
            print("✅ 签到活动已开始！")
            
            # 6. 显示结果
            print(f"\n📊 页面标题: {page.title()}")
            print(f"📊 页面URL: {page.url}")
            
            # 保持浏览器打开
            print("\n⏳ 签到活动进行中，保持浏览器打开60秒...")
            time.sleep(60)
            
        finally:
            browser.close()
            print("浏览器已关闭")

if __name__ == "__main__":
    main()
