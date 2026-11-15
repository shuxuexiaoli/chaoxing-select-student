"""
学习通选人活动完整自动化脚本
从登录到启动选人活动的完整流程

使用方法：
    python select-student-complete.py

依赖：
    pip install playwright
    playwright install chromium
"""

import sys
import time
from playwright.sync_api import sync_playwright


def login_chaoxing(page, phone="YOUR_PHONE", password=YOUR_PASSWORD"):
    """登录学习通
    
    成功标志：页面标题变为"四川信息职业技术学院"
    """
    print("[1] Navigating to login page...")
    page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    
    # 填写手机号（使用 input[type='text'] 更可靠）
    inputs = page.locator("input[type='text']").all()
    if inputs:
        inputs[0].fill(phone)
    time.sleep(1)
    
    # 填写密码
    page.locator("input[type='password']").first.fill(password)
    time.sleep(1)
    
    # 点击登录
    login_btn = page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first
    login_btn.click()
    
    # 等待登录完成（需要15秒左右）
    print("[2] Waiting for login...")
    time.sleep(15)
    
    title = page.title()
    success = "四川信息职业技术学院" in title
    print(f"[2] Page title: {title}, Success: {success}")
    return success


def enter_course(page, course_id, enc, cpi):
    """直接导航到课程页面"""
    course_url = f"https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={course_id}&edit=true&enc={enc}&v=2&cpi={cpi}&baseEducation=0"
    
    print(f"[3] Navigating to course: {course_url}")
    page.goto(course_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    
    title = page.title()
    print(f"[3] Page title: {title}")
    return "高等数学" in title or "经济数学" in title


def enter_activity_list(page, course_id, class_id, cpi, enc, fid=YOUR_FID):
    """直接导航到指定班级的活动列表"""
    activity_url = f"https://mobilelearn.chaoxing.com/page/active/activeList?fid={fid}&courseId={course_id}&classId={class_id}&cpi={cpi}&enc={enc}"
    
    print(f"[4] Navigating to activity list: {activity_url}")
    page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    
    title = page.title()
    print(f"[4] Page title: {title}")
    return "活动列表" in title


def open_add_activity_menu(page):
    """点击添加活动按钮，打开活动类型选择菜单"""
    print("[5] Clicking .add-activate-icon...")
    page.click(".add-activate-icon")
    time.sleep(3)
    print("[5] Menu opened!")


def click_select_student(page):
    """点击选人选项"""
    print("[6] Clicking .btnSelectPerson...")
    page.click(".btnSelectPerson")
    time.sleep(3)
    print("[6] Select student dialog opened!")


def fill_reason_and_start(page, reason="随机选人提问"):
    """填写选人事由并点击立即开始
    
    ⚠️ 重要：页面上有多个"立即开始"按钮，需要找到弹窗中的那个
    """
    # 填写选人事由
    print(f"[7] Filling reason: {reason}")
    input_field = page.locator("input[placeholder*='请输入选人事由'], textarea[placeholder*='请输入选人事由']").first
    if input_field:
        input_field.fill(reason)
        time.sleep(1)
        print("[7] Reason filled!")
    
    # 找到弹窗中的"立即开始"按钮并点击
    print("[8] Finding 立即开始 button in popup...")
    result = page.evaluate("""
        () => {
            const popups = document.querySelectorAll('.popup, .modal, .dialog, div[class*="pop"], div[class*="modal"]');
            for (let popup of popups) {
                if (popup.offsetParent !== null) {
                    const buttons = popup.querySelectorAll('button, a, div');
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
        print(f"[8] Clicked 立即开始 at ({result['x']}, {result['y']})")
    else:
        print("[8] ERROR: Could not find 立即开始 button in popup!")
    
    # 检查是否成功
    title = page.title()
    print(f"[8] Page title: {title}")
    return "选人" in title


def main():
    """主函数：完整的选人活动创建流程"""
    with sync_playwright() as p:
        # 启动浏览器
        print("=== 学习通选人活动自动化 ===\n")
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
        page = context.new_page()
        page.set_default_timeout(30000)
        
        # 课程参数（高等数学（进阶）- 示例考试班）
        COURSE_ID = "200000002"
        CLASS_ID = "100000007"
        CPI = "300000002"
        ENC = "9efe87cda9f0672e3ca7da9d3872007a"
        FID = "3012"
        
        # 1. 登录
        if not login_chaoxing(page):
            print("❌ Login failed!")
            browser.close()
            return
        
        print("✅ Login successful!\n")
        
        # 2. 进入课程
        if not enter_course(page, COURSE_ID, ENC, CPI):
            print("❌ Failed to enter course!")
            browser.close()
            return
        
        print("✅ Entered course!\n")
        
        # 3. 进入活动列表
        if not enter_activity_list(page, COURSE_ID, CLASS_ID, CPI, ENC, FID):
            print("❌ Failed to enter activity list!")
            browser.close()
            return
        
        print("✅ Entered activity list!\n")
        
        # 4. 打开添加活动菜单
        open_add_activity_menu(page)
        
        # 5. 点击选人
        click_select_student(page)
        
        # 6. 填写事由并开始
        if fill_reason_and_start(page, "随机选人提问"):
            print("\n✅ 选人活动已成功启动！")
            print(f"当前页面: {page.title()}")
            print(f"URL: {page.url}")
        else:
            print("\n❌ Failed to start activity!")
        
        # 保持浏览器打开
        print("\n浏览器将保持打开30秒...")
        time.sleep(30)
        
        browser.close()
        print("浏览器已关闭")


if __name__ == "__main__":
    main()
