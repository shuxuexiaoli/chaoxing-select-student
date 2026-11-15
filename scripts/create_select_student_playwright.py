"""
学习通创建选人活动 - Playwright自动化脚本
使用方法：直接运行或导入使用

正确的CSS选择器：
  - 添加活动按钮: .add-activate-icon
  - 选人选项: .btnSelectPerson (不是 .title-name)
"""

import time
from playwright.sync_api import sync_playwright


def create_select_student_activity(page, reason="", count=1, duration_minutes=5):
    """
    在活动列表页面创建选人活动
    
    Args:
        page: Playwright page对象
        reason: 选人事由
        count: 每次选人数量
        duration_minutes: 活动时长（分钟）
    
    Returns:
        bool: 是否成功打开选人配置页面
    """
    # 点击 .add-activate-icon 打开活动类型菜单
    print("[1] 点击添加活动按钮...")
    try:
        page.click(".add-activate-icon")
        print("[1] 已点击 .add-activate-icon!")
        time.sleep(3)
    except Exception as e:
        print(f"[1] 点击失败: {e}")
        return False
    
    # 点击 .btnSelectPerson 选择选人活动
    print("[2] 选择选人活动...")
    try:
        page.click(".btnSelectPerson")
        print("[2] 已点击 .btnSelectPerson!")
        time.sleep(3)
    except Exception as e:
        print(f"[2] 点击失败: {e}")
        return False
    
    # 检查是否进入选人配置页面
    print("[3] 检查选人配置页面...")
    try:
        # 查找"请输入选人事由"输入框
        reason_input = page.locator("input[placeholder*='选人事由'], textarea[placeholder*='选人事由']").first
        if reason_input:
            print("[3] 已进入选人配置页面!")
            
            # 填写事由
            if reason:
                reason_input.fill(reason)
                print(f"[3] 已填写事由: {reason}")
            
            return True
    except Exception as e:
        print(f"[3] 检查失败: {e}")
    
    return False


# 使用示例
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
        page = context.new_page()
        page.set_default_timeout(30000)
        
        # 假设已经登录并进入活动列表页面
        # 活动列表URL示例:
        # https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000002&classId=100000007&cpi=300000002&enc=YOUR_ENC
        
        activity_url = "https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000002&classId=100000007&cpi=300000002&enc=YOUR_ENC"
        page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        
        # 创建选人活动
        if create_select_student_activity(page, reason="课堂提问"):
            print("✅ 选人活动配置页面已打开!")
            page.screenshot(path="select_student_config.png")
        
        time.sleep(30)
        browser.close()
