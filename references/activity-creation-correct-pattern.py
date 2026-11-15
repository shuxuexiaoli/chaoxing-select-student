"""
正确的活动创建模式（2026-06-01验证）
关键点：
1. 使用精确的class选择器（li.btnDiscuss），不要用文本匹配
2. 每个步骤后必须关闭弹窗
3. 关闭弹窗后再填写表单和点击按钮
"""
import time
import json
from playwright.sync_api import sync_playwright

COURSE_PARAMS = {
    'courseId': '200000002',
    'cpi': '300000002',
    'enc': 'YOUR_ENC',
    'fid': '3012'
}
CLASS = {'name': '示例考试班', 'classId': '100000007'}
PHONE = 'YOUR_PHONE'
PWD = '190253'


def close_popups(page):
    """关闭所有弹窗 — 每个步骤后调用"""
    page.evaluate("""() => {
        const popups = document.querySelectorAll('.popDiv, .maskDiv, .popBottom, .pick-container, .popPermission, .popMove, .popCellShowHide');
        for (let el of popups) {
            el.style.display = 'none';
        }
    }""")
    time.sleep(1)


def click_start_button(page):
    """强制显示并点击立即开始按钮"""
    result = page.evaluate("""() => {
        const all = document.querySelectorAll('a, button, div');
        for (let el of all) {
            if ((el.textContent||'').trim() === '立即开始') {
                el.style.display = 'block';
                el.style.visibility = 'visible';
                el.style.width = 'auto';
                el.style.height = 'auto';
                el.style.opacity = '1';
                el.click();
                return 'clicked';
            }
        }
        return 'not found';
    }""")
    if result == 'clicked':
        time.sleep(3)
        # 检查确认弹窗
        page.evaluate("""() => {
            const all = document.querySelectorAll('a, button, div');
            for (let el of all) {
                const text = (el.textContent||'').trim();
                if (text === '确定' || text === '确认') {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0) { el.click(); }
                }
            }
        }""")
        time.sleep(3)
        return True
    return False


def create_discussion(page, topic):
    """创建主题讨论 — 使用精确class选择器"""
    close_popups(page)
    page.click('.add-activate-icon')
    time.sleep(3)
    close_popups(page)
    
    # ✅ 使用精确的class选择器，不要用文本匹配
    page.evaluate("""() => {
        const btn = document.querySelector('li.btnDiscuss');
        if (btn && btn.offsetParent !== null) {
            btn.click();
            return 'clicked';
        }
        return 'not found';
    }""")
    time.sleep(8)
    close_popups(page)
    
    # 填写话题
    page.evaluate(f"""() => {{
        const el = document.getElementById('discussTitle');
        if (el) {{
            el.style.display = 'block';
            el.style.visibility = 'visible';
            el.value = {json.dumps(topic)};
            el.dispatchEvent(new Event('input', {{bubbles:true}}));
        }}
    }}""")
    time.sleep(2)
    close_popups(page)
    
    return click_start_button(page)


def create_signin(page):
    """创建签到 — 4步流程"""
    close_popups(page)
    page.click('.add-activate-icon')
    time.sleep(3)
    close_popups(page)
    
    # 点击签到类型
    page.evaluate("""() => {
        const li = document.querySelector('li.btnSignIn');
        if (li) { li.click(); return; }
    }""")
    time.sleep(3)
    close_popups(page)
    
    # 选择普通签到
    page.evaluate("""() => {
        const tabs = document.querySelectorAll('.signin-tab span, .pop-signin-content span');
        for (const s of tabs) {
            if (s.textContent.trim() === '普通签到') {
                s.click(); return;
            }
        }
    }""")
    time.sleep(8)
    close_popups(page)
    
    return click_start_button(page)


def create_select(page, reason):
    """创建选人活动"""
    close_popups(page)
    page.click('.add-activate-icon')
    time.sleep(3)
    close_popups(page)
    
    # 使用精确的class选择器
    page.evaluate("""() => {
        const btn = document.querySelector('li.btnSelectPerson');
        if (btn && btn.offsetParent !== null) {
            btn.click();
            return 'clicked';
        }
        return 'not found';
    }""")
    time.sleep(8)
    close_popups(page)
    
    # 填写事由
    try:
        page.wait_for_selector('input[placeholder*="事由"]', state='visible', timeout=10000)
        page.locator('input[placeholder*="事由"]').fill(reason)
    except:
        pass
    time.sleep(2)
    close_popups(page)
    
    return click_start_button(page)


def main():
    name = CLASS['name']
    cid = CLASS['classId']
    cp = COURSE_PARAMS
    
    p = sync_playwright().start()
    browser = p.chromium.launch(channel='msedge', headless=True)
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800}, locale='zh-CN')
    page = ctx.new_page()
    page.set_default_timeout(30000)
    
    # 登录
    page.goto('https://passport2.chaoxing.com/login', wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)
    inputs = page.locator("input[type='text']").all()
    if inputs:
        inputs[0].fill(PHONE)
    time.sleep(1)
    page.locator("input[type='password']").first.fill(PWD)
    time.sleep(1)
    page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first.click()
    time.sleep(15)
    
    # 进入活动列表
    page.goto(
        f'https://mobilelearn.chaoxing.com/page/active/activeList'
        f'?fid={cp["fid"]}&courseId={cp["courseId"]}&classId={cid}&cpi={cp["cpi"]}&enc={cp["enc"]}',
        wait_until='domcontentloaded', timeout=60000
    )
    time.sleep(5)
    
    # 创建签到
    print('创建签到...')
    signin = create_signin(page)
    print(f'签到: {"✅" if signin else "❌"}')
    
    # 返回活动列表
    page.goto(
        f'https://mobilelearn.chaoxing.com/page/active/activeList'
        f'?fid={cp["fid"]}&courseId={cp["courseId"]}&classId={cid}&cpi={cp["cpi"]}&enc={cp["enc"]}',
        wait_until='domcontentloaded', timeout=60000
    )
    time.sleep(5)
    
    # 创建主题讨论
    print('创建主题讨论...')
    discuss = create_discussion(page, '你每天花多少时间在数学上？')
    print(f'主题讨论: {"✅" if discuss else "❌"}')
    
    # 返回活动列表
    page.goto(
        f'https://mobilelearn.chaoxing.com/page/active/activeList'
        f'?fid={cp["fid"]}&courseId={cp["courseId"]}&classId={cid}&cpi={cp["cpi"]}&enc={cp["enc"]}',
        wait_until='domcontentloaded', timeout=60000
    )
    time.sleep(5)
    
    # 创建选人
    print('创建选人...')
    select = create_select(page, '随机提问')
    print(f'选人: {"✅" if select else "❌"}')
    
    p.stop()


if __name__ == '__main__':
    main()
