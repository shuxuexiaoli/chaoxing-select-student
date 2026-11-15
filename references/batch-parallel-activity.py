"""
批量并行创建活动模板
支持在多个班级同时创建各类活动（选人、签到、随堂练习、抢答、主题讨论）

使用方法：
1. 修改 CLASSES 列表为你的班级
2. 修改 COURSE_PARAMS 为课程参数
3. 修改 activity_type 和 activity_config 为需要的活动类型和配置
4. 运行脚本，多个班级并行执行

性能参考：5个班级并行创建选人活动，总耗时约78秒
"""

import time
import threading
from playwright.sync_api import sync_playwright

# ============ 配置区 ============

# 班级列表
CLASSES = [
    {"name": "示例班级A", "classId": "100000001"},
    {"name": "示例班级B", "classId": "100000002"},
    {"name": "示例班级C", "classId": "100000003"},
    {"name": "示例班级D", "classId": "100000004"},
    {"name": "示例班级E", "classId": "100000005"},
]

# 课程公共参数
COURSE_PARAMS = {
    "courseId": "200000001",
    "cpi": "300000001",
    "enc": "YOUR_ENC",
    "fid": "3012"
}

# 登录信息
LOGIN_INFO = {
    "phone": "YOUR_PHONE",
    "password": "190253"
}

# 活动类型配置
# 可选: select_student, signin, quiz, quick_answer, discussion
ACTIVITY_TYPE = "select_student"

ACTIVITY_CONFIG = {
    "select_student": {
        "css_selector": ".btnSelectPerson",
        "input_placeholder": "请输入选人事由",
        "input_value": "随机选人提问",
        "name": "选人"
    },
    "signin": {
        "css_selector": ".btnSignIn",
        "input_placeholder": "请输入标题",
        "input_value": "课堂签到",
        "name": "签到"
    },
    "quiz": {
        "css_selector": ".btnTest",
        "input_placeholder": None,  # 随堂练习使用富文本编辑器
        "input_value": "函数f(x)=x²的导数是？",
        "name": "随堂练习"
    },
    "quick_answer": {
        "css_selector": ".btnQuickAnswer",
        "input_placeholder": "请输入抢答内容",
        "input_value": "请抢答：什么是导数？",
        "name": "抢答"
    },
    "discussion": {
        "css_selector": ".btnDiscuss",
        "input_placeholder": "请输入讨论话题",
        "input_value": "极值与最值的区别",
        "name": "主题讨论"
    }
}

# ============ 核心函数 ============

def click_start_button(page, class_name=""):
    """使用JavaScript点击可见的立即开始按钮
    
    重要：页面上有多个"立即开始"按钮，直接使用 page.click("text=立即开始") 会：
    1. 匹配到10+个元素
    2. Playwright选择第一个，但该元素可能不可见
    3. 超时30秒后失败
    
    此函数使用JavaScript找到可见的按钮并点击。
    """
    try:
        result = page.evaluate("""
            () => {
                const buttons = Array.from(document.querySelectorAll('a, button')).filter(el => 
                    el.textContent.trim() === '立即开始'
                );
                for (const btn of buttons) {
                    const style = window.getComputedStyle(btn);
                    if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                        btn.click();
                        return { success: true, text: btn.textContent };
                    }
                }
                if (buttons.length > 0) {
                    buttons[0].click();
                    return { success: true, text: buttons[0].textContent };
                }
                return { success: false, error: '未找到立即开始按钮' };
            }
        """)
        return result and result.get('success')
    except Exception as e:
        print(f"[{class_name}] ❌ JavaScript点击错误: {e}")
        return False

def create_activity_for_class(class_info, results, activity_type="select_student"):
    """为单个班级创建活动"""
    class_name = class_info["name"]
    class_id = class_info["classId"]
    config = ACTIVITY_CONFIG[activity_type]
    
    print(f"\n{'='*50}")
    print(f"开始处理: {class_name} (classId={class_id})")
    print(f"活动类型: {config['name']}")
    print(f"{'='*50}")
    
    try:
        # 用 start() 而不是 with，避免浏览器自动关闭
        p = sync_playwright().start()
        # 启动浏览器
        print(f"[{class_name}] [1] 启动浏览器...")
        browser = p.chromium.launch(channel="msedge", headless=False)  # 用户偏好Edge浏览器
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN"
        )
        page = context.new_page()
        page.set_default_timeout(30000)

        # 登录
        print(f"[{class_name}] [2] 导航到登录页面...")
        page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        print(f"[{class_name}] [3] 填写登录信息...")
        inputs = page.locator("input[type='text']").all()
        if inputs:
            inputs[0].fill(LOGIN_INFO["phone"])
        time.sleep(1)

        pwd_input = page.locator("input[type='password']").first
        pwd_input.fill(LOGIN_INFO["password"])
        time.sleep(1)

        print(f"[{class_name}] [4] 点击登录...")
        login_btn = page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first
        login_btn.click()

        print(f"[{class_name}] [5] 等待登录...")
        time.sleep(15)

        title = page.title()
        print(f"[{class_name}] [5] 页面标题: {title}")

        if "四川信息职业技术学院" not in title:
            print(f"[{class_name}] ❌ 登录失败!")
            results[class_name] = "登录失败"
            p.stop()
            return

        print(f"[{class_name}] [6] 登录成功!")

        # 导航到活动列表
        activity_url = (
            f"https://mobilelearn.chaoxing.com/page/active/activeList?"
            f"fid={COURSE_PARAMS['fid']}&courseId={COURSE_PARAMS['courseId']}"
            f"&classId={class_id}&cpi={COURSE_PARAMS['cpi']}&enc={COURSE_PARAMS['enc']}"
        )

        print(f"[{class_name}] [7] 导航到活动列表...")
        page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        title = page.title()
        print(f"[{class_name}] [7] 页面标题: {title}")

        if "活动列表" not in title:
            print(f"[{class_name}] ❌ 进入活动列表失败!")
            results[class_name] = "进入活动列表失败"
            p.stop()
            return

        print(f"[{class_name}] [8] 成功进入活动列表!")

        # 点击添加活动按钮
        print(f"[{class_name}] [9] 点击添加活动按钮...")
        try:
            page.click(".add-activate-icon")
            print(f"[{class_name}] [9] 点击成功!")
            time.sleep(3)
        except Exception as e:
            print(f"[{class_name}] [9] 错误: {e}")
            results[class_name] = f"点击添加活动失败: {e}"
            p.stop()
            return

        # 点击活动类型按钮
        print(f"[{class_name}] [10] 点击{config['name']}按钮...")
        try:
            page.click(config["css_selector"])
            print(f"[{class_name}] [10] 点击成功!")
            time.sleep(3)
        except Exception as e:
            print(f"[{class_name}] [10] 错误: {e}")
            results[class_name] = f"点击{config['name']}按钮失败: {e}"
            p.stop()
            return

        # 填写活动内容
        print(f"[{class_name}] [11] 填写活动内容...")
        try:
            if config["input_placeholder"]:
                input_field = page.locator(f"input[placeholder*='{config['input_placeholder']}'], textarea[placeholder*='{config['input_placeholder']}']").first
                if input_field:
                    input_field.fill(config["input_value"])
                    print(f"[{class_name}] [11] 填写成功: {config['input_value']}")
                    time.sleep(1)
                else:
                    print(f"[{class_name}] [11] 未找到输入框")
            else:
                print(f"[{class_name}] [11] 跳过（随堂练习使用富文本编辑器）")
        except Exception as e:
            print(f"[{class_name}] [11] 错误: {e}")

        # 点击立即开始按钮
        print(f"[{class_name}] [12] 点击立即开始按钮...")
        if click_start_button(page, class_name):
            print(f"[{class_name}] [12] 点击成功!")
            time.sleep(5)
        else:
            print(f"[{class_name}] [12] 点击失败!")
            results[class_name] = "点击立即开始失败"
            p.stop()
            return

        # 截图记录
        screenshot_path = rf"D:\BaiduSyncdisk\龙虾文件\screenshots\{activity_type}_{class_id}.png"
        page.screenshot(path=screenshot_path)
        print(f"[{class_name}] [13] 截图已保存: {screenshot_path}")

        print(f"[{class_name}] ✅ {config['name']}活动创建成功!")
        results[class_name] = "成功"

        # 关闭浏览器
        time.sleep(5)
        p.stop()
        print(f"[{class_name}] 浏览器已关闭")
            
    except Exception as e:
        print(f"[{class_name}] ❌ 发生错误: {e}")
        results[class_name] = f"错误: {e}"

def main():
    """主函数"""
    config = ACTIVITY_CONFIG[ACTIVITY_TYPE]
    
    print("="*60)
    print(f"批量创建{config['name']}活动 - 高等数学（进阶）课程")
    print("="*60)
    print(f"\n班级数量: {len(CLASSES)}")
    print(f"活动类型: {config['name']}")
    print("\n班级列表:")
    for cls in CLASSES:
        print(f"  - {cls['name']} (classId={cls['classId']})")
    print("\n" + "="*60)
    
    # 存储结果
    results = {}
    
    # 使用线程并行执行
    threads = []
    for class_info in CLASSES:
        thread = threading.Thread(
            target=create_activity_for_class,
            args=(class_info, results, ACTIVITY_TYPE)
        )
        threads.append(thread)
    
    # 启动所有线程
    print("\n开始并行执行...")
    start_time = time.time()
    
    for thread in threads:
        thread.start()
        time.sleep(3)  # 错开启动时间，避免同时登录
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 打印结果汇总
    print("\n" + "="*60)
    print("执行结果汇总")
    print("="*60)
    print(f"\n总耗时: {elapsed_time:.2f} 秒")
    print(f"活动类型: {config['name']}")
    print("\n各班级执行结果:")
    
    success_count = 0
    for class_name, result in results.items():
        status = "✅" if result == "成功" else "❌"
        print(f"  {status} {class_name}: {result}")
        if result == "成功":
            success_count += 1
    
    print(f"\n成功: {success_count}/{len(CLASSES)} 个班级")
    print("="*60)

if __name__ == "__main__":
    main()
