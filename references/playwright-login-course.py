"""
学习通 Playwright 自动化登录 + 进入课程脚本
适用于四川信息职业技术学院 - 李盘润账号

使用方法:
1. 确保已安装 playwright: pip install playwright
2. 确保已安装浏览器: playwright install chromium
3. 运行脚本: python playwright-login-course.py

注意事项:
- 登录页面没有隐私政策复选框
- 登录后需要等待15秒
- 课程列表在iframe中，需要特殊处理
"""

import time
from playwright.sync_api import sync_playwright

# 配置信息
PHONE = "YOUR_PHONE"
PASSWORD = YOUR_PASSWORD"  # 替换为实际密码
TARGET_COURSE = "高等数学（进阶）"  # 或 "经济数学"

def login_and_enter_course():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN"
        )
        page = context.new_page()
        page.set_default_timeout(30000)

        # 登录
        print("[1] 导航到登录页面...")
        page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        print("[2] 填写手机号...")
        inputs = page.locator("input[type='text']").all()
        if inputs:
            inputs[0].fill(PHONE)
        time.sleep(1)

        print("[3] 填写密码...")
        page.locator("input[type='password']").first.fill(PASSWORD)
        time.sleep(1)

        print("[4] 点击登录...")
        login_btn = page.locator(
            "button[type='submit'], a.submitBtn, .loginBtn, "
            "button:has-text('登录'), a:has-text('登录')"
        ).first
        login_btn.click()

        print("[5] 等待登录完成...")
        time.sleep(15)

        title = page.title()
        print(f"[5] 页面标题: {title}")

        if "四川信息职业技术学院" not in title:
            print("❌ 登录失败!")
            browser.close()
            return

        print("[6] 登录成功!")

        # 点击课程菜单
        print("[7] 点击'课程'菜单...")
        page.click("text=课程")
        time.sleep(5)

        # 在iframe中查找课程
        print("[8] 查找课程iframe...")
        course_frame = None
        for frame in page.frames:
            try:
                content = frame.content()
                if TARGET_COURSE in content:
                    course_frame = frame
                    print(f"[8] 找到课程iframe: {frame.url[:80]}...")
                    break
            except:
                pass

        if not course_frame:
            print("[8] ❌ 未找到课程iframe!")
            browser.close()
            return

        # 提取课程URL
        print("[9] 提取课程URL...")
        course_url = course_frame.evaluate("""
            (courseName) => {
                const links = document.querySelectorAll('a');
                for (let link of links) {
                    if (link.textContent && link.textContent.includes(courseName)) {
                        return link.href;
                    }
                }
                return null;
            }
        """, TARGET_COURSE)

        if course_url:
            print(f"[9] 课程URL: {course_url}")
            
            # 直接导航到课程
            print("[10] 导航到课程页面...")
            page.goto(course_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

            title = page.title()
            print(f"[10] 页面标题: {title}")

            if TARGET_COURSE in title:
                print("[11] ✅ 成功进入课程!")
            else:
                print("[11] ❌ 未能进入课程")
        else:
            print("[9] ❌ 未找到课程URL")

        # 保持浏览器打开
        print("\n[12] 浏览器保持打开30秒...")
        time.sleep(30)

        browser.close()
        print("[13] 浏览器已关闭")

if __name__ == "__main__":
    login_and_enter_course()
