"""
学习通签到通用脚本（任意班级）
用法: python signin_generic.py <classId> <班级名>

2026-06-08 创建：使用 #signin_begin 按钮ID方法
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from playwright.sync_api import sync_playwright

PHONE = "YOUR_PHONE"
PWD = "190253"

# 经济数学课程参数
CP = {"courseId":"200000001","cpi":"300000001","enc":"YOUR_ENC","fid":"3012"}

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

def signin(class_id, class_name):
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
            f"?fid={CP['fid']}&courseId={CP['courseId']}&classId={class_id}&enc={CP['enc']}",
            wait_until="domcontentloaded", timeout=60000
        )
        time.sleep(5)
        close_popups(page)
        
        print(f"➕ 点击添加按钮...", flush=True)
        page.locator('.add-activate-icon').click(force=True)
        time.sleep(3)
        close_popups(page)
        
        print(f"✍️ 选择签到...", flush=True)
        page.evaluate("""() => {
            const el = document.querySelector('.btnSignIn');
            if(el){el.click();return;}
            document.querySelectorAll('li,.list,[class*="btn"]').forEach(e => {
                if((e.textContent||'').trim().includes('签到')&&e.offsetParent!==null) e.click();
            });
        }""")
        time.sleep(5)
        close_popups(page)
        
        print(f"▶️ 点击立即开始...", flush=True)
        r = page.evaluate("""() => {
            const btn = document.getElementById('signin_begin');
            if(!btn) return 'not found';
            btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
            let p=btn.parentElement;while(p&&p!==document.body){p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}
            btn.click();return 'clicked';
        }""")
        time.sleep(3)
        
        if "clicked" in str(r):
            print(f"✅ {class_name}签到创建成功！", flush=True)
            browser.close()
            p.stop()
            return "成功"
        else:
            print(f"❌ 签到按钮未找到: {r}", flush=True)
            browser.close()
            p.stop()
            return "失败"
    except Exception as e:
        print(f"❌ 错误: {e}", flush=True)
        return f"错误: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python signin_generic.py <classId> <班级名>")
        sys.exit(1)
    class_id = sys.argv[1]
    class_name = sys.argv[2]
    result = signin(class_id, class_name)
    print(f"\n签到结果: {result}", flush=True)
