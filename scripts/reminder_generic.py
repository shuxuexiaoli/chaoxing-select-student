"""
学习通课堂提醒通用脚本（任意班级）
用法: python reminder_generic.py <班级名> <教室> <节次>

2026-06-08 创建：发送课堂提醒到微信
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from datetime import datetime

def send_reminder(class_name, room, jie):
    """发送课堂提醒"""
    now = datetime.now()
    time_str = now.strftime("%H:%M")
    
    # 计算上课时间
    time_map = {
        "1-2": "08:50",
        "3-4": "10:30",
        "5-6": "14:00",
        "7-8": "15:50",
        "9-10": "19:00"
    }
    start_time = time_map.get(jie, "未知")
    
    message = f"""
📚 课堂提醒

⏰ 时间: {time_str}（{start_time}上课）
🏫 教室: {room}
👥 班级: {class_name}
📖 节次: 第{jie}节

请准备上课！
"""
    
    print(message, flush=True)
    return message

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python reminder_generic.py <班级名> <教室> <节次>")
        sys.exit(1)
    
    class_name = sys.argv[1]
    room = sys.argv[2]
    jie = sys.argv[3]
    
    send_reminder(class_name, room, jie)
