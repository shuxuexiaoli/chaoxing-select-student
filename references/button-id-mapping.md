# 学习通活动按钮ID映射表

**2026-06-08 验证通过**

## 按钮ID映射

每个活动类型有唯一的按钮ID，创建活动时必须使用对应的ID精确点击。

| 活动类型 | CSS选择器 | 按钮ID | 说明 |
|---------|----------|--------|------|
| 签到 | `.btnSignIn` | `signin_begin` | 签到活动的"立即开始"按钮 |
| 选人 | `.btnSelectPerson` | `selectPerson_begin` | 选人活动的"立即开始"按钮 |
| 主题讨论 | `.btnDiscuss` | `discuss_begin` | 主题讨论的"立即开始"按钮 |
| 抢答 | `.btnQuickAnswer` | `quickAnswer_begin` | 抢答活动的"立即开始"按钮 |
| 随堂练习 | `.btnTest` | `test_begin` | 随堂练习的"立即开始"按钮 |

## 通用点击函数

```python
def click_btn_by_id(page, btn_id):
    """精确点击指定ID的按钮"""
    r = page.evaluate(f"""() => {{
        const btn = document.getElementById('{btn_id}');
        if(!btn) return 'not found';
        btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
        let p=btn.parentElement;while(p&&p!==document.body){{p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}}
        btn.click();return 'clicked';
    }}""")
    time.sleep(3)
    return 'clicked' in str(r)
```

## 使用示例

```python
# 签到
click_btn_by_id(page, 'signin_begin')

# 选人
click_btn_by_id(page, 'selectPerson_begin')

# 主题讨论
click_btn_by_id(page, 'discuss_begin')
```

## 完整活动创建流程

```python
# 1. 进入活动列表
page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
time.sleep(5)
close_popups(page)

# 2. 点击添加按钮
page.locator('.add-activate-icon').click(force=True)
time.sleep(3)
close_popups(page)

# 3. 选择活动类型
page.evaluate("""() => {
    const el = document.querySelector('.btnSignIn');  # 或 .btnSelectPerson, .btnDiscuss
    if(el){el.click();return;}
}""")
time.sleep(5)
close_popups(page)

# 4. 填写表单（如果需要）
# 签到不需要填写
# 选人需要填写事由
# 主题讨论需要填写话题

# 5. 点击立即开始（使用按钮ID）
click_btn_by_id(page, 'signin_begin')  # 或 selectPerson_begin, discuss_begin
```

## 常见错误

### ❌ 错误1：通用文本匹配
```python
# ❌ 会匹配到错误按钮
for (let el of document.querySelectorAll('a')) {
    if (el.textContent.trim() === '立即开始') { el.click(); }
}
```

### ❌ 错误2：使用 locator.click()
```python
# ❌ 会被弹窗遮挡
page.locator("text=立即开始").click()
```

### ❌ 错误3：使用 page.click()
```python
# ❌ 会超时失败
page.click("text=立即开始")
```

## 验证方法

创建活动后，检查页面是否跳转到活动结果页：
- 签到：URL包含 `/page/sign/endSign`
- 选人：URL包含 `/page/selectperson/selectPerson`
- 主题讨论：URL不变，但活动出现在列表中
