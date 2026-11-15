# Playwright自动化参考

## 安装
```bash
pip install playwright -i https://pypi.tuna.tsinghua.edu.cn/simple
playwright install chromium
```

## 基本用法
```python
from playwright.sync_api import sync_playwright
import time

# ✅ 用 start() 而不是 with，避免浏览器自动关闭
p = sync_playwright().start()
browser = p.chromium.launch(
    headless=False,  # 显示浏览器窗口
    channel="msedge",  # 用户偏好Edge浏览器
    args=['--start-maximized']
)

page = browser.new_page()
page.goto("https://example.com", wait_until="networkidle", timeout=30000)

# 填写表单
page.fill("#input-id", "value")

# 点击按钮
page.click("text=按钮文字")

# 截图
page.screenshot(path="screenshot.png", full_page=True)

# 不加 browser.close()，保持浏览器打开
# p.stop()  # 只在确定要关闭时调用
```

## ❌ 错误写法（会导致浏览器莫名关闭）
```python
# 不要用 with 语句！脚本结束或异常时浏览器会自动被杀
with sync_playwright() as p:
    browser = p.chromium.launch(...)
    # ... 操作 ...
    browser.close()  # with退出时已经关了，这行多余
```

## 学习通专用
```python
# 登录学习通
page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded")
time.sleep(5)

# 填写手机号（使用input[type='text']更可靠）
inputs = page.locator("input[type='text']").all()
if inputs:
    inputs[0].fill("手机号")
time.sleep(1)

# 填写密码
page.locator("input[type='password']").first.fill("密码")
time.sleep(1)

# 点击登录（无需勾选隐私政策）
login_btn = page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first
login_btn.click()
time.sleep(15)  # 等待登录完成
```

## 注意事项
- 用户偏好使用Edge浏览器：`channel="msedge"` 或 `executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"`
- Edge基于Chromium，页面底部会显示"chrome-xxx"（内核版本号），这是正常的
- 使用清华镜像加速pip安装：`-i https://pypi.tuna.tsinghua.edu.cn/simple`
- `playwright install chromium`可能需要较长时间，建议使用系统已安装的浏览器
- 登录后需要等待15秒左右，页面跳转较慢
- 当前学习通登录页面没有隐私政策复选框，无需勾选
