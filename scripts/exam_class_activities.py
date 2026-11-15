"""
示例考试班 - 创建签到、主题讨论、选人活动
适用于任何班级，修改 COURSE_PARAMS 和 CLASS 即可
"""
import time
import json
from playwright.sync_api import sync_playwright

# 课程参数（根据目标课程修改）
COURSE_PARAMS = {
    'courseId': '200000002',
    'cpi': '300000002',
    'enc': 'YOUR_ENC',
    'fid': '3012'
}

CLASS = {'name': '示例考试班', 'classId': '100000007'}
PHONE = 'YOUR_PHONE'
PWD = '190253'


def create_activity(page, activity_type, title=''):
    """创建活动（签到/主题讨论/选人）"""
    # 点击添加活动按钮
    print(f'  [1] 点击添加活动...')
    add_btn = page.locator('.add-activate-icon')
    add_btn.wait_for(state='visible', timeout=10000)
    add_btn.click()
    time.sleep(3)
    
    if activity_type == 'signin':
        print(f'  [2] 点击签到...')
        page.evaluate("""() => {
            const li = document.querySelector('li.btnSignIn');
            if (li) { li.click(); return; }
            const lis = document.querySelectorAll('li.list');
            for (const el of lis) {
                if (el.textContent.trim().startsWith('签到') && el.offsetParent !== null) {
                    el.click(); return;
                }
            }
        }""")
        time.sleep(3)
        print(f'  [3] 点击普通签到...')
        page.evaluate("""() => {
            const tabs = document.querySelectorAll('.signin-tab span, .pop-signin-content span, .tab-box span');
            for (const s of tabs) {
                if (s.textContent.trim() === '普通签到') { s.click(); return; }
            }
        }""")
        time.sleep(8)
        
    elif activity_type == 'discuss':
        print(f'  [2] 点击主题讨论...')
        page.evaluate("""() => {
            const els = document.querySelectorAll('.btnDiscuss, li.list');
            for (let el of els) {
                if (el.textContent && el.textContent.includes('主题讨论') && el.offsetParent !== null) {
                    el.click(); return;
                }
            }
        }""")
        time.sleep(8)
        if title:
            print(f'  [3] 填写话题...')
            try:
                page.wait_for_selector('#discussTitle', state='visible', timeout=15000)
                page.locator('#discussTitle').fill(title)
            except:
                page.evaluate(f"""() => {{
                    const el = document.getElementById('discussTitle');
                    if (el) {{ el.value = {json.dumps(title)}; el.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                }}""")
            time.sleep(2)
    
    elif activity_type == 'select':
        print(f'  [2] 点击选人...')
        page.evaluate("""() => {
            const lis = document.querySelectorAll('.btnSelectPerson, li.list');
            for (const el of lis) {
                if (el.textContent && el.textContent.includes('选人') && el.offsetParent !== null) {
                    el.click(); return;
                }
            }
        }""")
        time.sleep(8)
        if title:
            print(f'  [3] 填写事由...')
            try:
                page.wait_for_selector('input[placeholder*="事由"]', state='visible', timeout=10000)
                page.locator('input[placeholder*="事由"]').fill(title)
            except:
                pass
            time.sleep(2)
    
    # 点击立即开始按钮（签到可能自动跳转，需先检查）
    if activity_type == 'signin':
        time.sleep(10)
        page_text = page.evaluate("document.body.innerText.substring(0, 500)")
        if '已签' in page_text or '签到率' in page_text:
            print(f'  ✅ 签到已创建（自动跳转到结果页）')
            return True

    print(f'  [4] 点击立即开始...')
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
        print(f'  ✅ 点击成功')
        time.sleep(3)
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
    else:
        print(f'  ❌ 未找到立即开始按钮')
        return False


def main():
    name = CLASS['name']
    cid = CLASS['classId']
    cp = COURSE_PARAMS
    
    print(f'{"="*60}')
    print(f'{name} - 创建签到、主题讨论、选人活动')
    print(f'{"="*60}')
    
    p = sync_playwright().start()
    browser = p.chromium.launch(channel='msedge', headless=True)
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800}, locale='zh-CN')
    page = ctx.new_page()
    page.set_default_timeout(30000)
    
    # 登录
    print(f'\n[{name}] 登录...')
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
    
    if '四川信息职业技术学院' not in page.title():
        print(f'[{name}] ❌ 登录失败')
        p.stop()
        return
    
    print(f'[{name}] ✅ 登录成功')
    
    # 进入活动列表
    activity_url = f'https://mobilelearn.chaoxing.com/page/active/activeList?fid={cp["fid"]}&courseId={cp["courseId"]}&classId={cid}&cpi={cp["cpi"]}&enc={cp["enc"]}'
    
    results = {}
    for i, (atype, title) in enumerate([
        ('signin', ''),
        ('discuss', '测试主题讨论：你每天花多少时间在数学上？请分享你的学习方法。'),
        ('select', '随机提问')
    ]):
        print(f'\n【{i+1}/3】创建{{"signin":"签到","discuss":"主题讨论","select":"选人"}[atype]}活动')
        page.goto(activity_url, wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)
        results[atype] = create_activity(page, atype, title)
        print(f'结果: {"✅ 成功" if results[atype] else "❌ 失败"}')
    
    print(f'\n{"="*60}')
    print(f'任务完成总结：')
    for k, v in results.items():
        print(f'  {k}: {"✅" if v else "❌"}')
    print(f'{"="*60}')
    
    p.stop()


if __name__ == '__main__':
    main()
