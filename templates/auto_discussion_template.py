"""
学习通主题讨论脚本 - 每天自动发送
读取进度文件，发送下一个话题到5个班

使用方法（示例考试班验证通过）：
1. 登录学习通
2. 进入指定班级活动列表
3. 点击添加按钮（force=True）
4. 选择主题讨论（.btnDiscuss）
5. 等待15秒表单加载
6. 填写话题（textarea#discussTitle）
7. 点击 #discuss_begin（专用按钮ID）

关键点：
- 必须使用 #discuss_begin，不能用通用"立即开始"文本
- 弹窗处理需检查 z-index 和 position
- 添加按钮需用 force=True
- 主题讨论表单需等15秒加载
- 话题用 Playwright fill()，不用 JS el.value
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import time
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

PHONE = "YOUR_PHONE"
PWD = "190253"
CP = {"courseId":"200000001","cpi":"300000001","enc":"YOUR_ENC","fid":"3012"}
CLASSES = [
    {"name":"示例班级A","classId":"100000001"},
    {"name":"示例班级B","classId":"100000002"},
    {"name":"示例班级C","classId":"100000003"},
    {"name":"示例班级D","classId":"100000004"},
    {"name":"示例班级E","classId":"100000005"},
]
TOPICS = [
    "你每月生活费1500元，每天花销速度为v(t)=50-0.5t（元/天），请用不定积分推导出第t天花完后的总花销函数。",
    "你跑步的速度函数为v(t)=2t+3（米/秒），请用不定积分求出你跑过的距离函数s(t)。",
    "你打游戏升级，经验增长率为f(x)=100+5x（点/小时），请用直接积分法求出x小时后的总经验值函数。",
    "你刷短视频的流量消耗率为f(t)=2+0.1t（MB/分钟），请用直接积分法求出t分钟的总流量消耗函数。",
    "手机电量消耗率P(t)=2t·e^(-t²)，请用第一类换元积分法求0到t时刻的总消耗量。",
    "咖啡因在体内的衰减率为C(t)=C₀·e^(-0.1t)，请用第一类换元积分法求体内咖啡因总量变化规律。",
    "期末复习效率随时间变化为dE/dt=E·(1-E/100)，请用换元积分法求解此微分方程，预测复习效率变化。",
    "外卖订单增长率为dN/dt=k√N，请用换元积分法求订单量随时间的变化规律。",
    "校园喷泉的水柱高度函数含√(ax+b)，请用第二类换元积分法计算水柱的截面面积。",
    "自行车轮胎的周长计算含√(r²-a²)，请用第二类换元积分法求轮胎的周长。",
    "你的兼职收入函数为R(t)=t·e^(0.05t)（元/月），请用分部积分法计算半年的总收入。",
    "你的笔记本电脑折旧率为dV/dt=-t·ln(t+1)，请用分部积分法求电脑价值随时间的变化规律。",
    "校园小路的宽度随位置变化为f(x)=3+0.5sin(x)米，请用定积分解释如何计算这段路的总面积。",
    "你一天的学习时间分配率为r(t)=5+3cos(πt/12)小时，请用定积分解释如何计算一天的总学习时间。",
    "教室温度函数为T(t)=22+5sin(πt/12)℃，请用定积分性质计算一天的平均温度。",
    "食堂客流量率为f(t)=100+80sin(πt/12-π/2)人/小时，请用定积分性质计算一天的总就餐人次。",
    "你骑自行车刹车时减速度为a(t)=-4t米/秒²，请用微积分基本定理求停车时间和滑行距离。",
    "校园网速随时间变化为v(t)=10+5sin(πt/12)MB/秒，请用微积分基本定理计算一天的总下载量。",
    "太阳能充电宝的充电功率为P(t)=P₀·sin²(πt/12)，请用第一类换元积分法计算一天的总充电量。",
    "宿舍空调的能耗率为E(t)=k·(T_out-T_in)²，请用第一类换元积分法计算一天的总电费。",
    "校园拱桥的截面高度含√(a²-x²)，请用第二类换元积分法计算桥拱的截面面积。",
    "操场跑道的周长计算含√(a²sin²t+b²cos²t)，请用第二类换元积分法近似计算跑道长度。",
    "股票收益率为R(t)=t·e^(rt)，请用分部积分法计算4年大学期间的累计收益。",
    "手机电池的维护成本率为C(t)=t·ln(t+1)元/年，请用分部积分法计算大学4年的总维护成本。",
    "校园人工湖的边界为y=f(x)，请用定积分设计面积测量方案。",
    "图书馆屋顶的截面曲线为y=6-0.2x²米，请用定积分计算屋顶面积。",
]
PROGRESS_FILE = Path.home() / "BaiduSyncdisk/龙虾文件/教学资料/discussion_progress.json"

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

def create_discussion(page, class_id, class_name, topic):
    """为一个班级创建主题讨论"""
    try:
        page.goto(
            f"https://mobilelearn.chaoxing.com/page/active/activeList"
            f"?fid={CP['fid']}&courseId={CP['courseId']}&classId={class_id}&enc={CP['enc']}",
            wait_until="domcontentloaded", timeout=60000
        )
        time.sleep(5)
        close_popups(page)

        page.locator('.add-activate-icon').click(force=True)
        time.sleep(3)
        close_popups(page)

        page.evaluate("""() => {
            const el = document.querySelector('.btnDiscuss');
            if(el){el.click();return;}
        }""")
        time.sleep(15)  # 主题讨论表单需等15秒加载
        close_popups(page)

        try:
            page.wait_for_selector("#discussTitle", state="visible", timeout=10000)
            page.locator("#discussTitle").fill(topic)
        except:
            page.evaluate(f'() => {{ const el=document.getElementById("discussTitle"); if(el){{el.value="{topic}";el.dispatchEvent(new Event("input",{{bubbles:true}}));}} }}')
        time.sleep(2)
        close_popups(page)

        r = page.evaluate("""() => {
            const btn = document.getElementById('discuss_begin');
            if(!btn) return 'not found';
            btn.style.cssText='display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:99999!important';
            let p=btn.parentElement;while(p&&p!==document.body){p.style.display='';p.style.visibility='visible';p.style.opacity='1';p=p.parentElement;}
            btn.click();return 'clicked';
        }""")
        time.sleep(3)
        return 'clicked' in str(r)
    except Exception as e:
        print(f"  ❌ {class_name}错误: {e}", flush=True)
        return False

def load_progress():
    """加载进度文件"""
    try:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"current_index": 0, "completed": []}

def save_progress(data):
    """保存进度文件"""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    """主函数：读取进度，发送下一个话题"""
    progress = load_progress()
    idx = progress.get("current_index", 0)
    
    if idx >= len(TOPICS):
        print("✅ 所有话题已发送完毕！", flush=True)
        return
    
    topic = TOPICS[idx]
    print(f"📢 发送话题 #{idx}: {topic[:50]}...", flush=True)
    
    p = sync_playwright().start()
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_context(viewport={"width":1280,"height":800}, locale="zh-CN").new_page()
    page.set_default_timeout(30000)

    print("📝 登录...", flush=True)
    do_login(page)
    
    results = {}
    for cls in CLASSES:
        name = cls["name"]
        cid = cls["classId"]
        print(f"  📤 {name}...", flush=True)
        ok = create_discussion(page, cid, name, topic)
        results[name] = "成功" if ok else "失败"
        print(f"  {'✅' if ok else '❌'} {name}", flush=True)
    
    browser.close()
    p.stop()
    
    # 更新进度
    progress["completed"].append({"index": idx, "results": results})
    progress["current_index"] = idx + 1
    save_progress(progress)
    
    success = sum(1 for r in results.values() if r == "成功")
    print(f"\n📊 结果: {success}/{len(CLASSES)} 成功", flush=True)
    print(f"📈 进度: {idx + 1}/{len(TOPICS)}", flush=True)

if __name__ == "__main__":
    main()
