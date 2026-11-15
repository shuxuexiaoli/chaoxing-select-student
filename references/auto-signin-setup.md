# 自动签到定时任务

## 架构
```
cron job (每节上课前5分钟)
  → signin_XX.py (wrapper，传节次参数)
    → auto_signin.py (核心脚本，headless Edge登录学习通+创建签到)
```

## 脚本位置
- 核心脚本：`~/.hermes/scripts/auto_signin.py`
- wrapper：`~/.hermes/scripts/signin_12.py` / `signin_34.py` / `signin_56.py` / `signin_78.py`

## 定时任务
| 节次 | 时间 | cron schedule |
|------|------|---------------|
| 1-2节 | 8:45 | `45 8 * * 1-5` |
| 3-4节 | 10:25 | `25 10 * * 1-5` |
| 5-6节 | 13:55 | `55 13 * * 1-5` |
| 7-8节 | 15:45 | `45 15 * * 1-5` |

## 工作流程
1. 脚本读取 JIE 参数（如 "1-2"）
2. 计算当前教学周和星期几
3. 从 SCHEDULE 中筛选今天该节次的班级（检查周次范围）
4. 用 headless Edge 登录学习通
5. 依次为每个班级创建签到（`.btnSignIn` → 填标题"课堂签到" → 立即开始）

## 关键参数
- 登录：phone=YOUR_PHONE, password=YOUR_PASSWORD
- 课程：courseId=200000001, cpi=300000001, enc=YOUR_ENC, fid=YOUR_FID
- 学期第1周周一：2026-03-02

## 注意事项
- 使用 headless=True 模式（无界面）
- 使用 channel="msedge"
- 结果发送到微信
