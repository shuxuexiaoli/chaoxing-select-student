# 学习通定时任务设置指南

## ⚠️ 关键：必须使用agent模式（no_agent=false）

`no_agent=true` 的cron任务通过"live adapter"投递到微信时会静默失败（脚本执行了但消息没到）。必须使用 `no_agent=false`（agent模式），在prompt中指示agent调用terminal执行脚本。

详见 Pitfall 29 和 `references/cron-delivery-diagnosis.md`。

## 定时任务类型

### 1. 课堂提醒（上课前10分钟）
```
prompt: '请发送提醒消息："📢 班级名 第X-X节 课程名 教室XXX 马上上课！"'
```

### 2. 课堂签到（上课前5分钟）
```
prompt: "请立即执行以下命令为班级名创建签到活动：\ncd ~/AppData/Local/hermes/scripts && python signin_generic.py <classId> 班级名\n\n执行完成后，报告签到结果。"
```

### 3. 选人活动（上课后10分钟 / 下课前10分钟）
```
prompt: "请立即执行以下命令为班级名创建选人活动：\ncd ~/AppData/Local/hermes/scripts && python select_student_generic.py <classId> 班级名\n\n执行完成后，报告选人结果。"
```

### 4. 主题讨论（每天10:30）
```
prompt: "现在是10:30，每天主题讨论时间到了。请执行以下操作：\n执行脚本：cd ~/AppData/Local/hermes/scripts && python -u auto_discussion_daily.py\n脚本会自动读取进度，发送下一个话题到5个班级。完成后汇报结果。"
```

## 经济数学课程班级ID

| 班级名 | classId |
|--------|---------|
| 示例班级A | 100000001 |
| 示例班级B | 100000002 |
| 示例班级C | 100000003 |
| 示例班级D | 100000004 |
| 示例班级E | 100000005 |

## 高等数学（进阶）课程班级ID

| 班级名 | classId |
|--------|---------|
| 示例考试班 | 100000007 |

## 课程参数

### 经济数学
```
courseId: 200000001
cpi: 300000001
enc: YOUR_ENC
fid: YOUR_FID
```

### 高等数学（进阶）
```
courseId: 200000002
cpi: 300000002
enc: YOUR_ENC
fid: YOUR_FID
```

## 课表时间

| 节次 | 上课时间 | 提醒时间 | 签到时间 | 选人-上课后 | 选人-下课前 |
|------|----------|----------|----------|------------|------------|
| 1-2节 | 08:50 | 08:40 | 08:45 | 09:00 | 10:10 |
| 3-4节 | 10:30 | 10:20 | 10:25 | 10:40 | 11:50 |
| 5-6节 | 14:00 | 13:50 | 13:55 | 14:10 | 15:20 |
| 7-8节 | 15:50 | 15:40 | 15:45 | 16:00 | 17:10 |
| 9-10节 | 19:00 | 18:50 | 18:55 | 19:10 | 20:20 |

## Cron任务设置示例（agent模式）

```bash
# 提醒
cronjob create name="提醒-示例班级E-1-2节" schedule="2026-06-09T08:40:00" \
  prompt='请发送提醒消息："📢 示例班级E 第1-2节 高等数学2 教室2506 马上上课！"'

# 签到
cronjob create name="签到-示例班级E-1-2节" schedule="2026-06-09T08:45:00" \
  prompt="请立即执行以下命令为示例班级E创建签到活动：\ncd ~/AppData/Local/hermes/scripts && python signin_generic.py 100000005 示例班级E\n\n执行完成后，报告签到结果。"

# 选人-上课后
cronjob create name="选人-示例班级E-上课后" schedule="2026-06-09T09:00:00" \
  prompt="请立即执行以下命令为示例班级E创建上课后选人活动：\ncd ~/AppData/Local/hermes/scripts && python select_student_generic.py 100000005 示例班级E\n\n执行完成后，报告选人结果。"

# 选人-下课前
cronjob create name="选人-示例班级E-下课前" schedule="2026-06-09T10:10:00" \
  prompt="请立即执行以下命令为示例班级E创建下课前选人活动：\ncd ~/AppData/Local/hermes/scripts && python select_student_generic.py 100000005 示例班级E\n\n执行完成后，报告选人结果。"
```

## 常见问题

### Q: Cron任务显示 `last_status: "error"` 但脚本手动运行正常
A: 这通常是**消息投递失败**（如微信限速），不是脚本执行失败。检查脚本的副作用（进度文件、活动列表）确认脚本是否真正执行。详见 Pitfall 27 和 Pitfall 30。

### Q: 用户收不到cron任务的消息
A: 检查是否使用了 `no_agent=true`。如果是，改为 `no_agent=false`（agent模式）。详见 Pitfall 29。

### Q: Cron任务 `next_run_at: null` 且 `last_run_at: null`
A: 任务可能因路径问题无法执行。确认脚本路径使用 `~/AppData/Local/hermes/scripts/` 而非 `~/.hermes/scripts/`。详见 Pitfall 28。

## 进度文件

主题讨论进度文件: `D:/BaiduSyncdisk/龙虾文件/教学资料/discussion_progress.json`

```json
{
  "current_index": 6,
  "completed": [
    {"index": 0, "results": {"示例班级A": "成功", ...}},
    ...
  ]
}
```
