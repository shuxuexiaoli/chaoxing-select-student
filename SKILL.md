---
name: chaoxing-select-student
description: "学习通（超星学习通）创建课堂活动的自动化操作指南。支持选人、签到、随堂练习、抢答、主题讨论等活动类型。包含登录、进入课程、进入班级活动、创建各类活动的完整Playwright自动化流程。支持批量定时发送主题讨论（带进度跟踪）和自动签到（cron定时）。"
version: 2.0.0
author: user
metadata:
  hermes:
    tags: [teaching, chaoxing, education, automation]
    related_skills: [playwright-browser-automation]
---

# 学习通课堂活动自动化操作指南（选人、签到等）

## 本地环境适配（WorkBuddy，2026-11-04 标注）

本技能原先运行在 Hermes 平台，迁到 WorkBuddy 后以下三处需要按新环境处理：

1. **脚本实际位置**：`C:\Users\Administrator\.workbuddy\skills\chaoxing-select-student\scripts\`。
   文档中出现的 `~/AppData/Local/hermes/scripts` 是历史路径，该目录已不存在，执行前替换为上面的实际路径。
2. **定时任务**：WorkBuddy 不使用 hermes cron，改用内置 automation（`automation_update`，支持 rrule 周期）。
   本文档 Pitfall 22/23/27~32 中关于 cron 的排错经验仅作历史参考，不适用于当前环境。
3. **运行时依赖**：需要 `playwright`（浏览器用 `channel="msedge"`，本机 Edge 已安装，无需下载内核）。
   当前机器 Python 环境尚未安装 playwright，首次执行前先 `pip install playwright`。

## 用户偏好（重要）

### 固定技能
用户要求以下技能固定使用，不要随意变更：
1. **数学公式转Word格式** - 使用 math-document-authoring 技能
2. **学习通操作** - 签到、主题讨论、选人等课堂活动自动化

### 登录确认
首次登录时询问用户选择登录方式（扫码/验证码），确认后记住选择，后续直接使用同一方式，不再询问。变更前需与用户确认。

### 任务删除确认
删除全部cron任务前，必须先找用户确认，得到同意后再执行。

### 主题讨论生成方法
经济数学5个班（示例班级A/2、示例班级C、示例班级D/2）和高等数学进阶示例考试班使用**相同的方法**生成主题讨论，只是courseId、cpi、enc等参数不同。

### 多活动批量创建
用户经常需要在同一个班级创建多种活动（签到+主题讨论+选人）。参考 `scripts/exam_class_activities.py` 了解完整流程。

### 通用脚本适用于所有课程
通用脚本（signin_generic.py, select_student_generic.py, discussion_generic.py）内置的是经济数学的courseId/cpi/enc参数，但**签到和选人活动的URL只依赖classId**，所以可以直接用于示例考试班（classId=100000007）等其他课程班级。2026-06-09验证：三种活动在示例考试班全部创建成功。

### Cron任务方式（2026-06-09 更新）
用户明确要求：**所有定时任务使用agent模式cron**（`no_agent=False`），在prompt中指示agent调用terminal执行通用脚本。不要用`no_agent=True`模式（live adapter投递静默失败，见Pitfall 29）。prompt示例：
```
请立即执行以下命令为示例班级B创建签到活动：
cd ~/AppData/Local/hermes/scripts && python signin_generic.py 100000002 示例班级B

执行完成后，报告签到结果。
```

---

## 前置条件
- 已获取课程参数（courseId, classId, cpi, fid, enc）
- 已知班级名称和classId
- 账号已登录学习通

## 学校信息
- **四川信息职业技术学院官网**: https://www.scitc.edu.cn/
- **信息门户（智慧川信）**: https://zhcx.scitc.edu.cn/ （注意：cas.svci.edu.cn 无法解析，不要使用）
- **学校地址**: 四川省广元市利州区学府路265号
- **邮编**: 628000

## 脚本文件

本skill提供以下可重用脚本，可在浏览器控制台或Playwright中执行：

### 通用脚本（支持任意班级）
- `scripts/signin_generic.py` — 签到通用脚本（参数：classId 班级名）
- `scripts/select_student_generic.py` — 选人通用脚本（参数：classId 班级名 [事由]）
- `scripts/quick_answer_generic.py` — **抢答通用脚本**（参数：classId 班级名 [内容]，默认内容"请抢答"）
- `scripts/discussion_generic.py` — 主题讨论通用脚本（参数：classId 班级名 [话题]）
- `scripts/reminder_generic.py` — 课堂提醒脚本（参数：班级名 教室 节次）
- `scripts/exam_class_all.py` — 组合活动脚本（一次性创建签到+选人+主题讨论）
- `scripts/auto_discussion_daily.py` — 主题讨论每日自动发送（进度跟踪）

### 参考文档
- `references/button-id-mapping.md` — **关键！** 按钮ID映射表（#signin_begin等）
- `references/cron-job-setup.md` — 定时任务设置指南
- `references/cron-delivery-diagnosis.md` — **Cron投递问题诊断记录**（live adapter静默失败的发现过程）

### 自动签到系统（定时任务）
- `~/.hermes/scripts/auto_signin.py` — **自动签到主脚本**（参数化，接受节次参数如 `1-2`、`3-4`）
- `~/.hermes/scripts/signin_12.py` — 第1-2节签到（08:45触发，周一~五）
- `~/.hermes/scripts/signin_34.py` — 第3-4节签到（10:25触发，周一~五）
- `~/.hermes/scripts/signin_56.py` — 第5-6节签到（13:55触发，周一~五）
- `~/.hermes/scripts/signin_78.py` — 第7-8节签到（15:45触发，周一~五）
- `~/.hermes/scripts/signin_910.py` — 第9-10节签到（18:55触发，周一~五）
- 5个cron job对应5个时间点，全部周一至周五触发，脚本内嵌SCHEDULE自动过滤无课日
- 选人脚本每个时段保留1个r1+1个r2（共10个活跃），其余16个已暂停
- 使用headless Edge + Playwright自动登录学习通
- 签到结果发送到微信
- 参考 `references/auto-signin-system.md` 了解完整架构和课表数据

### 活动创建脚本

- `scripts/login.js` — 登录学习通
- `scripts/navigate_course.js` — 进入课程
- `scripts/navigate_class.js` — 进入班级活动
- `scripts/create_select_student.js` — 创建选人活动（浏览器控制台版）
- `scripts/create_select_student_playwright.py` — 创建选人活动（Playwright版）
- `scripts/create_signin_playwright.py` — 创建签到活动（Playwright版）
- `scripts/create_quiz_playwright.py` — 创建随堂练习活动（Playwright版）
- `scripts/create_quick_answer_playwright.py` — 创建抢答活动（Playwright版）
- `scripts/quick_answer_generic.py` — 抢答通用脚本（命令行参数版，支持任意班级）
- `scripts/create_discussion_playwright.py` — 创建主题讨论活动（Playwright版）
- `scripts/auto_discussion_batch.py` — **批量定时发送主题讨论模板**（带进度跟踪，每天发2个，cron定时）
- `references/batch-discussion-with-progress.md` — **批量主题讨论自动发送方案**：进度跟踪JSON、cron定时、每天N个的分批策略
- `references/math-discussion-topics-template.md` — **数学主题讨论话题生成模板**：生活场景库、话题结构、经济数学13个知识点清单
- `references/batch-discussion-creation.py` — **批量并行创建主题讨论模板**（5班同时执行，含完整错误处理）
- `references/single-class-discussion-test.md` — **单班级测试脚本模板**（测试新课程/新班级的主题讨论发送）
- `references/activity-creation-correct-pattern.py` — **正确的活动创建模式**（2026-06-01验证）：精确class选择器 + 每步关闭弹窗，支持签到/主题讨论/选人
- `references/select-student-complete.py` — **完整的端到端自动化脚本**（登录→课程→活动列表→添加选人→填写事由→启动活动）
- `references/select-student-single-class.md` — **单班级选人快速参考**（按班级切换classId、按活动类型切换CSS选择器）
- `references/playwright-complete-automation.py` — 完整的Playwright自动化脚本（登录→进入课程→班级活动→活动列表）
- `references/playwright-login-course.py` — Playwright自动化登录+进入课程脚本
- `references/batch-parallel-activity.py` — **批量并行创建活动模板**（多班级同时执行，支持选人/签到/随堂练习/抢答/主题讨论）— **最新版本，包含完整的ACTIVITY_TYPE切换和ACTIVITY_CONFIG配置**
- `references/batch-and-automation.md` — **批量操作与自动签到模式**：并行创建活动模板、cron自动签到脚本模式、课表时间
- `references/information-portal.md` — **信息门户（智慧川信）自动化**：从官网导航到信息门户、验证码登录流程、表单元素精确定位技巧
- `references/class-list-api.md` — **班级列表API**：获取课程所有班级的API端点、完整班级列表（经济数学55个班、高等数学进阶47个班）
- `references/homework-creation.md` — **作业创建指南**：作业不在移动端活动列表中，需通过PC课程管理页面创建（mooc1-1.chaoxing.com）
- `references/schedule-sync-workflow.md` — **课表同步工作流**：教务系统课表变化时，同步更新class_reminder.py和auto_signin.py的完整流程（CDP读取→对比→更新→验证）。**⚠️ 包含HTML表格innerText的tab分隔解析pitfall**（多tab=空列，必须正确计数）

## 操作流程

### 1. 登录学习通
```javascript
// 打开登录页: https://passport2.chaoxing.com/login

// 填入手机号和密码
document.querySelector('#phone').value = '手机号';
document.querySelector('#pwd').value = '密码';

// 点击登录按钮
document.querySelector('.login-btn').click();

// 登录成功后跳转到: i.mooc.chaoxing.com/space/index
```

**Playwright方式（推荐）：**
```python
from playwright.sync_api import sync_playwright
import time

# 用 start() 而不是 with，避免浏览器自动关闭（见 Pitfall 12）
p = sync_playwright().start()
browser = p.chromium.launch(channel="msedge", headless=False)  # 用户偏好Edge浏览器
context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
page = context.new_page()
page.set_default_timeout(30000)

page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
time.sleep(5)

# 填写手机号和密码
inputs = page.locator("input[type='text']").all()
if inputs:
    inputs[0].fill("手机号")
time.sleep(1)

page.locator("input[type='password']").first.fill("密码")
time.sleep(1)

# 点击登录按钮（无需勾选隐私政策，当前页面没有隐私政策复选框）
login_btn = page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first
login_btn.click()

time.sleep(15)  # 等待登录完成，需要较长时间
```

> ⚠️ **重要**：当前学习通登录页面**没有隐私政策复选框**，只有一个"下次自动登录"的复选框（不需要勾选）。无需执行任何复选框操作。

### 2. 进入课程

课程列表加载在iframe中，需要先找到正确的iframe再操作。

**方式A：通过iframe点击课程（推荐）**
```python
# 点击左侧菜单"课程"
page.click("text=课程")
time.sleep(5)

# 查找包含课程列表的iframe
frames = page.frames
course_frame = None
for frame in frames:
    try:
        content = frame.content()
        if "目标课程名" in content:
            course_frame = frame
            break
    except:
        pass

# 在iframe中点击课程
if course_frame:
    course_frame.click("text=目标课程名")
    time.sleep(5)
```

**方式B：直接提取课程URL并导航（更可靠）**
```python
# 点击左侧菜单"课程"
page.click("text=课程")
time.sleep(5)

# 在iframe中查找课程链接
course_frame = None
for frame in page.frames:
    try:
        if "目标课程名" in frame.content():
            course_frame = frame
            break
    except:
        pass

if course_frame:
    # 使用JavaScript提取课程URL
    result = course_frame.evaluate("""
        () => {
            const links = document.querySelectorAll('a');
            for (let link of links) {
                if (link.textContent && link.textContent.includes('目标课程名')) {
                    return link.href;
                }
            }
            return null;
        }
    """)
    
    if result:
        # 直接导航到课程URL
        page.goto(result, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
```

**课程URL格式：**
```
https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={courseId}&edit=true&enc={enc}&v=2&cpi={cpi}&baseEducation=0
```

导航后会自动跳转到：
```
https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/tch?courseid={courseId}&clazzid={clazzid}&cpi={cpi}&enc={enc}
```

### 3. 进入班级活动
```javascript
// 课程主页URL示例:
// https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/tch?courseid={courseId}&clazzid={clazzid}&cpi={cpi}

// 左侧菜单点击"班级活动"
// iframe地址: https://mobilelearn.chaoxing.com/page/class/classList?courseid={courseId}&clazzid={clazzid}&cpi={cpi}&enc={enc}&fid={fid}
```

### 4. 进入目标班级活动列表
```javascript
// 在班级列表页找到目标班级
const classItems = document.querySelectorAll('li.class-list');

classItems.forEach(item => {
  if (item.getAttribute('classname') === '示例班级B') {
    const btn = item.querySelector('.jb_btn');
    btn.scrollIntoView();
    btn.click();
  }
});

// 跳转到活动列表:
// https://mobilelearn.chaoxing.com/page/active/activeList?fid={fid}&courseId={courseId}&classId={classId}&cpi={cpi}&enc={enc}
```

### 5. 创建选人活动

> ⚠️ **重要**：必须使用正确的CSS选择器，否则点击会超时或无效。
> - 添加活动按钮: `.add-activate-icon`
> - 选人选项: `.btnSelectPerson`（不是 `.title-name`）

```javascript
// 点击"添加活动"按钮（使用 .add-activate-icon 类）
document.querySelector('.add-activate-icon').click();

// 弹出活动类型菜单
// 包含: 签到、抢答、选人、评分、问卷、主题讨论、分组任务、词云、随堂练习、作业、考试、直播

// 点击"选人"（使用 .btnSelectPerson 类）
document.querySelector('.btnSelectPerson').click();
```

**Playwright方式：**
```python
# 点击添加活动按钮
page.click(".add-activate-icon")
time.sleep(3)

# 点击选人选项
page.click(".btnSelectPerson")
time.sleep(3)

# 此时会弹出选人配置窗口，包含：
# - 选人事由输入框
# - 优先2小时内签到人员（开关）
# - 每次选人数量（默认1人）
# - 活动时长（默认5分钟）
# - 手动结束（开关）
# - 多班发放（开关）
# - 保存 / 立即开始 按钮
```

## 完整Playwright自动化流程（推荐）

**模板文件：**
- `templates/select_student_generic_template.py` — 通用选人脚本模板（可指定班级）
- `templates/auto_discussion_template.py` — 主题讨论自动发送脚本模板（带进度跟踪）

完整的自动化脚本位于 `references/playwright-complete-automation.py`，包含以下函数：

### 函数说明

```python
from playwright.sync_api import sync_playwright
import time

# 1. 登录学习通
def login_chaoxing(page, phone="YOUR_PHONE", password=YOUR_PASSWORD"):
    """登录成功标志：页面标题变为"四川信息职业技术学院""""
    page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    inputs = page.locator("input[type='text']").all()
    if inputs:
        inputs[0].fill(phone)
    time.sleep(1)
    page.locator("input[type='password']").first.fill(password)
    time.sleep(1)
    login_btn = page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first
    login_btn.click()
    time.sleep(15)  # 等待登录完成
    return "四川信息职业技术学院" in page.title()

# 2. 进入课程
def enter_course(page, course_id, enc, cpi):
    """直接导航到课程页面"""
    course_url = f"https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={course_id}&edit=true&enc={enc}&v=2&cpi={cpi}&baseEducation=0"
    page.goto(course_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    return "高等数学" in page.title() or "经济数学" in page.title()

# 3. 进入班级活动
def enter_class_activity(page):
    """点击左侧菜单进入班级活动"""
    page.click("text=班级活动")
    time.sleep(5)

# 4. 进入活动列表
def enter_activity_list(page, course_id, class_id, cpi, enc, fid=YOUR_FID):
    """直接导航到指定班级的活动列表"""
    activity_url = f"https://mobilelearn.chaoxing.com/page/active/activeList?fid={fid}&courseId={course_id}&classId={class_id}&cpi={cpi}&enc={enc}"
    page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    return "活动列表" in page.title()

# 5. 在iframe中查找课程URL
def find_course_url_in_iframe(page, course_name):
    """从课程列表iframe中提取课程URL"""
    page.click("text=课程")
    time.sleep(5)
    for frame in page.frames:
        try:
            content = frame.content()
            if course_name in content:
                result = frame.evaluate(f"""
                    () => {{
                        const links = document.querySelectorAll('a');
                        for (let link of links) {{
                            if (link.textContent && link.textContent.includes('{course_name}')) {{
                                return link.href;
                            }}
                        }}
                        return null;
                    }}
                """)
                if result:
                    return result
        except:
            pass
    return None
```

### 使用示例

**快速启动选人活动（完整流程）：**
```python
# 使用 references/select-student-complete.py 中的函数
from references.select_student_complete import (
    login_chaoxing, enter_course, enter_activity_list,
    open_add_activity_menu, click_select_student, fill_reason_and_start
)
from playwright.sync_api import sync_playwright
import time

p = sync_playwright().start()
browser = p.chromium.launch(channel="msedge", headless=False)
context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
page = context.new_page()
page.set_default_timeout(30000)

if login_chaoxing(page):
    if enter_course(page, "200000002", "enc", "cpi"):
        if enter_activity_list(page, "200000002", "100000007", "cpi", "enc"):
            open_add_activity_menu(page)
            click_select_student(page)
            fill_reason_and_start(page, "随机选人提问")

# 保持浏览器打开，不加 browser.close()
```

**分步操作：**
```python
from playwright.sync_api import sync_playwright
import time

p = sync_playwright().start()
browser = p.chromium.launch(channel="msedge", headless=False)
context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
page = context.new_page()
page.set_default_timeout(30000)

if login_chaoxing(page):
    if enter_course(page, "200000002", "13c0bfec572bb3435c1d29bbd19487e5", "300000002"):
        if enter_activity_list(page, "200000002", "100000007", "300000002", "9efe87cda9f0672e3ca7da9d3872007a"):
            page.screenshot(path="activity_list.png")

# 保持浏览器打开
```

## 关键参数示例

```yaml
# 四川信息职业技术学院 - 经济数学课程
courseId: 200000001
clazzid: 100000006  # 示例总班级
cpi: 300000001
fid: YOUR_FID
enc: "YOUR_ENC"

# 班级配置（5个班级）
classes:
  - name: "示例班级A"
    classId: 100000001
    studentCount: 46
  - name: "示例班级B"
    classId: 100000002
    studentCount: 46
  - name: "示例班级C"
    classId: 100000003
  - name: "示例班级D"
    classId: 100000004
  - name: "示例班级E"
    classId: 100000005

# 高等数学（进阶）— cpi和enc与经济数学不同！
courseId: 200000002
clazzid: 100000007  # 示例考试班
cpi: 300000002  # 注意：不是300000001（那是经济数学的cpi）
enc: "YOUR_ENC"  # 示例考试班classEnc
courseEnc: "4E4DAA868184A5D37E55FA8C70F5978B"
课程页面enc: "18ffaf76d71653b36e1345ed68a53d77"
作业openc: "d05c8342cfd569d27cf863a31a130ce3"
教师: 伍星

# 高等数学（进阶）班级配置
classes:
  - name: "示例考试班"
    classId: 100000007
    enc: "9efe87cda9f0672e3ca7da9d3872007a"
  - name: "高数3重修班"
    studentCount: 26
  - name: "高数1重修"
    studentCount: 86
  - name: "数学建模"
    studentCount: 40
  - name: "AI24-3"
    studentCount: 24
  - name: "计网24-3"
    studentCount: 51
```

### 快速访问URL

**经济数学 - 班级活动列表页面**：
```
https://mobilelearn.chaoxing.com/page/class/classList?courseid=200000001&clazzid=100000006&cpi=300000001&enc=YOUR_ENC&fid=YOUR_FID
```

**经济数学 - 5个班级活动列表**：
```
示例班级A: https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000001&classId=100000001&cpi=300000001&enc=YOUR_ENC
示例班级B: https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000001&classId=100000002&cpi=300000001&enc=YOUR_ENC
示例班级C: https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000001&classId=100000003&cpi=300000001&enc=YOUR_ENC
示例班级D: https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000001&classId=100000004&cpi=300000001&enc=YOUR_ENC
示例班级E: https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000001&classId=100000005&cpi=300000001&enc=YOUR_ENC
```

**高等数学（进阶） - 示例考试班活动列表**：
```
https://mobilelearn.chaoxing.com/page/active/activeList?fid=YOUR_FID&courseId=200000002&classId=100000007&cpi=300000002&enc=YOUR_ENC
```

**高等数学（进阶） - 课程管理页面**：
```
https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId=200000002&edit=true&enc=YOUR_ENC
```

**高等数学（进阶） - 示例考试班作业页面**（需先建立session）：
```
https://mooc1-1.chaoxing.com/mooc-ans/work/getAllWork?classId=100000007&courseId=200000002&isdisplaytable=2&mooc=1&ut=t&enc=YOUR_ENC&cpi=300000002&openc=YOUR_ENC
```

## 登录注意事项

### Playwright自动化登录
- 学习通登录页使用JavaScript渲染，需要等待页面加载完成
- 密码输入框id为`#pwd`，手机号输入框id为`#phone`
- 登录按钮class为`.login-btn`，也可用`text=登录`选择器
- 登录后需要等待较长时间（8-15秒）让页面跳转完成
- **重要**：当前版本登录页面没有隐私政策复选框，只有"下次自动登录"复选框（可忽略）
- 登录成功标志：页面标题变为"四川信息职业技术学院"

### 登录代码示例（Playwright Python）
```python
from playwright.sync_api import sync_playwright
import time

p = sync_playwright().start()
browser = p.chromium.launch(channel="msedge", headless=False)
context = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
page = context.new_page()

page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
time.sleep(5)

# 填写手机号和密码
inputs = page.locator("input[type='text']").all()
if inputs:
    inputs[0].fill("手机号")
time.sleep(1)

pwd_input = page.locator("input[type='password']").first
pwd_input.fill("密码")
time.sleep(1)

# 点击登录
login_btn = page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first
login_btn.click()

# 等待登录完成
time.sleep(15)

# 检查登录是否成功
title = page.title()
if "四川信息职业技术学院" in title:
    print("登录成功!")

# 保持浏览器打开，不加 browser.close()
```

### 登录失败排查
1. 确认密码是否正确
2. 检查是否需要验证码（滑动验证、图形验证码）
3. 账号是否被锁定（多次失败后）
4. 尝试手动登录验证账号状态

## 浏览器操作注意事项

1. **iframe处理**: 学习通大量使用iframe，操作前需确认目标在哪个frame中
2. **等待加载**: iframe加载需要时间，操作前等待页面稳定（至少5秒）
3. **元素定位**: 使用`document.querySelector`定位元素
4. **滚动可见**: 操作前调用`element.scrollIntoView()`
5. **弹窗处理**: 可能有隐私政策、提示等弹窗，需先处理
6. **登录等待**: 登录后需要等待15秒左右，页面跳转较慢
7. **页面标题验证**: 登录成功的标志是页面标题变为"四川信息职业技术学院"

## 重要Pitfalls

### Pitfall 1: 课程卡片点击无效
课程列表在iframe中，直接点击课程卡片可能无效。**推荐使用方式B（提取URL直接导航）**，更可靠。

### Pitfall 2: 隐私政策复选框不存在
当前学习通登录页面**没有隐私政策复选框**，只有一个"下次自动登录"的复选框（不需要勾选）。无需执行任何复选框操作。

### Pitfall 6: 添加活动菜单的正确CSS选择器
**重要**：添加活动菜单的CSS选择器：
- 添加活动按钮: `.add-activate-icon`（不是 `text=+添加活动` 或 `text=添加活动`）
- 选人选项: `.btnSelectPerson`（不是 `.title-name` 或 `text=选人`）
- 签到选项: `.btnSignIn`（不是 `text=签到`）

### ⚠️ Pitfall 26: 按钮ID是唯一可靠的方法（2026-06-08 验证）
**绝对不要用"立即开始"文本匹配**——页面上有10+个同名按钮，大部分不可见（width=0），会导致点击失败。

**正确方法：用按钮ID精确点击**：
| 活动类型 | 按钮ID | 
|---------|--------|
| 签到 | `#signin_begin` |
| 选人 | `#selectPerson_begin` |
| 主题讨论 | `#discuss_begin` |
| 抢答 | `#quickAnswer_begin` |
| 随堂练习 | `#test_begin` |

**通用点击函数（必须使用）**：
```python
def click_btn_by_id(page, btn_id):
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

**为什么之前的方法失败**：
- `page.evaluate("...立即开始...")` → 匹配到10+个按钮，大部分width=0
- `page.locator("text=立即开始")` → 超时，找不到可见元素
- `btns[-1]['x'], btns[-1]['y']` → 坐标点击有时无效

**为什么按钮ID方法成功**：
- 每个活动类型有唯一的按钮ID
- 直接操作DOM，不依赖可见性检测
- 强制设置CSS确保按钮可点击

使用错误的选择器会导致点击超时或点击无效。JavaScript版本和Playwright版本都必须使用这些正确的CSS选择器。

**⚠️ 签到的额外步骤**：点击 `.btnSignIn` 后会弹出签到类型选择框（普通签到、手势签到、位置签到、二维码签到、签到码签到），必须再点击"普通签到"选项。**点击"普通签到"后页面直接跳转到签到结果页（显示"已签/未签/签到率"），签到自动开始，不需要也不出现"立即开始"按钮**（2026-06-08验证）。详见第7节"创建签到活动"。
### Pitfall 7: "立即开始"按钮的点击（关键坑点）— 必须使用按钮ID精确点击

**2026-06-08 关键发现**：页面上有多个活动类型的"立即开始"按钮，每个活动类型有自己唯一的按钮ID。用通用文本匹配"立即开始"会匹配到错误按钮或找不到按钮。

**✅ 正确方法：使用按钮ID精确点击**

| 活动类型 | 按钮ID |
|---------|--------|
| 签到 | `#signin_begin` |
| 选人 | `#selectPerson_begin` |
| 主题讨论 | `#discuss_begin` |
| 抢答 | `#quickAnswer_begin` |
| 随堂练习 | `#test_begin` |

```python
# ✅ 正确：精确点击按钮ID
def click_btn_by_id(page, btn_id):
    r = page.evaluate(f"""() => {{
        const btn = document.getElementById('{btn_id}');
        if(!btn) return 'not found';
        btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
        let p=btn.parentElement;while(p&&p!==document.body){{p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}}
        btn.click();return 'clicked';
    }}""")
    time.sleep(3)
    return 'clicked' in str(r)

# 使用示例
click_btn_by_id(page, 'signin_begin')       # 签到
click_btn_by_id(page, 'selectPerson_begin')  # 选人
click_btn_by_id(page, 'discuss_begin')       # 主题讨论
```

**❌ 错误做法（会导致失败）**：
```python
# ❌ 通用文本匹配 — 会匹配到错误按钮
for (let el of document.querySelectorAll('a')) {
    if (el.textContent.trim() === '立即开始') { el.click(); }
}
```

**为什么通用方法失败**：
1. 页面上有10+个"立即开始"按钮（每种活动类型都有）
2. 大部分按钮 `width=0`（不可见/未渲染）
3. 直接点击会匹配到错误活动类型的按钮

### Pitfall 3: iframe中的JavaScript执行
在iframe中执行JavaScript时，需要使用`frame.evaluate()`而不是`page.evaluate()`，否则会报错。

### Pitfall 4: 活动列表URL构造
活动列表URL格式为：`https://mobilelearn.chaoxing.com/page/active/activeList?fid={fid}&courseId={courseId}&classId={classId}&cpi={cpi}&enc={enc}`

## 课程导航技巧

### 直接URL导航（推荐）
使用直接URL导航比点击UI更可靠：

**进入课程页面**：
```
https://mooc1-1.chaoxing.com/mooc-ans/coursecontroller/isNewCourse?courseId={courseId}&edit=true&enc={enc}&v=2&cpi={cpi}&baseEducation=0
```

**进入班级活动列表**：
```
https://mobilelearn.chaoxing.com/page/active/activeList?fid={fid}&courseId={courseId}&classId={classId}&cpi={cpi}&enc={enc}
```

### 从课程列表获取课程URL
1. 登录后点击"课程"菜单
2. 在iframe中找到目标课程
3. 提取课程链接中的courseId、enc、cpi等参数
4. 使用直接URL导航

### 添加活动操作
**点击"+添加活动"按钮**：
```python
page.click(".add-activate-icon")
time.sleep(3)
```

**选择"选人"活动**：
```python
page.click(".btnSelectPerson")
time.sleep(5)
```

**活动类型选择菜单：**
- 点击".add-activate-icon"后会弹出活动类型选择菜单
- 菜单分类：
  - **课堂活动**：签到(`.btnSignIn`)、选人(`.btnSelectPerson`)、随堂练习、主题讨论、抢答、问卷、分组任务、投票、评分、抽签、群聊、AI实践
  - **教学工具**：白板、计时器、腾讯会议、直播、通知
  - **教学资源**：课件、教案、章节、资料、笔记、云盘、电脑文件、网页链接

### 6. 填写选人事由并开始活动

点击"选人"后会弹出配置窗口，需要填写事由并点击"立即开始"。

**弹窗内容：**
- 选人事由输入框（placeholder: "请输入选人事由"）
- 优先2小时内签到人员（开关，默认开启）
- 每次选人数量（默认1人）
- 活动时长（默认0天0小时5分钟）
- 手动结束（开关，默认关闭）
- 多班发放（开关，默认关闭）
- 保存 / 立即开始 按钮

**Playwright方式：**
```python
# 填写选人事由
input_field = page.locator("input[placeholder*='请输入选人事由'], textarea[placeholder*='请输入选人事由']").first
if input_field:
    input_field.fill("随机选人提问")
    time.sleep(1)

# 点击"立即开始"按钮（在弹窗中）
# ⚠️ 重要：页面上有多个"立即开始"按钮，需要找到弹窗中的那个
# 方法：在弹窗/modal中查找
result = page.evaluate("""
    () => {
        const popups = document.querySelectorAll('.popup, .modal, .dialog, div[class*="pop"], div[class*="modal"]');
        for (let popup of popups) {
            if (popup.offsetParent !== null) {
                const buttons = popup.querySelectorAll('button, a, div');
                for (let btn of buttons) {
                    if (btn.textContent && btn.textContent.trim() === '立即开始') {
                        const rect = btn.getBoundingClientRect();
                        return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                    }
                }
            }
        }
        return null;
    }
""")

if result:
    page.mouse.click(result['x'], result['y'])
    time.sleep(5)
```

**活动开始后的页面：**
- 页面标题变为"选人"
- URL变为: `https://mobilelearn.chaoxing.com/page/selectperson/selectPerson?activeId={activeId}&classId={classId}&courseId={courseId}&fid={fid}&cpi={cpi}&showOnScreenShare=true&returnType=1`
- 显示活动名称、倒计时、"导出数据"和"结束活动"按钮

### 7. 创建签到活动（2026-06-01修正，2026-06-08再修正）

签到活动只需要**3步**（比选人少一步）：

**⚠️ 点击 `.btnSignIn` → 选择"普通签到"后，签到自动开始，页面跳转到结果页。没有标题输入框，没有"立即开始"按钮。**

**Playwright方式：**
```python
# 第1步：点击添加活动按钮
page.click(".add-activate-icon")
time.sleep(3)

# 第2步：点击"签到"活动类型 (li.btnSignIn)
page.evaluate("""() => {
    const li = document.querySelector('li.btnSignIn');
    if (li) { li.click(); return 'clicked'; }
    const els = document.querySelectorAll('li.list');
    for (const el of els) {
        if (el.textContent.includes('签到') && el.offsetParent !== null) {
            el.click(); return 'clicked2';
        }
    }
    return 'not found';
}""")
time.sleep(3)

# 第3步：选择"普通签到" — 点击后签到自动开始，页面跳转到结果页
page.evaluate("""() => {
    const spans = document.querySelectorAll('.pop-signin-content span, .signin-tab span, .tab-box span, span');
    for (const s of spans) {
        if (s.textContent.trim() === '普通签到' && s.offsetParent !== null) {
            s.click(); return 'clicked';
        }
    }
    return 'not found';
}""")
time.sleep(8)

# 完成！页面已跳转到签到结果页，显示"已签/未签/签到率"
# 不需要填写标题，不需要点击"立即开始"
```

**签到配置窗口内容（点击"普通签到"后自动生效，不展示配置界面）：**
- 签到类型：普通签到（选择后直接开始）
- 页面跳转到签到结果页，显示已签/未签人数和签到率
- 备注/标题无法在创建时设置（签到直接开始）

**签到活动开始后的页面：**
- 页面标题变为"签到"
- URL变为: `https://mobilelearn.chaoxing.com/page/sign/endSign?activeId={activeId}&classId={classId}&courseId={courseId}&cpi={cpi}&showOnScreenShare=true&returnType=1&fid={fid}`
- 显示签到类型（普通签到）、开始时间、倒计时
- 已签/未签统计、签到率
- "导出数据"、"结束活动"、"投屏模式" 按钮

### 10. 创建主题讨论活动

主题讨论活动使用 `.btnDiscuss` 类选择。

**Playwright方式：**
```python
# 点击添加活动按钮
page.click(".add-activate-icon")
time.sleep(3)
close_popups(page)  # ⚠️ 必须关闭弹窗！

# 点击主题讨论选项
page.locator(".btnDiscuss").first.click()
time.sleep(15)  # 必须等15秒
close_popups(page)  # ⚠️ 关闭弹窗再填写
```

⚠️ **主题讨论表单需要等15秒才能完全渲染**（不是8秒或10秒）。等不够会导致textarea不可见、按钮width=0。

**主题讨论配置页面内容：**
- 讨论话题输入框（`textarea#discussTitle`，不是input）
- 参与奖励积分（默认2分）
- 活动时长（默认1天）
- 手动结束开关
- 功能开关：允许查看回复、匿名回复等
- 保存 / 立即开始 按钮

**填写话题并开始讨论（推荐方式）：**
```python
# ⚠️ 必须等15秒让表单渲染
time.sleep(15)

# 填写讨论话题（用Playwright fill，不要用JS el.value）
# JS el.value 不会触发框架的数据绑定，导致提交时话题为空
try:
    page.wait_for_selector("#discussTitle", state="visible", timeout=10000)
    page.locator("#discussTitle").fill("不定积分的实际意义")
except:
    # 备选：JS赋值（可能不触发数据绑定）
    page.evaluate("""() => {
        const el = document.getElementById('discussTitle');
        if (el) { el.value = '话题内容'; el.dispatchEvent(new Event('input', {bubbles:true})); }
    }""")
time.sleep(2)

# 点击"立即开始"按钮
# ⚠️ 页面上有10个"立即开始"按钮，必须过滤：
# 1. 排除 hideMyself class
# 2. 只选 width > 0 的（有实际尺寸的）
# 3. 用 page.mouse.click 点击坐标，不要用 locator.click
btns = page.evaluate("""() => {
    const all = document.querySelectorAll('a');
    const result = [];
    for (let el of all) {
        if ((el.textContent||'').trim() === '立即开始' && !el.className.includes('hideMyself')) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                result.push({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
            }
        }
    }
    return result;
}""")
if btns:
    page.mouse.click(btns[-1]['x'], btns[-1]['y'])  # 点最后一个（弹窗中的）
    time.sleep(5)
```

**判断创建是否成功：**
- 点击"立即开始"后，URL **不会变化**（仍停留在activeList页面）
- 弹窗会关闭
- 成功标志：活动列表中出现新创建的主题讨论
- 不要依赖URL变化判断成功与否

**批量创建主题讨论：**
- 用 `threading` 并行执行，每个线程独立浏览器实例
- 启动线程时错开3秒
- 偶尔1-2个班级会失败（表单加载问题），需单独重试
- 批量创建主题讨论模板：`templates/batch_discussion.py`（5班并行，含重试逻辑）
- **最新批量模板**：`templates/batch_discussion_v2.py`（force_click_start，2026-06-08验证5班全成功）
- 完整脚本：`scripts/create_discussion_playwright.py`

**主题讨论开始后的页面：**
- 页面标题变为"主题讨论"
- 显示讨论话题、开始时间
- 讨论内容编辑区
- 参与人数统计
- "导出数据"、"结束活动"、"投屏模式" 按钮

### 9. 创建抢答活动

抢答活动使用 `.btnQuickAnswer` 类选择。

**Playwright方式：**
```python
# 点击添加活动按钮
page.click(".add-activate-icon")
time.sleep(3)

# 点击抢答选项（使用 .btnQuickAnswer 类）
result = page.evaluate("""
    () => {
        const elements = document.querySelectorAll('.btnQuickAnswer, li.list');
        for (let el of elements) {
            if (el.textContent && el.textContent.includes('抢答') && el.offsetParent !== null) {
                el.click();
                return 'Clicked!';
            }
        }
        return 'Not found';
    }
""")
time.sleep(3)
```

**抢答配置窗口内容：**
- 内容输入框（placeholder: "请输入抢答内容"）
- 时长设置：小时、分钟、秒（默认0小时5分钟0秒）
- 手动结束（开关，默认关闭）
- 允许抢答人数（默认"全部"）
- 功能开关（默认关闭）：
  - 根据抢答顺序奖励积分
  - 抢答需输入答案
  - 延时抢答
  - 多班发放
- 保存 / 立即开始 按钮

**填写内容并开始抢答：**
```python
# 填写抢答内容
input_field = page.locator("input[placeholder*='请输入抢答内容'], textarea[placeholder*='请输入抢答内容']").first
if input_field:
    input_field.fill("请抢答：什么是导数？")
    time.sleep(1)

# 点击"立即开始"按钮（在弹窗中，使用与其他活动相同的弹窗按钮查找方法）
result = page.evaluate("""
    () => {
        const buttons = document.querySelectorAll('a, button, div');
        for (let btn of buttons) {
            if (btn.textContent && btn.textContent.trim() === '立即开始' && btn.offsetParent !== null) {
                const rect = btn.getBoundingClientRect();
                return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
            }
        }
        return null;
    }
""")
if result:
    page.mouse.click(result['x'], result['y'])
    time.sleep(5)
```

**抢答活动开始后的页面：**
- 页面标题变为"抢答"
- URL变为: `https://mobilelearn.chaoxing.com/page/answer/teaQuickAnswer?activeId={activeId}&classId={classId}&courseId={courseId}&fid={fid}&returnType=1&cpi={cpi}&showOnScreenShare=true`
- 显示抢答内容、开始时间
- 已参与人数统计、剩余时长
- 抢答人员列表
- "导出数据"、"结束活动"、"投屏模式" 按钮

**活动类型CSS选择器汇总（2026-06-08 更新）：**

**⚠️ 关键：每个活动类型有唯一的按钮ID，创建活动时必须使用对应的ID精确点击！**

| 分类 | 活动类型 | CSS选择器 | 按钮ID |
|------|---------|----------|--------|
| **课堂活动** | 签到 | `.btnSignIn` | `signin_begin` |
| | 选人 | `.btnSelectPerson` | `selectPerson_begin` |
| | 随堂练习 | `.btnTest` | `test_begin` |
| | 主题讨论 | `.btnDiscuss` | `discuss_begin` |
| | 抢答 | `.btnQuickAnswer` | `quickAnswer_begin` |
| | 问卷 | `.btnQuestionnaire` |
| | 分组任务 | `.btnTask` |
| | 投票 | `.btnVote` |
| | 评分 | `.btnGrade` |
| | 抽签 | `.btnDrawLots` |
| | 群聊 | `.btnStudentBack` |
| | AI实践 | `.btnAiEvaluate` |
| **教学工具** | 白板 | `.btnWhiteBoard` |
| | 计时器 | `.btnTimer` |
| | 腾讯会议 | `.btnWeMeet` |
| | 直播 | `.btnZhibo` |
| | 通知 | `.btnNotice` |
| **教学资源** | 课件 | `.btnCourseware` |
| | 教案 | `.btnTeachPlan` |
| | 章节 | `.btnChapter` |
| | 资料 | `.btnResourceData` |
| | 笔记 | `.btnNote` |
| | 云盘 | `.btnResourceYun` |
| | 电脑文件 | `.btnResourceFile` |
| | 网页链接 | `.btnResourceLink` |
| 活动类型 | CSS选择器 | 配置字段 | 启动后URL模式 |
|---------|----------|---------|-------------|
| 选人 | `.btnSelectPerson` | 选人事由 (`input[placeholder*='请输入选人事由']`) | `/page/selectperson/selectPerson?activeId=` |
| 签到 | `.btnSignIn` | **无配置字段** — 点击"普通签到"后自动开始 | `/page/sign/endSign?activeId=` |
| 随堂练习 | `.btnTest` | 题目内容 (富文本编辑器) | `/page/quiz/quizStatisticsPage?activeId=` |
| 抢答 | `.btnQuickAnswer` | 抢答内容 (`input[placeholder*='请输入抢答内容']`) | `/page/answer/teaQuickAnswer?activeId=` |
| 主题讨论 | `.btnDiscuss` | 讨论话题 (`input[placeholder*='请输入讨论话题']`) | `/page/discuss/discussList?activeId=` |
| 问卷 | `.btnQuestionnaire` | — | — |

**活动开始后URL模式（注意：签到无"立即开始"按钮，点击"普通签到"后直接跳转）：**
| 活动类型 | URL模式 |
|---------|--------|
| 选人 | `https://mobilelearn.chaoxing.com/page/selectperson/selectPerson?activeId={activeId}&...` |
| 签到 | `https://mobilelearn.chaoxing.com/page/sign/endSign?activeId={activeId}&...` |
| 随堂练习 | `https://mobilelearn.chaoxing.com/page/quiz/quizStatisticsPage?activeId={activeId}&...` |
| 抢答 | `https://mobilelearn.chaoxing.com/page/answer/teaQuickAnswer?activeId={activeId}&...` |
| 主题讨论 | `https://mobilelearn.chaoxing.com/page/discuss/discussList?activeId={activeId}&...` |

### 10. 创建主题讨论活动（2026-05-31验证）

主题讨论活动使用 `.btnDiscuss` 类选择。

⚠️ **关键pitfalls**（已验证）：
- 点击 `.btnDiscuss` 后**必须等15秒**（不是8秒），表单才能完全渲染
- 讨论话题输入框是 `textarea#discussTitle`，不是input
- 用 `page.locator("#discussTitle").fill(topic)` 填写（JS `el.value` 不触发框架数据绑定）
- "立即开始"按钮页面上有10个，需过滤：`!className.includes('hideMyself')` 且 `rect.width > 0`
- 用 `page.mouse.click(x, y)` 点击，不要用 `page.click("text=立即开始")`
- 点击后**URL不变**，弹窗关闭，活动出现在列表中即表示成功
- 批量5班并行偶尔1-2个失败（表单未加载），需单独重试

**⚠️ 主题讨论表单加载慢，必须等15秒（见 Pitfall 10）。**

**Playwright方式：**
```python
# 点击添加活动按钮
page.click(".add-activate-icon")
time.sleep(3)

# 点击主题讨论选项
page.locator(".btnDiscuss").first.click()
time.sleep(15)  # 必须等15秒！表单加载慢

# 用Playwright fill填写话题（不要用JS）
page.locator("#discussTitle").fill("讨论话题内容")
time.sleep(2)
```

**主题讨论配置页面内容：**
- 讨论话题输入框（placeholder: "请输入讨论话题"）
- 讨论内容编辑区（富文本编辑器）
- 发送通知开关
- 活动时长设置
- 保存 / 立即开始 按钮

**填写话题并开始讨论：**
```python
# 填写讨论话题（用Playwright fill，不用JS）
page.locator("#discussTitle").fill("不定积分的实际意义")
time.sleep(2)

# 点击"立即开始"按钮 — 查找有尺寸的可见按钮
result = page.evaluate("""
    () => {
        const all = document.querySelectorAll('a');
        for (let el of all) {
            if ((el.textContent||'').trim() === '立即开始' && !el.className.includes('hideMyself')) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0) {
                    el.click();
                    return 'clicked';
                }
            }
        }
        return 'not found';
    }
""")
time.sleep(5)
# 注意：点击后URL可能不会变化（仍停留在activeList页面），但活动已创建成功
# 验证方法：检查活动列表中是否出现新的话题讨论条目
```

**主题讨论开始后的页面：**
- 页面标题变为"主题讨论"
- 显示讨论话题、开始时间
- 讨论内容编辑区
- 参与人数统计
- "导出数据"、"结束活动"、"投屏模式" 按钮

### Pitfall 14: 主题讨论表单渲染慢 + "立即开始"按钮定位（关键！）

创建主题讨论时，点击 `.btnDiscuss` 后**必须等待10-15秒**（不是5秒），表单才能完全渲染。否则：
- `#discussTitle` textarea 存在但不可见（`getBoundingClientRect()` 返回 0）
- 所有"立即开始"按钮宽度为0
- `page.locator("#discussTitle").fill()` 超时报 `element is not visible`

**正确流程：**
```python
# 1. 点击主题讨论
page.locator(".btnDiscuss").first.click()
time.sleep(15)  # 必须等15秒！

# 2. 填写话题（是 textarea#discussTitle，不是 input）
try:
    page.wait_for_selector("#discussTitle", state="visible", timeout=10000)
    page.locator("#discussTitle").fill(topic)
except:
    page.evaluate(f"""() => {{
        const el = document.getElementById('discussTitle');
        if (el) {{ el.value = '{topic}'; el.dispatchEvent(new Event('input', {{bubbles:true}})); }}
    }}""")

# 3. 点击"立即开始"——页面上有10+个同名按钮，只有弹窗中的有尺寸
btns = page.evaluate("""() => {
    const all = document.querySelectorAll('a');
    const result = [];
    for (let el of all) {
        if ((el.textContent||'').trim() === '立即开始' && !el.className.includes('hideMyself')) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                result.push({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
            }
        }
    }
    return result;
}""")
if btns:
    page.mouse.click(btns[-1]['x'], btns[-1]['y'])  # 取最后一个
    time.sleep(5)
```

**"立即开始"按钮分析：**
- 每个活动行都有一个"开始"或"立即开始" `<a>` 标签，class=`jb_btn jb_btn_92 fr fs14`
- 只有弹窗/浮层中的按钮有实际尺寸（width > 0），活动列表中的都是 width=0
- 用 `btns[-1]` 取最后一个有尺寸的按钮（即弹窗中的）
- 点击后 URL 不变（带 `#` 后缀），弹窗关闭，活动出现在列表中 = 成功
- `hideMyself` class 的按钮应跳过

**错误做法（会导致空白页面）：**
```python
# ❌ 强制修改CSS会破坏页面布局
page.evaluate("""() => {
    document.querySelectorAll('[class*="pop"]').forEach(el => {
        el.style.display = 'block';  // 破坏整个页面！
    });
}""")
```

### Pitfall 15: 批量创建活动的"成功"误判

并行批量创建活动时，脚本报告"✅ 成功"可能只是按钮被点击，但活动实际未创建。

**验证方法：** 创建后检查活动列表，看新活动是否出现：
```python
activities = page.evaluate("""() => {
    const lis = document.querySelectorAll('li');
    return Array.from(lis).filter(li =>
        li.textContent.includes('目标话题')
    ).map(li => li.textContent.trim().substring(0, 100));
}""")
```

### Pitfall 14: 主题讨论表单需等15秒（不是8秒）
主题讨论弹窗的表单（`#discussTitle`）加载较慢。使用8秒等待时，textarea的`getBoundingClientRect()`返回`width=0, height=0`，Playwright的`fill()`会报"element is not visible"。

**正确做法：等待15秒**
```python
page.locator(".btnDiscuss").first.click()
time.sleep(15)  # 必须等15秒，8秒不够

# 然后用Playwright fill（不要用JS el.value，不触发数据绑定）
page.wait_for_selector("#discussTitle", state="visible", timeout=20000)
page.locator("#discussTitle").fill("讨论话题")
```

**❌ 不要用JS设置value**：`el.value = '...'` 不触发Vue/React的数据绑定，提交时话题为空。
```python
# ❌ 这样填了但提交时是空的
page.evaluate("document.getElementById('discussTitle').value = '话题'")
```

### Pitfall 15: "立即开始"按钮有10个，需精确过滤（含force_click备选）
页面上每个活动类型都有自己的"立即开始"按钮（签到、选人、抢答等），共约10个。直接click会匹配到错误的按钮。

**最佳方案：force_click_start（2026-06-08验证）**
当过滤方法找不到按钮时（所有按钮width=0），强制显示并点击：
```python
def force_click_start(page):
    result = page.evaluate("""() => {
        for (let el of document.querySelectorAll('a,button,div')) {
            if ((el.textContent||'').trim() === '立即开始') {
                el.style.display='block';
                el.style.visibility='visible';
                el.style.width='auto';
                el.style.height='auto';
                el.style.opacity='1';
                el.click();
                return 'clicked';
            }
        }
        return 'not found';
    }""")
    return result == 'clicked'
```
此方法在5个班级并行发送主题讨论时全部成功（之前过滤方法返回"未找到按钮"）。

**正确做法：过滤hideMyself class且width>0**
```python
btns = page.evaluate("""() => {
    const all = document.querySelectorAll('a');
    const result = [];
    for (let el of all) {
        if ((el.textContent||'').trim() === '立即开始' && !el.className.includes('hideMyself')) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0) {
                result.push({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
            }
        }
    }
    return result;
}""")
if btns:
    page.mouse.click(btns[-1]['x'], btns[-1]['y'])  # 点最后一个
```

**也可用JS直接click**（不经过Playwright的visibility检查）：
```python
page.evaluate("""() => {
    const all = document.querySelectorAll('a');
    for (let el of all) {
        if ((el.textContent||'').trim() === '立即开始' && !el.className.includes('hideMyself')) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0) { el.click(); return 'clicked'; }
        }
    }
    return 'not found';
}""")
```

### Pitfall 16: 主题讨论点击"立即开始"后URL不变但活动已创建
点击"立即开始"后，页面URL不变（仍在`activeList?...#`），但这**不代表失败**。弹窗关闭，活动已出现在列表中。

**验证方法**：检查活动列表是否出现新条目，而不是检查URL变化。
```python
# ❌ 错误验证
if "discuss" in page.url.lower():
    print("成功")

# ✅ 正确验证：弹窗关闭 + 活动出现在列表
# 或直接信任点击成功，不验证URL
```

### Pitfall 14: 主题讨论创建关键坑点（2026-05-31验证）

**表单加载时间**：点击 `.btnDiscuss` 后必须等 **15秒**（不是8秒），否则 `#discussTitle` textarea 仍是隐藏状态（`rect.width=0`）。

**填写话题**：用 Playwright 的 `page.locator("#discussTitle").fill(topic)` 最可靠。JS的 `el.value = '...'` 虽然能设值但不触发框架数据绑定，可能导致提交时话题为空。

**"立即开始"按钮过滤**：页面上最多有 **10个** "立即开始"按钮（每个活动类型都有自己的），必须过滤：
- 排除 `className.includes('hideMyself')` 的隐藏按钮
- 只选 `rect.width > 0 && rect.height > 0` 的可见按钮
- 用 `mouse.click(x, y)` 坐标点击，不用 `el.click()`（可能被遮挡）

**点击后URL不变**：点击"立即开始"后URL不会跳转到讨论页面，弹窗关闭、活动出现在列表中即表示成功。不要用URL变化判断成功与否。

**批量并行偶尔失败**：5个班级并行创建时，1-2个可能因表单未加载完而失败，需要单独重试。

### Pitfall 17: WPS Office无法自动化MathType Toggle TeX

尝试将Word文档中的LaTeX `$...$` 公式通过MathType的"切换TeX"功能批量转为公式对象时，发现**WPS Office的自定义UI框架无法被自动化控制**：

- **pywinauto UIA**：WPS不暴露TabItem/MenuItem等标准UI元素（返回0个元素）
- **win32com COM**：MathType的Toggle TeX命令不可用（所有变体都报-2147352567错误）
- **pyautogui坐标点击**：WPS选项卡栏使用自定义渲染，像素坐标不准确，多次点击偏移到其他功能
- **键盘导航**：全选(Ctrl+A)触发WPS的"拼音指南"弹窗（模态对话框），阻塞所有后续操作

**拼音指南弹窗**：WPS中全选中文文本会自动弹出"拼音指南"模态弹窗。可通过Windows API关闭：
```python
# 用WM_CLOSE消息关闭拼音指南弹窗
user32 = ctypes.windll.user32
def close_pinyin():
    result = []
    def callback(h, l):
        length = user32.GetWindowTextLengthW(h)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(h, buf, length + 1)
            if '拼音' in buf.value:
                result.append(h)
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(WNDENUMPROC(callback), 0)
    for h in result:
        user32.SendMessageW(h, 0x0010, 0, 0)
```

**结论**：MathType Toggle TeX是纯UI操作，只能手动执行（3步：Ctrl+A → MathType工具选项卡 → 切换TeX）。自动化此操作在WPS环境下不可行。

**替代方案**：直接生成包含Word原生公式对象(OMML)的docx文件，避免需要MathType转换。用python-docx的`m:oMath`元素插入公式。

### Pitfall 15: 自动签到（定时任务 + headless浏览器）

通过 cron job 在课前5分钟自动创建签到：
- 脚本位置：`~/.hermes/scripts/signin_12.py` / `signin_34.py` / `signin_56.py` / `signin_78.py` / `signin_910.py`
- 每个脚本内嵌SCHEDULE课表，根据当前周次+星期+时段自动判断是否有课
- 无课时输出"📭 今天没有X-X节课程，跳过签到"并静默退出
- **cron统一设为周一至周五**（`1-5`），不需要在cron层限制特定星期
- 使用 `headless=True` 的 Edge 浏览器（用户偏好Edge）
- 登录等待15秒，表单等待8-10秒

**⚠️ 创建签到的完整流程（2026-06-01修复，2026-06-08修正）：**

签到只需要**3步**（不是4步）—— 点击"普通签到"后签到自动开始，**没有"立即开始"按钮**：

```python
# 1. 点击添加活动按钮
page.click(".add-activate-icon")
time.sleep(3)

# 2. 点击"签到"活动类型 (li.btnSignIn)
page.evaluate("""() => {
    const li = document.querySelector('li.btnSignIn');
    if (li) { li.click(); return 'clicked'; }
    const els = document.querySelectorAll('li.list');
    for (const el of els) {
        if (el.textContent.includes('签到') && el.offsetParent !== null) {
            el.click(); return 'clicked2';
        }
    }
    return 'not found';
}""")
time.sleep(3)

# 3. 点击"普通签到"选项 — 点击后页面直接跳转到签到结果页，签到自动开始
page.evaluate("""() => {
    const spans = document.querySelectorAll('.pop-signin-content span, .signin-tab span, .tab-box span, span');
    for (const s of spans) {
        if (s.textContent.trim() === '普通签到' && s.offsetParent !== null) {
            s.click(); return 'clicked';
        }
    }
    return 'not found';
}""")
time.sleep(8)

# 4. ❌ 不需要点击"立即开始"！点击"普通签到"后签到已自动开始
#    页面会跳转到签到结果页，显示"已签/未签/签到率"
#    如果脚本中尝试查找"立即开始"按钮，会找不到并报告失败（误报）
```

**为什么不需要第4步**：与其他活动（选人、主题讨论、抢答）不同，签到活动点击"普通签到"后直接生效，页面跳转到签到结果页。不存在"立即开始"按钮。旧脚本尝试查找该按钮会返回"not found"并报告失败，但签到实际已创建成功。

**签到成功判断**：页面出现"已签/未签/签到率"即表示成功。

**⚠️ 签到点击"普通签到"后直接跳转结果页（2026-06-08验证）**

点击"普通签到"后，页面可能**直接跳转到签到结果页**（显示"已签/未签/签到率"），跳过了"立即开始"按钮。此时脚本找不到"立即开始"按钮会报告失败，但签到实际已创建成功。

**正确判断方式**：点击"普通签到"后等待8-10秒，检查页面是否出现"已签"或"签到率"字样：
```python
# 点击普通签到后
time.sleep(10)
page_text = page.evaluate("document.body.innerText.substring(0, 500)")
if '已签' in page_text or '签到率' in page_text:
    print('✅ 签到已创建（自动跳转到结果页）')
else:
    # 再尝试点击"立即开始"
    ...
```

**不要仅依赖"立即开始"按钮是否存在来判断签到是否成功**。签到有两种成功路径：
1. 点击"立即开始" → 成功
2. 点击"普通签到"后直接跳转到结果页 → 也是成功

### Pitfall 18: 自动签到标题输入框 placeholder 不匹配
在操作表单时，使用精确的属性选择器（name、placeholder）比通用type选择器更可靠。

**错误示例**（可能填错字段）：
```python
# type='number' 的输入框不会被 type='text' 匹配
phone_input = page.locator("input[type='text']").first  # 可能匹配到验证码框
phone_input.fill("YOUR_PHONE")  # 填错了！
```

**正确示例**（精确定位）：
```python
# 使用name属性精确定位
phone_input = page.locator("input[name='Tel']").first
phone_input.fill("YOUR_PHONE")  # 正确填入手机号框

# 或使用placeholder定位
phone_input = page.locator("input[placeholder*='手机号']").first
```

**调试技巧**：打印所有input元素的属性帮助定位：
```python
inputs = page.query_selector_all("input")
for inp in inputs:
    placeholder = inp.get_attribute("placeholder") or ""
    input_type = inp.get_attribute("type") or ""
    name = inp.get_attribute("name") or ""
    visible = inp.is_visible()
    print(f"Input: placeholder='{placeholder}', type='{input_type}', name='{name}', visible={visible}")
```

### Pitfall 9: 处理打开新标签页的链接
点击某些链接（如"信息门户"）会在新标签页打开目标页面。使用 `expect_page()` 捕获新页面：

```python
# 监听新页面
with page.context.expect_page() as new_page_info:
    portal_link.click()

new_page = new_page_info.value
new_page.wait_for_load_state("domcontentloaded", timeout=15000)
print(f"新页面URL: {new_page.url}")

# 后续操作在新页面上进行
new_page.screenshot(path="screenshot.png")
```

### Pitfall 12: 浏览器莫名关闭 — 禁止使用 with sync_playwright()（关键！）

**这是最常见的坑**：脚本跑着跑着浏览器突然消失，没有任何报错。

**根本原因**：使用了 `with sync_playwright() as p:` 上下文管理器。Python的`with`语句在以下情况自动调用`playwright.stop()`：
1. 脚本正常执行完毕（with块结束）
2. 任何异常导致with块提前退出
3. `time.sleep(30)` 结束后进入下一行

**错误写法（所有旧脚本都有这个问题）：**
```python
# ❌ 脚本结束或异常时，浏览器自动被杀
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=False)
    page = browser.new_page()
    # ... 操作 ...
    time.sleep(30)
    browser.close()  # 这行是多余的，with退出时已经关了
```

**正确写法：**
```python
# ✅ 浏览器保持打开，不会被自动关闭
p = sync_playwright().start()
browser = p.chromium.launch(channel="msedge", headless=False)
page = browser.new_page()
# ... 操作 ...
# 不加 browser.close()，保持浏览器打开
# 如果需要等待用户手动关闭浏览器：
try:
    while True:
        time.sleep(1)
        try:
            page.title()  # 浏览器关闭后会抛异常
        except:
            break
except KeyboardInterrupt:
    pass
p.stop()
```

**三条规则：**
1. 用 `p = sync_playwright().start()` 代替 `with sync_playwright() as p:`
2. 不要加 `browser.close()`
3. 用 `channel="msedge"` 不用 `"chrome"`

### Pitfall 13: 保持浏览器打开（不自动关闭）
用户偏好浏览器打开后保持运行，不自动关闭。不要使用 `time.sleep(60)` 然后 `browser.close()`。

**推荐模式：等待用户手动关闭浏览器**
```python
from playwright.sync_api import sync_playwright
import time

p = sync_playwright().start()
browser = p.chromium.launch(channel="msedge", headless=False)
page = browser.new_page()
page.goto("https://zhcx.scitc.edu.cn/", wait_until="domcontentloaded", timeout=60000)
time.sleep(5)

print("✅ 浏览器已打开，您可以手动关闭浏览器窗口")

# 等待浏览器被手动关闭
try:
    while True:
        time.sleep(1)
        try:
            page.title()  # 如果浏览器已关闭会抛出异常
        except:
            print("浏览器已关闭")
            break
except KeyboardInterrupt:
    print("脚本被中断")

p.stop()
```

> ⚠️ **不要** 反复启动新的浏览器实例打开同一个网站。用户明确表示"不要循环打开"——打开一次即可，保持运行直到手动关闭。

### Pitfall 11: Edge浏览器的两种启动方式
Playwright启动Edge有两种方式，效果相同（Edge基于Chromium，页面底部仍显示"chrome-148"）：

**方式1：channel参数（推荐，简洁）**
```python
browser = p.chromium.launch(channel="msedge", headless=False)
```

**方式2：executable_path参数（更明确）**
```python
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
browser = p.chromium.launch(executable_path=edge_path, headless=False)
```

> ⚠️ **注意**：无论使用哪种方式，页面底部的浏览器信息都会显示"chrome-xxx"（Chromium内核版本号），这是正常的——Edge基于Chromium，Playwright将其识别为Chrome。实际使用的是Edge的可执行文件。

### Pitfall 10: 主题讨论表单加载需要15秒
创建主题讨论时，点击`.btnDiscuss`后，`#discussTitle` textarea 需要 **10-15秒** 才会变为可见状态。用8秒等待会导致 textarea `element is not visible` 错误。

**错误表现**：`#discussTitle` 存在于DOM中但 `getBoundingClientRect().width === 0`，Playwright `fill()` 报 `element is not visible`。

**正确做法**：
```python
page.locator(".btnDiscuss").first.click()
time.sleep(15)  # 必须等15秒！不是8秒

# 然后用 Playwright fill（不要用 JS el.value = ... ，JS设置值不触发框架的数据绑定）
page.locator("#discussTitle").fill("讨论话题")
time.sleep(2)
```

**为什么不用 JS fill**：学习通使用前端框架，`el.value = 'xxx'` + `dispatchEvent('input')` 虽然设置了值，但框架可能不识别，导致提交时话题为空。必须用 Playwright 的 `fill()` 方法。

**批量创建时的重试策略**：5个班级并行创建时，偶尔有1-2个班级因表单加载时间不一致而失败。建议：
1. 第一轮并行创建
2. 检查结果，对失败的班级单独重试
3. 单独重试时用更长的等待时间（15-20秒）

### Pitfall 11: 链接href为None的处理
页面上某些链接（特别是底部快捷入口）的href属性可能为None，但点击后仍能正常跳转。处理方法：
1. 先尝试获取href，如果为None则直接点击
2. 使用expect_page()捕获新打开的页面
3. 从新页面的URL获取真实地址

```python
link = page.locator("a:has-text('信息门户')").first
href = link.get_attribute("href")
if href and href != "None":
    page.goto(href)
else:
    with page.context.expect_page() as new_page_info:
        link.click()
    new_page = new_page_info.value
    new_page.wait_for_load_state("domcontentloaded")
    print(f"真实URL: {new_page.url}")
```

### Pitfall 8: 批量多班级并行执行
当需要在多个班级同时创建活动时，使用Python `threading` 并行执行，每个线程独立启动浏览器实例。

**关键要点：**
- 每个线程使用独立的 `sync_playwright()` 实例和浏览器
- 启动线程时错开2-3秒（`time.sleep(3)`），避免同时登录导致冲突
- 使用共享的 `results` 字典收集各线程执行结果
- 每个线程独立登录（不共享session），因为每个浏览器实例是独立的
- 重试单个班级时不需要并行，直接顺序执行即可

### Pitfall 9: 主题讨论话题输入框不可见
创建主题讨论时，`textarea#discussTitle` 可能因页面动画/加载延迟而 `is_visible()=false`，导致 `page.locator(...).fill()` 超时（`element is not visible`）。

**解决**：等待8秒让表单完全加载，然后用JS直接设置值，绕过Playwright的visibility检查：
```python
time.sleep(8)
page.evaluate(f"""() => {{
    const el = document.getElementById('discussTitle');
    if (el) {{
        el.style.display = 'block';
        el.style.visibility = 'visible';
        el.value = '{TOPIC}';
        el.dispatchEvent(new Event('input', {{bubbles: true}}));
        return 'filled';
    }}
    return 'not found';
}}""")
```

**注意**：对于学习通弹窗表单，`fill()` 比 `evaluate()` 更容易受visibility影响，优先用JS `evaluate()` 填写。

**批量执行模板：**
```python
import threading
from playwright.sync_api import sync_playwright

CLASSES = [
    {"name": "示例班级A", "classId": "100000001"},
    {"name": "示例班级B", "classId": "100000002"},
    # ... 更多班级
]

def create_activity_for_class(class_info, results):
    class_name = class_info["name"]
    class_id = class_info["classId"]
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="msedge", headless=False)
        # ... 登录、导航、创建活动 ...
        # 使用 click_start_button() 点击立即开始
        results[class_name] = "成功"
        # 不加 browser.close()
        p.stop()
    except Exception as e:
        results[class_name] = f"错误: {e}"

# 并行执行
results = {}
threads = []
for class_info in CLASSES:
    t = threading.Thread(target=create_activity_for_class, args=(class_info, results))
    threads.append(t)

for t in threads:
    t.start()
    time.sleep(3)  # 错开启动

for t in threads:
    t.join()

# 打印结果
for name, result in results.items():
    print(f"  {'✅' if result == '成功' else '❌'} {name}: {result}")
```

**性能参考：** 5个班级并行创建选人活动，总耗时约78秒（含登录等待时间）。

## 最佳实践

### 批量操作多个班级（推荐使用并行执行）
当需要在多个班级执行相同操作时（如5个班级都创建同一个签到活动）：

**推荐方法：使用 `references/batch-parallel-activity.py` 模板**
1. 修改 `CLASSES` 列表为你的班级
2. 修改 `COURSE_PARAMS` 为课程参数
3. 修改 `activity_type` 为需要的活动类型
4. 运行脚本，5个班级并行执行，总耗时约78秒

**关键要点：**
- 使用 `threading` 并行执行，每个线程独立浏览器实例
- 启动线程时错开3秒，避免同时登录冲突
- 使用 `click_start_button()` 函数点击"立即开始"（Pitfall 7）
- 每个班级操作完成后自动截图保存

**备选方法：顺序执行**（较慢但更稳定）
1. 先准备好班级URL列表（见上方班级配置）
2. 创建一个循环脚本，依次导航到每个班级的活动列表
3. 对每个班级执行相同的活动创建操作
4. 每个班级操作完成后截图确认

### 保存课程信息到本地文件
当用户有多个班级时，建议将课程信息保存到本地文件（如 `高等数学课程班级信息.txt`），包含：
- 课程公共参数（courseId, cpi, enc, fid）
- 所有班级的classId和活动列表URL
- 活动类型CSS选择器汇总
- 已创建的活动示例

**文件夹组织建议**（基于实际使用经验）：
```
项目文件夹/
├── screenshots/     # 操作截图
├── scripts/         # Playwright脚本
│   └── 脚本索引.txt # 脚本功能说明
├── data/            # 数据文件（班级信息等）
├── media/           # 媒体文件（图片、动图）
└── README.md        # 文件夹说明文档
```

这样可以快速参考，无需每次都从记忆中查找。用户偏好将结构化数据存入文件而非依赖记忆空间。

### Pitfall 14: 主题讨论表单加载慢（关键！）

创建主题讨论时，点击 `.btnDiscuss` 后 **必须等待 10-15 秒** 让表单完全加载。之前等 5-8 秒导致：
- `#discussTitle` textarea 为 hidden 状态，`fill()` 失败
- "立即开始"按钮 `width=0`，无法用 `mouse.click` 点击

**症状**：脚本报告"话题已填写"和"点击成功"，但活动列表中没有新活动。

**修复**：
```python
# 点击主题讨论后，必须等够
time.sleep(15)  # 不能少于 10 秒

# 用 Playwright fill（备选 JS fallback）
try:
    page.wait_for_selector("#discussTitle", state="visible", timeout=15000)
    page.locator("#discussTitle").fill("话题内容")
except:
    page.evaluate("""() => {
        const el = document.getElementById('discussTitle');
        if (el) { el.value = '话题内容'; el.dispatchEvent(new Event('input', {bubbles:true})); }
    }""")
```

**注意**：点击"立即开始"后 **URL 不会变化**（仍为 `activeList#`），但活动已创建成功。不要用 URL 变化判断成功与否。

### Pitfall 15: 检测活动是否创建成功

点击"立即开始"后页面 URL 不会变化（仍为 `activeList#`），但活动可能已创建成功。

**正确判断方式**：等待 5 秒后重新加载活动列表，检查新活动是否出现。
```python
# ❌ 错误：URL 没变化 ≠ 失败
if "discuss" in page.url.lower():
    print("成功")

# ✅ 正确：重新加载列表检查
time.sleep(5)
page.reload()
time.sleep(5)
has_activity = page.evaluate("""() => {
    return document.body.innerText.includes('你的活动标题');
}""")
```

### Pitfall 18: 签到活动没有"立即开始"按钮（2026-06-08验证）

签到活动的流程与其他活动不同：点击"普通签到"后**签到自动开始**，页面直接跳转到签到结果页。不存在标题输入框或"立即开始"按钮。

- **不需要填写标题**（签到备注是可选的，且在自动开始后无法修改）
- **不需要点击"立即开始"**（按钮根本不存在）
- **判断成功**：页面出现"已签/未签/签到率"即表示成功
- **旧脚本误报**：如果脚本尝试查找"立即开始"按钮，会返回"not found"并报告失败，但签到实际已创建成功。应改用页面内容判断。

### Pitfall 19: 签到页面已存在时重复创建

如果当前页面已在签到结果页（显示"已签/未签/签到率"），再运行创建签到脚本会失败，因为页面不是活动列表。

**解决**：创建签到前先检查当前页面状态，如果已在签到结果页，先导航回活动列表：
```python
current_text = page.evaluate("document.body.innerText.substring(0, 200)")
if '已签' in current_text or '未签' in current_text:
    page.goto(activity_list_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
```

**注意**：签到活动点击"普通签到"后自动开始（不需要"立即开始"），页面直接跳转到结果页。如果脚本在结果页上尝试创建新签到，会因为找不到`.add-activate-icon`而失败。

### Pitfall 24: 活动类型选择器误点已有活动（2026-06-01验证）

创建活动时，如果用 `li.list` 匹配文本（如 `"主题讨论"`），会同时匹配到：
1. **活动类型选择器**中的"主题讨论"按钮（`li.btnDiscuss`）— 正确目标
2. **活动列表中已有的**主题讨论活动条目（如"测试主题讨论：xxx 开始时间：..."）— 错误目标

**症状**：脚本报告"点击成功"，但实际上点击的是已有的活动条目，不是创建新活动的按钮。签到创建了但主题讨论没创建。

**根本原因**：活动列表中的每个已有活动也是 `li.list` 元素，文本中包含活动类型名。

**解决方案：使用精确的class选择器，不要用文本匹配**：
```python
# ❌ 错误：会匹配到已有活动
page.evaluate("""() => {
    const els = document.querySelectorAll('.btnDiscuss, li.list');
    for (let el of els) {
        if (el.textContent && el.textContent.includes('主题讨论') && el.offsetParent !== null) {
            el.click(); return;
        }
    }
}""")

# ✅ 正确：只匹配活动类型按钮
page.evaluate("""() => {
    const btn = document.querySelector('li.btnDiscuss');
    if (btn && btn.offsetParent !== null) {
        btn.click();
        return 'clicked';
    }
    return 'not found';
}""")
```

**各活动类型的精确选择器**：
| 活动类型 | 精确选择器 |
|---------|-----------|
| 签到 | `li.btnSignIn` |
| 选人 | `li.btnSelectPerson` |
| 主题讨论 | `li.btnDiscuss` |
| 抢答 | `li.btnQuickAnswer` |
| 随堂练习 | `li.btnTest` |

**验证方法**：点击后打印目标元素的文本，确认是"主题讨论"而不是"测试主题讨论：xxx 开始时间：..."。

### Pitfall 25: 每个步骤后必须关闭弹窗（2026-06-01验证）

创建活动的每个步骤后都需要关闭弹窗，否则弹窗会遮挡后续操作：

```python
def close_popups(page):
    """关闭所有弹窗 — 每个步骤后调用"""
    page.evaluate("""() => {
        const popups = document.querySelectorAll('.popDiv, .maskDiv, .popBottom, .pick-container, .popPermission, .popMove, .popCellShowHide');
        for (let el of popups) {
            el.style.display = 'none';
        }
    }""")
    time.sleep(1)

# 正确流程：
close_popups(page)           # 1. 进入活动列表后
page.click('.add-activate-icon')
time.sleep(3)
close_popups(page)           # 2. 点击添加按钮后
# 点击活动类型（如 li.btnDiscuss）
time.sleep(8)
close_popups(page)           # 3. 点击活动类型后
# 填写话题/事由
close_popups(page)           # 4. 填写内容后
# 点击立即开始
```

**不关闭弹窗的后果**：
- 弹窗遮挡"立即开始"按钮，导致 width=0
- 表单元素被遮挡，fill() 超时
- 点击穿透到弹窗下面的元素

### Pitfall 20: 弹窗遮挡导致"立即开始"按钮width=0（2026-06-01验证）

创建活动时，页面上可能有**多个隐藏弹窗**覆盖在"立即开始"按钮上方，导致：
- 按钮的 `getBoundingClientRect().width === 0`
- `mouse.click` 点击无效
- 脚本报告"未找到立即开始按钮"

**常见弹窗来源**：
- 权限设置弹窗（`.popDiv.popPermission`）
- 通讯录弹窗（`.pick-container`）
- 确认弹窗（`.popBottom`）
- 遮罩层（`.maskDiv`）

**症状**：调试时发现页面上有大量"确定"/"取消"按钮（width=0），以及权限设置内容（教师姓名列表）。

**解决方案：关闭弹窗 + 强制显示 + JS点击**：
```python
def close_popups(page):
    """关闭所有弹窗"""
    page.evaluate("""() => {
        const popups = document.querySelectorAll('.popDiv, .maskDiv, .popBottom, .pick-container');
        for (let el of popups) {
            el.style.display = 'none';
        }
        const cancelBtns = document.querySelectorAll('a, button, div');
        for (let el of cancelBtns) {
            if ((el.textContent||'').trim() === '取消') {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0) { el.click(); }
            }
        }
    }""")
    time.sleep(1)

# 在点击"立即开始"前调用
close_popups(page)

# 强制显示并点击按钮
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

# 检查是否有确认弹窗
if result == 'clicked':
    time.sleep(3)
    page.evaluate("""() => {
        const all = document.querySelectorAll('a, button, div');
        for (let el of all) {
            const text = (el.textContent||'').trim();
            if (text === '确定' || text === '确认') {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0) { el.click(); return; }
            }
        }
    }""")
```

**⚠️ 注意**：强制修改CSS（`el.style.display = 'block'`）只用于目标按钮，不要对所有弹窗都强制显示，否则会破坏页面布局。

### Pitfall 21: 获取课程全部班级列表

获取课程所有班级的API（无需手动遍历）：
```python
result = page.evaluate("""async () => {
    const resp = await fetch('/v2/apis/class/getClassList?courseId=200000001&isHaveAuth=1&isfiled=');
    return await resp.json();
}""")
# result['data'] = [{name, id, studentcount, ...}, ...]
```

⚠️ 注意区分课程：**示例考试班**（classId=100000007）属于**高等数学（进阶）**（courseId=200000002），不在经济数学（courseId=200000001）中。详见 `references/class-list-api.md`。

## 自动签到定时任务

已设置5个cron定时任务，上课前5分钟自动创建签到（headless Edge + Playwright）。全部周一至周五触发，脚本内嵌SCHEDULE课表自动过滤无课日。

| 节次 | 签到时间 | 选人r1 | 选人r2 | 脚本 |
|------|---------|--------|--------|------|
| 1-2节 | 08:45 | 09:05 | 10:05 | `signin_12.py` / `sp_12_1_r1.py` / `sp_12_1_r2.py` |
| 3-4节 | 10:25 | 10:45 | 11:45 | `signin_34.py` / `sp_34_1_r1.py` / `sp_34_1_r2.py` |
| 5-6节 | 13:55 | 14:15 | 15:15 | `signin_56.py` / `sp_56_1_r1.py` / `sp_56_1_r2.py` |
| 7-8节 | 15:45 | 16:05 | 17:05 | `signin_78.py` / `sp_78_1_r1.py` / `sp_78_1_r2.py` |
| 9-10节 | 18:55 | 19:15 | 20:05 | `signin_910.py` / `sp_910_2_r1.py` / `sp_910_2_r2.py` |

主题讨论：每天10:30（全部5个班，无课表过滤，`auto_discussion.py`）

**⚠️ 选人cron去重**：原有按星期命名的26个选人cron（如sp_34_1_r1~sp_34_5_r1），扩展为每天触发后同一时段多个cron会同时触发。每个时段只保留1个r1+1个r2，其余暂停。

主脚本 `~/.hermes/scripts/auto_signin.py` 接受节次参数（如 `python auto_signin.py 1-2`），根据周几+教学周判断哪些班级有课，自动创建签到。结果发送到微信。

**注意**：教室可能每周不同（如周三3-4节示例班级C，16周在0401，其他周在0302）。脚本中用多个SCHEDULE条目+不同周次范围处理。详见 `references/schedule-sync-workflow.md`。

自动签到脚本位置：
- 主脚本：`~/.hermes/scripts/auto_signin.py`（接受命令行参数，如 `auto_signin.py 1-2`）
- 节次包装：`~/.hermes/scripts/signin_12.py`、`signin_34.py`、`signin_56.py`、`signin_78.py`、`signin_910.py`、`signin_910.py`

## Pitfall 22: 不要批量删除所有cron任务

用户说"停止所有任务"或类似模糊指令时，**不要直接删除所有cron job**。用户通常只针对某个具体问题（如某个班级的主题讨论发送失败），而非真的要删除全部定时任务。

**⚠️ 用户明确要求：删除全部任务前必须先确认！**

**正确做法**：
1. 先 `cronjob list` 查看当前任务
2. 用 `clarify` 确认用户要停止哪些具体任务
3. 只删除/暂停用户确认的任务
4. **删除全部任务前，必须找用户确认后再执行**

**错误示范**：用户说"停止所有任务"→ 删除12个cron job → 用户说"我说的是XX问题，回滚那些任务" → 需要重新创建全部任务，浪费时间和API调用。

## Pitfall 23: Cron Job创建需要prompt参数

使用 `cronjob create` 时，如果 `no_agent` 不是 `true`，则 `prompt` 参数是**必需的**。只提供 `script` 和 `name` 会报错 `"create requires either prompt or at least one skill"`。

**正确做法**：
```python
# ✅ 有script但无no_agent时，必须加prompt
cronjob create, name="xxx", script="xxx.py", prompt="运行xxx脚本"

# ✅ 或者设置no_agent=true（纯脚本模式，不需要prompt）
cronjob create, name="xxx", script="xxx.py", no_agent=true
```

**错误示范**：只提供name和script → 创建失败 → 需要重试。

## Pitfall 22: 不要批量删除所有cron任务

用户说"停止所有任务"或类似模糊指令时，**不要直接删除所有cron job**。用户通常只针对某个具体问题（如某个班级的主题讨论发送失败），而非真的要删除全部定时任务。

**正确做法**：
1. 先 `cronjob list` 查看当前任务
2. 用 `clarify` 确认用户要停止哪些具体任务
3. 只删除/暂停用户确认的任务

## Pitfall 23: Cron Job创建需要prompt参数

使用 `cronjob create` 时，`prompt` 参数是**必需的**（除非设置 `no_agent=true`）。只提供 `script` 和 `name` 会报错。

## Pitfall 29: Cron `no_agent=true` 的live adapter投递问题（2026-06-09 关键发现）

**根本原因**：`no_agent=true` 的cron任务**脚本确实会执行**，但其stdout通过"live adapter"投递到微信时**静默失败**。

**症状**：
- `agent.log` 显示 `Job 'xxx': delivered to weixin:... via live adapter`（看起来成功了）
- `gateway.log` 中**没有任何对应的发送记录**（消息从未到达网关）
- 用户**收不到任何消息**
- `last_status` 可能是 `"error"` 也可能显示成功，但消息就是没到

**诊断方法**：
```bash
# 1. 检查agent.log中的投递记录
grep "delivered to.*via live adapter" ~/AppData/Local/hermes/logs/agent.log

# 2. 检查gateway.log中是否有对应的发送记录（应该有但可能没有）
grep "18:50\|18:55" ~/AppData/Local/hermes/logs/gateway.log

# 3. 如果agent.log有投递但gateway.log没有 → live adapter投递失败
```

**✅ 解决方案：使用 `no_agent=false`（agent模式）**：
```bash
# ❌ 不可靠：no_agent模式的live adapter投递静默失败
cronjob create name="签到-xxx" no_agent=true \
  script="cd /c/Users/Administrator/AppData/Local/hermes/scripts && python signin_generic.py 100000002 示例班级B" \
  schedule="once at 2026-06-09 15:45"

# ✅ 可靠：agent模式，脚本通过agent的正常gateway通道发送
cronjob create name="示例班级B-签到" no_agent=false \
  prompt="请立即执行以下命令为示例班级B创建签到活动：\ncd ~/AppData/Local/hermes/scripts && python signin_generic.py 100000002 示例班级B\n\n执行完成后，报告签到结果。" \
  schedule="once at 2026-06-09 15:45"
```

**agent模式为什么可靠**：
- cron触发时启动完整agent会话
- agent通过terminal工具执行脚本
- 脚本结果通过agent的send_message直接发送到微信（不经过live adapter）
- 2026-06-09 19:05 测试验证：示例考试班签到任务通过agent模式成功执行并投递

**用户的明确要求**："后续所有任务都使用固定技能发放" — 即用agent模式cron（no_agent=false），在prompt中指示agent调用terminal执行通用脚本。

## Pitfall 27: Cron `last_status: "error"` ≠ 脚本执行失败（2026-06-09 关键发现）

cronjob list 中的 `last_status: "error"` **不代表脚本执行失败**，可能是消息投递（delivery）失败。

**真实案例**：主题讨论脚本 `auto_discussion_daily.py` 通过cron执行，5个班级全部发送成功（进度文件确认 `1/26`），但 `last_status: "error"`。原因是WeChat消息投递被限速。

**诊断方法**（按优先级）：
1. **检查脚本副作用** — 进度文件、活动列表、数据库变更等，确认脚本是否真正执行
2. **查看 `gateway.log`** — 搜索 `send failed` 或 `rate limited` 确认投递错误
3. **查看 `errors.log`** — 搜索 job_id 确认具体错误信息
4. **查看 `agent.log`** — 搜索 job_id 查看完整执行链路

**常见投递错误**：
- `iLink sendmessage rate limited; cooldown active for 30.0s` — 微信消息发送频率过高，被限速30秒
- `delivery error: Weixin send failed` — 微信投递失败（通常与限速相关）

**根因**：短时间内手动发送多条消息（如确认签到结果、手动通知等）触发了微信的速率限制。后续cron任务尝试投递结果时被拦截。

**解决方案**：
1. 等待限速冷却期过后，后续任务会自动恢复正常
2. 不要频繁手动发送消息（间隔至少30秒）
3. 脚本本身添加本地日志记录，不依赖微信回报确认成功
4. 在脚本中用 `print()` 输出结果，cron的stdout会被记录到日志
5. **使用agent模式cron**（Pitfall 29）— agent会话有独立的消息通道，不受限速影响

**验证脚本是否成功的方法**：
```bash
# 1. 检查进度文件（主题讨论）
cat ~/BaiduSyncdisk/龙虾文件/教学资料/discussion_progress.json

# 2. 检查脚本是否在正确路径
ls ~/AppData/Local/hermes/scripts/signin_generic.py

# 3. 手动运行脚本确认功能正常
cd ~/AppData/Local/hermes/scripts && python -u signin_generic.py 100000004 示例班级D

# 4. 查看gateway日志中的投递错误
grep "rate limited\|send failed" ~/AppData/Local/hermes/logs/gateway.log
```

## Pitfall 28: Cron脚本路径必须用Hermes home（2026-06-09 关键发现）

**Windows上Hermes home不是 `~/.hermes/`**，而是 `~/AppData/Local/hermes/`。

cron任务中的脚本路径必须使用正确的Hermes home：

```bash
# ❌ 错误：~/.hermes/ 不存在或不是Hermes home
cd ~/.hermes/scripts && python signin_generic.py

# ✅ 正确：使用 ~/AppData/Local/hermes/scripts/
cd ~/AppData/Local/hermes/scripts && python signin_generic.py 100000004 示例班级D
```

**验证Hermes home位置**：
```bash
# 检查脚本文件是否存在
ls ~/AppData/Local/hermes/scripts/signin_generic.py
```

**症状**：cron任务 `next_run_at: null` 且 `last_run_at: null`，说明任务可能因为路径问题无法执行。

**相关日志位置**：
- 执行日志：`~/AppData/Local/hermes/logs/agent.log`
- 错误日志：`~/AppData/Local/hermes/logs/errors.log`
- 网关日志：`~/AppData/Local/hermes/logs/gateway.log`

### Pitfall 26: 更新进度文件用write_file而非Python命令

`execute_code` 或 `terminal` 中运行 Python 命令更新 JSON 文件时，可能被用户消息中断（exit code 130）或超时阻塞。

**可靠方案**：用 `write_file` 工具直接写入完整 JSON 文件内容。先 `read_file` 读取当前内容，修改后用 `write_file` 写回。

```python
# ❌ 不可靠：Python命令可能被阻塞
terminal("python -c \"import json; ...\"")

# ✅ 可靠：用write_file直接写入
read_file("discussion_progress.json")  # 读取
write_file("discussion_progress.json", new_content)  # 写回
```

### Pitfall 30: WeChat消息限速导致cron投递失败（2026-06-09 发现）

**症状**：cron任务 `last_status: "error"`，但脚本实际执行成功（进度文件确认、活动列表有新活动）。

**根因**：WeChat iLink API有速率限制（约30秒冷却期）。短时间内发送多条消息（手动确认+自动投递）会触发限速，后续cron投递被拦截：
```
[Weixin] send failed: iLink sendmessage rate limited; cooldown active for 30.0s
```

**影响**：
- cron任务显示"error"但脚本已成功执行
- 用户看不到执行结果，误以为任务失败
- 后续任务也可能被限速影响

**解决方案**：
1. **不要频繁手动发送消息**——间隔至少30秒
2. **脚本添加本地日志**——不依赖微信回报确认成功
3. **检查脚本副作用**——进度文件、活动列表等，确认脚本是否真正执行
4. **查看gateway.log**——搜索 `rate limited` 确认是否为限速问题
5. **等待冷却期过后**——后续任务会自动恢复正常
6. **使用agent模式cron**（Pitfall 29）— agent会话有独立的消息通道，不受限速影响

**验证脚本是否成功**：
```bash
# 检查进度文件
cat ~/BaiduSyncdisk/龙虾文件/教学资料/discussion_progress.json
# 手动运行确认
cd ~/AppData/Local/hermes/scripts && python -u signin_generic.py 100000004 示例班级D
```

## Pitfall 31: Cron脚本路径格式（2026-06-09 验证）

cron任务中的脚本路径必须使用MSYS绝对路径格式：

```bash
# ✅ 正确：MSYS绝对路径
cd /c/Users/Administrator/AppData/Local/hermes/scripts && python signin_generic.py 100000002 示例班级B

# ❌ 错误：~ 可能不展开
cd ~/AppData/Local/hermes/scripts && python signin_generic.py

# ❌ 错误：Windows路径格式在bash中不工作
cd C:\Users\Administrator\AppData\Local\hermes\scripts && python signin_generic.py
```

**注意**：即使路径正确，`no_agent=true` 的投递仍可能失败（见Pitfall 29）。推荐使用 `no_agent=false`。

## Pitfall 32: 每节课需要4-5个独立cron任务（2026-06-09 标准化，2026-06-11 更新）

**任务结构**（以3-4节为例）：
| 时间 | 任务类型 | 脚本 |
|------|----------|------|
| 上课前10分钟 | 📢 提醒 | `echo "📢 班级名 第X-X节 课程名 教室XXX 马上上课！"` |
| 上课前5分钟 | ✍️ 签到 | `cd /c/Users/Administrator/AppData/Local/hermes/scripts && python signin_generic.py <classId> <班级名>` |
| 上课后10分钟 | 👤 选人-上课后 | `cd /c/Users/Administrator/AppData/Local/hermes/scripts && python select_student_generic.py <classId> <班级名>` |
| 课堂中间（约一半时间） | 🎯 抢答 | `cd /c/Users/Administrator/AppData/Local/hermes/scripts && python quick_answer_generic.py <classId> <班级名>` |
| 下课前10分钟 | 👤 选人-下课前 | `cd /c/Users/Administrator/AppData/Local/hermes/scripts && python select_student_generic.py <classId> <班级名>` |

**⚠️ 用户可能要求"选人"改为"抢答"**：用户有时会说错活动类型（如说"选人"实际想要"抢答"），创建前建议确认。

**各节次时间参考**（含课堂中间抢答时间）：
| 节次 | 上课时间 | 提醒 | 签到 | 选人-上课后 | 抢答 | 选人-下课前 |
|------|----------|------|------|------------|------|------------|
| 1-2节 | 08:50 | 08:40 | 08:45 | 09:00 | 09:35 | 10:10 |
| 3-4节 | 10:30 | 10:20 | 10:25 | 10:40 | 11:15 | 11:50 |
| 5-6节 | 14:00 | 13:50 | 13:55 | 14:10 | 14:45 | 15:20 |
| 7-8节 | 15:50 | 15:40 | 15:45 | 16:00 | 16:35 | 17:10 |
| 9-10节 | 19:00 | 18:50 | 18:55 | 19:10 | 19:45 | 20:20 |

**创建示例**（agent模式，no_agent=false）：
```bash
# 提醒
cronjob create name="示例班级C-3-4-提醒" schedule="2026-06-10T10:20:00" \
  prompt='请发送提醒消息："📢 示例班级C 第3-4节 高等数学2 教室0302 马上上课！"'

# 签到
cronjob create name="示例班级C-3-4-签到" schedule="2026-06-10T10:25:00" \
  prompt="请立即执行以下命令为示例班级C创建签到活动：\ncd ~/AppData/Local/hermes/scripts && python signin_generic.py 100000003 示例班级C\n\n执行完成后，报告签到结果。"

# 选人-上课后
cronjob create name="示例班级C-3-4-选人上课后" schedule="2026-06-10T10:40:00" \
  prompt="请立即执行以下命令为示例班级C创建上课后选人活动：\ncd ~/AppData/Local/hermes/scripts && python select_student_generic.py 100000003 示例班级C\n\n执行完成后，报告选人结果。"

# 选人-下课前
cronjob create name="示例班级C-3-4-选人下课前" schedule="2026-06-10T11:50:00" \
  prompt="请立即执行以下命令为示例班级C创建下课前选人活动：\ncd ~/AppData/Local/hermes/scripts && python select_student_generic.py 100000003 示例班级C\n\n执行完成后，报告选人结果。"
```

## 课表管理

### 脚本结构
- `class_reminder.py` - 课前提醒（SCHEDULE数组按周次区分）
- `auto_signin.py` - 自动签到（接受节次参数）
- `auto_discussion.py` - 主题讨论自动发送（进度跟踪）

### 课表更新流程
1. 从教务系统查询最新课表（通过session_search查找历史查询结果）
2. 更新 class_reminder.py 和 auto_signin.py 的 SCHEDULE 数组
3. 根据课表调整 cron 任务的执行日期

### SCHEDULE数组格式
```python
# class_reminder.py: (weekday, 'jie', 'class_name', 'room', 'time', 'week_range')
# auto_signin.py: (weekday, 'jie', 'class_id', 'class_name', 'week_range')
# week_range: '14-18' 表示第14到18周
```

详见 `chaoxing-course-automation` skill。

## 常见问题

### Q: 找不到班级列表
A: 检查iframe是否加载完成，尝试刷新页面或重新进入班级活动

### Q: 点击按钮无反应
A: 可能元素被遮挡，先调用`scrollIntoView()`，或使用Playwright的click方法

### Q: 参数如何获取
A: 从课程主页URL中提取courseId、clazzid、cpi；从班级活动页面URL中提取enc、fid

### Q: 登录一直失败
A: 可能原因：密码错误、需要验证码、账号锁定。建议先手动登录确认账号状态。

### Q: 添加活动按钮点击无效
A: 使用JavaScript点击：`document.querySelector('.add-activate-icon').click()`

### Q: 点击课程卡片后没有跳转
A: 课程卡片在iframe中，直接点击可能无效。使用方式B（提取URL直接导航）更可靠。

### Q: 隐私政策复选框找不到
A: 当前学习通登录页面没有隐私政策复选框，无需勾选任何复选框。

## 已知课程参数

```yaml
# 四川信息职业技术学院 - 李盘润账号
账号: YOUR_PHONE
学校: 四川信息职业技术学院

# 经济数学课程（第11次开课）
courseId: 200000001
clazzid: 100000006
cpi: 300000001
fid: YOUR_FID
enc: "YOUR_ENC"

# 班级配置（5个班级）
classes:
  - name: "示例班级A"
    classId: 100000001
    studentCount: 46
  - name: "示例班级B"
    classId: 100000002
    studentCount: 46
  - name: "示例班级C"
    classId: 100000003
  - name: "示例班级D"
    classId: 100000004
  - name: "示例班级E"
    classId: 100000005

# 高等数学（进阶）— cpi和enc与经济数学不同！
courseId: 200000002
clazzid: 100000007  # 示例考试班
cpi: 300000002  # 注意：不是300000001（那是经济数学的cpi）
enc: "YOUR_ENC"  # 示例考试班classEnc
courseEnc: "4E4DAA868184A5D37E55FA8C70F5978B"
课程页面enc: "18ffaf76d71653b36e1345ed68a53d77"
作业openc: "d05c8342cfd569d27cf863a31a130ce3"
教师: 伍星
```

## 主题讨论创建要点（2026-05-31验证）

**⚠️ 主题讨论生成方法适用于所有课程和班级**
经济数学5个班（示例班级A/2、示例班级C、示例班级D/2）和高等数学进阶示例考试班使用相同的方法生成主题讨论，只是courseId、cpi、enc等参数不同。

1. **表单加载**：点击 `.btnDiscuss` 后等 **15秒**（低于15秒 textarea 不可见）
2. **填写话题**：用 `page.locator("#discussTitle").fill(topic)`（JS赋值不触发数据绑定）
3. **按钮过滤**：页面10个"立即开始"，排除 `hideMyself` class 且 `width>0`
4. **成功判断**：URL不变但弹窗关闭、活动出现在列表中
5. **批量并行**：5班并行偶尔1-2个失败，需单独重试

**批量定时发送（带进度跟踪）**：当需要为多班级发送大量主题讨论（如26个话题×5班），使用带进度跟踪的自动发送脚本，每天发送1个话题，cron定时执行（26天完成）。详见 `references/batch-discussion-with-progress.md`。

**⚠️ 用户偏好：主题讨论话题要求**
- **格式**：一句话精简描述，不要冗长的问题背景描述（用户明确要求"具体一些主题讨论就改成一句话"）
- **内容**：与学生日常生活相关（生活费、跑步、游戏、外卖、手机电量、咖啡因、兼职收入等），不要抽象的工程/金融场景
- **数量**：每天1个话题（5班同时发送），26天完成（不是每天2个13天完成）
- **脚本位置**：`~/.hermes/scripts/auto_discussion.py` + `D:\BaiduSyncdisk\龙虾文件\scripts\auto_discussion.py`
- **进度文件**：`D:\BaiduSyncdisk\龙虾文件\教学资料\discussion_progress.json`

**话题生成模板示例（学生生活版）**：
```
不定积分概念: "你每月生活费1500元，每天花销速度为v(t)=50-0.5t（元/天），请用不定积分推导出第t天花完后的总花销函数。"
直接积分法: "你打游戏升级，经验增长率为f(x)=100+5x（点/小时），请用直接积分法求出x小时后的总经验值函数。"
第一类换元法: "手机电量消耗率P(t)=2t·e^(-t²)，请用第一类换元积分法求0到t时刻的总消耗量。"
分部积分法: "你的兼职收入函数为R(t)=t·e^(0.05t)（元/月），请用分部积分法计算半年的总收入。"
定积分性质: "食堂客流量率为f(t)=100+80sin(πt/12-π/2)人/小时，请用定积分性质计算一天的总就餐人次。"
```
完整26个话题列表见 `references/math-discussion-topics-template.md`。

完整脚本：`scripts/create_discussion_playwright.py`

## 自动签到（cron定时任务）

上课前5分钟自动创建签到，使用headless Edge浏览器：
- 主脚本：`~/.hermes/scripts/auto_signin.py`（接受JIE参数如"1-2"）
- 签到：`signin_12.py` / `signin_34.py` / `signin_56.py` / `signin_78.py` / `signin_910.py`（全部周一~五触发）
- 选人：`sp_12_1_r1.py` / `sp_12_1_r2.py` 等10个活跃脚本（每时段1个r1+1个r2）
- 脚本根据当前周次+星期+时段判断哪些班级有课，无课自动跳过
- cron统一设为周一至周五（`1-5`），不在cron层限制特定星期

## 按钮ID映射与弹窗处理（合并自 chaoxing-topic-discussion）

**⚠️ 关键发现（2026-06-08 验证）：所有活动类型都有专用按钮ID，必须使用精确ID点击：**

| 活动类型 | 按钮ID | CSS选择器 |
|---------|--------|----------|
| 签到 | `#signin_begin` | `.btnSignIn` |
| 选人 | `#selectPerson_begin` | `.btnSelectPerson` |
| 主题讨论 | `#discuss_begin` | `.btnDiscuss` |
| 抢答 | `#quickAnswer_begin` | `.btnQuickAnswer` |
| 随堂练习 | `#test_begin` | `.btnTest` |

**❌ 错误做法（会导致"未找到按钮"失败）：**
```python
# 用通用文本匹配会找不到按钮
btns = page.evaluate("""() => {
    const all = document.querySelectorAll('a');
    for (let el of all) {
        if ((el.textContent||'').trim() === '立即开始') { ... }
    }
}""")
```

**✅ 正确做法（使用专用按钮ID）：**
```python
result = page.evaluate("""() => {
    const btn = document.getElementById('signin_begin');  # 或 selectPerson_begin / discuss_begin
    if(!btn) return 'not found';
    btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
    let p=btn.parentElement;while(p&&p!==document.body){p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}
    btn.click();return 'clicked';
}""")
```

详细的按钮ID映射表（discuss_begin、signin_begin、selectPerson_begin等完整列表）和弹窗处理详解（z-index/position检查、强制显示函数、调试技巧）见：
- `references/button-id-mapping.md` — 完整按钮ID列表 + 通用活动创建6步流程
- `references/popup-handling.md` — 弹窗类型、CSS类、关闭函数、调试技巧
- `templates/auto_discussion_template.py` — 主题讨论自动发送脚本模板

## 课表数据管理（合并自 chaoxing-course-automation）

详细的课表数据和更新注意事项见：
- `references/class-info-and-schedule.md` — 班级信息 + 第14-18周课表
- `references/schedule-data-notes.md` — 课表数据来源、教室变化记录、更新教训
