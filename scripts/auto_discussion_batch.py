"""
经济数学主题讨论自动发送脚本（带进度跟踪）
每天为5个班级发送2个主题讨论，共26个主题讨论
使用方法：python auto_discussion.py
进度保存在 discussion_progress.json
"""

import threading
import time
import json
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# 课程参数
COURSE_PARAMS = {
    "courseId": "200000001",
    "cpi": "300000001",
    "enc": "YOUR_ENC",
    "fid": "3012"
}

# 5个班级
CLASSES = [
    {"name": "示例班级A", "classId": "100000001"},
    {"name": "示例班级B", "classId": "100000002"},
    {"name": "示例班级C", "classId": "100000003"},
    {"name": "示例班级D", "classId": "100000004"},
    {"name": "示例班级E", "classId": "100000005"},
]

PHONE = "YOUR_PHONE"
PWD = "190253"

# 26个主题讨论题目（与生活相关）
TOPICS = [
    # 1. 不定积分的概念与性质
    "银行存款复利问题：如果你在银行存入10000元，年利率为5%，连续复利计算，那么经过t年后你的存款总额是多少？请用不定积分的知识解释为什么这个公式是正确的。",
    "汽车行驶距离问题：一辆汽车的速度函数为v(t)=3t²+2t（米/秒），请用不定积分求出汽车的行驶距离函数，并解释为什么不定积分能帮助我们从速度推导出距离。",
    # ... 更多话题见 D:\BaiduSyncdisk\龙虾文件\教学资料\主题讨论题目.md
]

# 进度文件路径（根据实际项目修改）
PROGRESS_FILE = r"D:\BaiduSyncdisk\龙虾文件\教学资料\discussion_progress.json"


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"current_index": 0, "completed": []}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def create_discussion(class_info, topic, results, class_idx):
    """为单个班级创建主题讨论"""
    name = class_info["name"]
    cid = class_info["classId"]
    cp = COURSE_PARAMS

    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, locale="zh-CN")
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # 登录
        print(f"  [{name}] 登录...")
        page.goto("https://passport2.chaoxing.com/login", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        inputs = page.locator("input[type='text']").all()
        if inputs:
            inputs[0].fill(PHONE)
        time.sleep(1)
        page.locator("input[type='password']").first.fill(PWD)
        time.sleep(1)
        page.locator("button[type='submit'], a.submitBtn, .loginBtn, button:has-text('登录'), a:has-text('登录')").first.click()
        time.sleep(15)

        if "四川信息职业技术学院" not in page.title():
            results[name] = "登录失败"
            p.stop()
            return

        # 进入活动列表
        print(f"  [{name}] 进入活动列表...")
        page.goto(
            f"https://mobilelearn.chaoxing.com/page/active/activeList"
            f"?fid={cp['fid']}&courseId={cp['courseId']}&classId={cid}&cpi={cp['cpi']}&enc={cp['enc']}",
            wait_until="domcontentloaded", timeout=60000
        )
        time.sleep(5)

        # 添加主题讨论
        print(f"  [{name}] 添加主题讨论...")
        page.click(".add-activate-icon")
        time.sleep(3)
        page.evaluate("""() => {
            const els = document.querySelectorAll('.btnDiscuss, li.list');
            for (let el of els) {
                if (el.textContent && el.textContent.includes('主题讨论') && el.offsetParent !== null) {
                    el.click(); return;
                }
            }
        }""")
        time.sleep(8)

        # 填写话题
        print(f"  [{name}] 填写话题...")
        try:
            page.wait_for_selector("#discussTitle", state="visible", timeout=15000)
            page.locator("#discussTitle").fill(topic)
        except:
            page.evaluate(f"""() => {{
                const el = document.getElementById('discussTitle');
                if (el) {{ el.value = {json.dumps(topic)}; el.dispatchEvent(new Event('input', {{bubbles:true}})); }}
            }}""")
        time.sleep(2)

        # 点击"立即开始"按钮（过滤hideMyself且width>0）
        btns = page.evaluate("""() => {
            const all = document.querySelectorAll('a, button, div');
            const result = [];
            for (let el of all) {
                if ((el.textContent||'').trim() === '立即开始') {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    if (style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0) {
                        result.push({x: rect.x + rect.width/2, y: rect.y + rect.height/2});
                    }
                }
            }
            return result;
        }""")

        if btns:
            print(f"  [{name}] 点击立即开始 at ({btns[-1]['x']:.0f}, {btns[-1]['y']:.0f})")
            page.mouse.click(btns[-1]['x'], btns[-1]['y'])
            time.sleep(5)
            results[name] = "成功"
            print(f"  [{name}] ✅ 完成")
        else:
            results[name] = "未找到按钮"
            print(f"  [{name}] ❌ 未找到立即开始按钮")

        p.stop()

    except Exception as e:
        print(f"  [{name}] ❌ {e}")
        results[name] = f"错误: {e}"


def send_batch_discussions(topic_idx):
    """为5个班级发送同一个主题讨论"""
    topic = TOPICS[topic_idx]
    print("=" * 60)
    print(f"发送主题讨论 [{topic_idx+1}/{len(TOPICS)}]")
    print(f"主题：{topic[:50]}...")
    print("=" * 60)

    results = {}
    threads = []
    for idx, cls in enumerate(CLASSES):
        t = threading.Thread(target=create_discussion, args=(cls, topic, results, idx))
        threads.append(t)
        t.start()
        time.sleep(3)

    for t in threads:
        t.join()

    success_count = sum(1 for r in results.values() if r == "成功")
    print(f"\n结果：{success_count}/{len(CLASSES)} 成功")
    for name, result in results.items():
        print(f"  {'✅' if result == '成功' else '❌'} {name}: {result}")

    return results


def main():
    progress = load_progress()
    current_index = progress["current_index"]
    
    print(f"\n{'='*60}")
    print(f"经济数学主题讨论自动发送")
    print(f"当前进度：{current_index}/{len(TOPICS)}")
    print(f"日期：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    if current_index >= len(TOPICS):
        print("✅ 所有主题讨论已发送完成！")
        return
    
    # 发送第1个主题讨论
    print(f"\n【第1个主题讨论】")
    results1 = send_batch_discussions(current_index)
    progress["completed"].append({"index": current_index, "results": results1})
    current_index += 1
    save_progress(progress)
    
    time.sleep(5)
    
    # 发送第2个主题讨论
    if current_index < len(TOPICS):
        print(f"\n【第2个主题讨论】")
        results2 = send_batch_discussions(current_index)
        progress["completed"].append({"index": current_index, "results": results2})
        current_index += 1
        progress["current_index"] = current_index
        save_progress(progress)
    
    print(f"\n{'='*60}")
    print(f"今日任务完成！进度：{current_index}/{len(TOPICS)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
