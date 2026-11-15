# 为单个班级创建选人活动（快速参考）

## 脚本模板

文件：`~/.hermes/scripts/create_select_dq252.py`（示例班级B示例）

关键参数：
```python
COURSE_ID = "200000001"  # 经济数学
CPI = "300000001"
ENC = "YOUR_ENC"
FID = "3012"
CLASS_ID = "100000002"  # 示例班级B
```

## 完整流程（3步）

1. 登录学习通（headless Edge, 等15秒）
2. 导航到活动列表URL
3. 添加活动 → 选人 → 填事由 → 点击立即开始

## 按班级切换

| 班级 | classId |
|------|---------|
| 示例班级A | 100000001 |
| 示例班级B | 100000002 |
| 示例班级C | 100000003 |
| 示例班级D | 100000004 |
| 示例班级E | 100000005 |

## 活动类型切换

将 `.btnSelectPerson` 替换为其他CSS选择器即可切换活动类型：
- 选人：`.btnSelectPerson`，事由输入框 `input[placeholder*='请输入选人事由']`
- 签到：`.btnSignIn`，需先选"普通签到"
- 抢答：`.btnQuickAnswer`，内容输入框 `input[placeholder*='请输入抢答内容']`
- 主题讨论：`.btnDiscuss`，话题 `textarea#discussTitle`（等15秒）
- 随堂练习：`.btnTest`
