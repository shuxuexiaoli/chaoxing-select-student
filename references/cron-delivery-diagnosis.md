# Cron投递问题诊断记录（2026-06-09）

## 问题描述

用户多次反馈cron定时任务"还是没有执行"，但日志显示任务已"delivered"。

## 诊断过程

### 1. 检查cron任务状态
```bash
cronjob list
```
发现 `no_agent=true` 的任务 `last_run_at: null` 或已被消耗（从列表消失），但用户未收到消息。

### 2. 检查agent.log
```
2026-06-09 18:50:02 INFO cron.scheduler: Job 'f5e1f9b7eeaf': delivered to weixin:o9cq80925DA-gRppBzmVoEEhKEEs@im.wechat via live adapter
```
显示投递成功。

### 3. 检查gateway.log
```
（18:50时间段无任何发送记录）
```
**关键发现**：agent.log显示"delivered via live adapter"，但gateway.log没有任何对应的发送记录。

### 4. 检查errors.log
```
2026-06-09 10:32:10 ERROR cron.scheduler: Job '4e832a3368b7': delivery error: Weixin send failed: iLink sendmessage rate limited; cooldown active for 30.0s
```
部分任务有明确的限速错误，但18:50的任务没有错误记录。

### 5. 测试agent模式
创建 `no_agent=false` 的测试任务（示例考试班签到），19:05执行：
```
2026-06-09 19:06:14 INFO cron.scheduler: Job '测试-示例考试班-签到' completed successfully
2026-06-09 19:06:14 INFO cron.scheduler: Job '6e277fe1ce58': delivered to weixin via live adapter
```
用户确认收到了消息。

## 根因

`no_agent=true` 的cron任务通过"live adapter"投递stdout输出到微信，但live adapter存在静默失败的问题：
- 返回成功状态，但消息未实际发送到gateway
- gateway.log无对应记录
- 用户收不到消息

`no_agent=false` 的cron任务通过agent会话执行，agent使用send_message工具发送结果，走的是正常gateway通道，不经过live adapter。

## 结论

**所有cron任务必须使用 `no_agent=false`（agent模式）**，在prompt中指示agent调用terminal执行脚本。

## 参考

- Pitfall 29: Cron `no_agent=true` 的live adapter投递问题
- Pitfall 30: WeChat消息限速导致cron投递失败
