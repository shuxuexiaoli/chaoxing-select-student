"""
学习通完整Playwright自动化脚本
包含：登录 → 进入课程 → 进入班级活动 → 进入活动列表
已验证可用的完整流程
"""
import time
from playwright.sync_api import sync_playwright

def login_chaoxing(page, phone="YOUR_PHONE", password=YOUR_PASSWORD"):
    """登录学习通"""
    page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    
    # 填写手机号 - 使用input[type='text']更可靠
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
    
    # 等待登录完成（需要较长时间）
    time.sleep(15)
    
    return "四川信息职业技术学院" in page.title()

def enter_course(page, course_id, enc, cpi):
    """进入指定课程"""
    course_url = f"https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={course_id}&edit=true&enc={enc}&v=2&cpi={cpi}&baseEducation=0"
    page.goto(course_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    return "高等数学" in page.title() or "经济数学" in page.title()

def enter_class_activity(page):
    """进入班级活动页面"""
    page.click("text=班级活动")
    time.sleep(5)

def enter_activity_list(page, course_id, class_id, cpi, enc, fid=YOUR_FID):
    """直接进入指定班级的活动列表"""
    activity_url = f"https://mobilelearn.chaoxing.com/page/active/activeList?fid={fid}&courseId={course_id}&classId={class_id}&cpi={cpi}&enc={enc}"
    page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    return "活动列表" in page.title()

def find_course_url_in_iframe(page, course_name):
    """在iframe中查找课程URL"""
    page.click("text=课程")
    time.sleep(5)
    
    for frame in page.frames:
        try:
            content = frame.content()
            if course_name in content:
                result = frame.evaluate(f"""
                    () => {{
                        const links = document.querySelectorAll('a');
                        for (let link of links) {{
                            if (link.textContent && link.textContent.includes('{course_name}')) {{
                                return link.href;
                            }}
                        }}
                        return null;
                    }}
                """)
                if result:
                    return result
        except:
            pass
    return None

# 使用示例
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
        page = context.new_page()
        page.set_default_timeout(30000)
        
        # 登录
        if login_chaoxing(page):
            print("✅ 登录成功")
            
            # 进入高等数学（进阶）
            if enter_course(page, "200000002", "13c0bfec572bb3435c1d29bbd19487e5", "300000002"):
                print("✅ 进入课程成功")
                
                # 进入示例考试班活动列表
                if enter_activity_list(page, "200000002", "100000007", "300000002", "9efe87cda9f0672e3ca7da9d3872007a"):
                    print("✅ 进入活动列表成功")
                    page.screenshot(path="activity_list.png")
        
        time.sleep(30)
        browser.close()
