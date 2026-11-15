# 四川信息职业技术学院 - 信息门户（智慧川信）自动化

> **完整文档已迁移至独立技能 `scitc-portal`**，请使用 `skill_view(name='scitc-portal')` 查看完整操作指南。

## 快速参考

- **官网**: https://www.scitc.edu.cn/
- **信息门户**: https://zhcx.scitc.edu.cn/
- **登录方式**: 微信扫码（默认）或 验证码（`input[name='Tel']` + `input[name='yzm']`）
- **用户**: 李盘润（T00081），人文学院 > 数学教研室

## 域名纠正

- ❌ `sict.edu.cn` — 不存在或页面为空
- ❌ `scit.edu.cn` — 四川工业科技学院（不是目标学校）
- ✅ `scitc.edu.cn` — 正确的官网域名

## 关键Pitfalls

1. 手机号输入框是 `type="number"`，用 `input[type='text']` 会匹配到验证码框
2. 验证码每日限5次
3. `cas.svci.edu.cn` 无法解析，用 `zhcx.scitc.edu.cn`
4. 每次Playwright脚本启动都是新浏览器实例，登录状态不保留
