"""
学习通选人脚本 - 通用版
用法: python select_student_generic.py <classId> <className>

使用方法（示例考试班验证通过）：
1. 登录学习通
2. 进入指定班级活动列表
3. 点击添加按钮（force=True）
4. 选择选人（.btnSelectPerson）
5. 填写选人事由
6. 点击 #selectPerson_begin（专用按钮ID）

关键点：
- 必须使用 #selectPerson_begin，不能用通用"立即开始"文本
- 弹窗处理需检查 z-index 和 position
- 添加按钮需用 force=True
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from playwright.sync_api import sync_playwright

PHONE = "YOUR_PHONE"
PWD = "190253"
COURSE_ID = "200000001"
CPI = "300000001"
ENC = "YOUR_ENC"
FID = "3012"
REASON = "随机选人提问"

def close_popups(page):
    """关闭所有弹窗（检查z-index和position）"""
    page.evaluate("""() => {
        const sels = '.popDiv,.maskDiv,.popBottom,.pick-container,.popPermission,.popMove,.popCellShowHide,.popLayer,.popbox,.popup,.modal,.overlay';
        document.querySelectorAll(sels).forEach(el => {
            const cs = getComputedStyle(el);
            if(cs.position==='fixed'||cs.position==='absolute'||parseInt(cs.zIndex)>100) el.style.display='none';
        });
        document.body.style.overflow='auto';
    }""")
    time.sleep(0.5)

def do_login(page):
    """登录学习通"""
    page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    inputs = page.locator("input[type='text']").all()
    if inputs: inputs[0].fill(PHONE)
    time.sleep(1)
    page.locator("input[type='password']").first.fill(PWD)
    time.sleep(1)
    page.locator("button[type='submit'],a.submitBtn,.loginBtn,button:has-text('登录'),a:has-text('登录')").first.click()
    time.sleep(15)

def select_student(class_id, class_name):
    """为指定班级创建选人活动"""
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_context(viewport={"width":1280,"height":800}, locale="zh-CN").new_page()
        page.set_default_timeout(30000)

        print(f"📝 登录学习通...", flush=True)
        do_login(page)

        print(f"📚 进入{class_name}活动列表...", flush=True)
        page.goto(
            f"https://mobilelearn.chaoxing.com/page/active/activeList"
            f"?fid={FID}&courseId={COURSE_ID}&classId={class_id}&enc={ENC}",
            wait_until="domcontentloaded", timeout=60000
        )
        time.sleep(5)
        close_popups(page)

        print(f"➕ 点击添加按钮...", flush=True)
        page.locator('.add-activate-icon').click(force=True)
        time.sleep(3)
        close_popups(page)

        print(f"👤 选择选人...", flush=True)
        page.evaluate("""() => {
            const el = document.querySelector('.btnSelectPerson');
            if(el){el.click();return;}
        }""")
        time.sleep(5)
        close_popups(page)

        # 填写选人事由
        try:
            page.wait_for_selector("input[placeholder*='请输入选人事由']", state="visible", timeout=5000)
            page.locator("input[placeholder*='请输入选人事由']").first.fill(REASON)
        except:
            pass
        time.sleep(1)
        close_popups(page)

        print(f"▶️ 点击立即开始...", flush=True)
        r = page.evaluate("""() => {
            const btn = document.getElementById('selectPerson_begin');
            if(!btn) return 'not found';
            btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
            let p=btn.parentElement;while(p&&p!==document.body){p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}
            btn.click();return 'clicked';
        }""")
        time.sleep(3)

        if "clicked" in r:
            print(f"✅ {class_name}选人创建成功！", flush=True)
            browser.close()
            p.stop()
            return "成功"
        else:
            print(f"❌ {class_name}选人按钮未找到", flush=True)
            browser.close()
            p.stop()
            return "失败"

    except Exception as e:
        print(f"❌ {class_name}选人错误: {e}", flush=True)
        return f"错误: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python select_student_generic.py <classId> <className>")
        sys.exit(1)
    
    class_id = sys.argv[1]
    class_name = sys.argv[2]
    
    result = select_student(class_id, class_name)
    print(f"\n选人结果: {result}", flush=True)
