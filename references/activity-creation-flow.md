# 学习通活动创建完整流程

## 通用活动创建流程（6步）

### 第1步：登录
```python
page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
time.sleep(5)
inputs = page.locator("input[type='text']").all()
if inputs: inputs[0].fill(PHONE)
time.sleep(1)
page.locator("input[type='password']").first.fill(PWD)
time.sleep(1)
page.locator("button[type='submit'],a.submitBtn,.loginBtn,button:has-text('登录'),a:has-text('登录')").first.click()
time.sleep(15)
```

### 第2步：进入活动列表
```python
page.goto(
    f"https://mobilelearn.chaoxing.com/page/active/activeList"
    f"?fid={FID}&courseId={COURSE_ID}&classId={class_id}&enc={ENC}",
    wait_until="domcontentloaded", timeout=60000
)
time.sleep(5)
close_popups(page)
```

### 第3步：点击添加按钮
```python
page.locator('.add-activate-icon').click(force=True)
time.sleep(3)
close_popups(page)
```

### 第4步：点击活动类型
```python
# 签到
page.evaluate("""() => {
    const el = document.querySelector('.btnSignIn');
    if(el){el.click();return;}
}""")

# 选人
page.evaluate("""() => {
    const el = document.querySelector('.btnSelectPerson');
    if(el){el.click();return;}
}""")

# 主题讨论
page.evaluate("""() => {
    const el = document.querySelector('.btnDiscuss');
    if(el){el.click();return;}
}""")
time.sleep(5)
close_popups(page)
```

### 第5步：填写表单（如果需要）
```python
# 签到：选"普通签到"
page.evaluate("""() => {
    const spans = document.querySelectorAll('.pop-signin-content span, .signin-tab span, span');
    for (const s of spans) {
        if (s.textContent.trim() === '普通签到' && s.offsetParent !== null) {
            s.click(); return 'clicked';
        }
    }
    return 'not found';
}""")
time.sleep(8)
close_popups(page)

# 选人：填事由
try:
    page.wait_for_selector("input[placeholder*='请输入选人事由']", state="visible", timeout=5000)
    page.locator("input[placeholder*='请输入选人事由']").first.fill(REASON)
except:
    pass
time.sleep(1)
close_popups(page)

# 主题讨论：填话题（等15秒）
time.sleep(15)
close_popups(page)
try:
    page.wait_for_selector("#discussTitle", state="visible", timeout=10000)
    page.locator("#discussTitle").fill(topic)
except:
    page.evaluate(f'() => {{ const el=document.getElementById("discussTitle"); if(el){{el.value="{topic}";el.dispatchEvent(new Event("input",{{bubbles:true}}));}} }}')
time.sleep(2)
close_popups(page)
```

### 第6步：点击专用按钮ID
```python
# 签到
r = page.evaluate("""() => {
    const btn = document.getElementById('signin_begin');
    if(!btn) return 'not found';
    btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
    let p=btn.parentElement;while(p&&p!==document.body){p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}
    btn.click();return 'clicked';
}""")

# 选人
r = page.evaluate("""() => {
    const btn = document.getElementById('selectPerson_begin');
    if(!btn) return 'not found';
    btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
    let p=btn.parentElement;while(p&&p!==document.body){p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}
    btn.click();return 'clicked';
}""")

# 主题讨论
r = page.evaluate("""() => {
    const btn = document.getElementById('discuss_begin');
    if(!btn) return 'not found';
    btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
    let p=btn.parentElement;while(p&&p!==document.body){p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}
    btn.click();return 'clicked';
}""")
time.sleep(3)
```

## 关键Pitfalls

1. **必须使用专用按钮ID**：不能用通用的"立即开始"文本匹配，会找不到按钮
2. **弹窗处理**：每次操作前调用 `close_popups(page)`，检查 z-index 和 position
3. **主题讨论表单加载慢**：点击 `.btnDiscuss` 后等15秒
4. **签到需选类型**：点击 `.btnSignIn` 后需再选"普通签到"
5. **force=True**：点击 `.add-activate-icon` 时使用 `force=True`
6. **话题用 Playwright fill()**：不用 JS el.value，不触发数据绑定

## 脚本模板

- 签到：`~/.hermes/scripts/signin_generic.py`
- 选人：`~/.hermes/scripts/select_student_generic.py`
- 主题讨论：`~/.hermes/scripts/auto_discussion_daily.py`
- 通用活动：`~/.hermes/scripts/exam_class_all.py`
