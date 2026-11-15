"""
通用选人脚本 - 支持任意班级
用法: python select_student_generic.py <classId> <班级名>

示例:
  python select_student_generic.py 100000005 示例班级E
  python select_student_generic.py 100000007 示例考试班

2026-06-08 创建
"""
import sys
import time
from playwright.sync_api import sync_playwright

if len(sys.argv) < 3:
    print("用法: python select_student_generic.py <classId> <班级名>")
    sys.exit(1)

CLASS_ID = sys.argv[1]
CLASS_NAME = sys.argv[2]
PHONE = "YOUR_PHONE"
PWD = "190253"

# 课程参数（根据班级自动判断）
EXAM_CLASSES = {"100000007"}  # 示例考试班
if CLASS_ID in EXAM_CLASSES:
    CP = {"courseId": "200000002", "cpi": "300000002", "enc": "9efe87cda9f0672e3ca7da9d3872007a", "fid": "3012"}
else:
    CP = {"courseId": "200000001", "cpi": "300000001", "enc": "YOUR_ENC", "fid": "3012"}

def close_popups(page):
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
    page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    inputs = page.locator("input[type='text']").all()
    if inputs: inputs[0].fill(PHONE)
    time.sleep(1)
    page.locator("input[type='password']").first.fill(PWD)
    time.sleep(1)
    page.locator("button[type='submit'],a.submitBtn,.loginBtn,button:has-text('登录'),a:has-text('登录')").first.click()
    time.sleep(15)

def select_student():
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_context(viewport={"width":1280,"height":800}, locale="zh-CN").new_page()
        page.set_default_timeout(30000)

        print(f"登录...", flush=True)
        do_login(page)

        print(f"进入{CLASS_NAME}活动列表...", flush=True)
        page.goto(
            f"https://mobilelearn.chaoxing.com/page/active/activeList"
            f"?fid={CP['fid']}&courseId={CP['courseId']}&classId={CLASS_ID}&enc={CP['enc']}",
            wait_until="domcontentloaded", timeout=60000
        )
        time.sleep(5)
        close_popups(page)

        print("点击添加按钮...", flush=True)
        page.locator('.add-activate-icon').click(force=True)
        time.sleep(3)
        close_popups(page)

        print("选择选人...", flush=True)
        page.evaluate("""() => {
            const el = document.querySelector('.btnSelectPerson');
            if(el){el.click();return;}
        }""")
        time.sleep(5)
        close_popups(page)

        try:
            page.wait_for_selector("input[placeholder*='请输入选人事由']", state="visible", timeout=5000)
            page.locator("input[placeholder*='请输入选人事由']").first.fill("随机选人提问")
        except:
            pass
        time.sleep(1)
        close_popups(page)

        print("点击立即开始...", flush=True)
        r = page.evaluate("""() => {
            const btn = document.getElementById('selectPerson_begin');
            if(!btn) return 'not found';
            btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
            let p=btn.parentElement;while(p&&p!==document.body){p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}
            btn.click();return 'clicked';
        }""")
        time.sleep(3)

        if "clicked" in r:
            print(f"✅ {CLASS_NAME}选人创建成功!", flush=True)
            return "成功"
        else:
            print(f"❌ 选人按钮未找到: {r}", flush=True)
            return "失败"

        browser.close()
        p.stop()

    except Exception as e:
        print(f"❌ 错误: {e}", flush=True)
        return f"错误: {e}"

result = select_student()
print(f"\n选人结果: {result}", flush=True)
