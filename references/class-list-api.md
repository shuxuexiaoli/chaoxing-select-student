# 学习通班级列表API

## API端点

在活动列表页面内通过 `fetch` 调用（需要已登录的cookies）：

```javascript
// 获取课程所有班级
const resp = await fetch('/v2/apis/class/getClassList?courseId={courseId}&isHaveAuth=1&isfiled=');
const data = await resp.json();
// data.data = [{name, id, studentcount, classEnc, courseEnc, semesterid, ...}, ...]
```

Playwright中调用：
```python
result = page.evaluate("""async () => {
    const resp = await fetch('/v2/apis/class/getClassList?courseId=200000001&isHaveAuth=1&isfiled=');
    return await resp.json();
}""")
classes = result['data']
for c in classes:
    print(f"  {c['name']:20s} id={c['id']}  {c['studentcount']}人")
```

## 经济数学（courseId=200000001）班级列表

共55个班级，关键班级：

| 班级名 | classId | 人数 |
|--------|---------|------|
| 示例班级A | 100000001 | 46 |
| 示例班级B | 100000002 | 46 |
| 示例班级C | 100000003 | 53 |
| 示例班级D | 100000004 | 49 |
| 示例班级E | 100000005 | 44 |
| 电商25-4 | 100000006 | 39 |
| 开放班级 | 142685338 | 335 |

## 高等数学（进阶）（courseId=200000002）班级列表

共47个班级，关键班级：

| 班级名 | classId | enc | 人数 |
|--------|---------|-----|------|
| 示例考试班 | 100000007 | YOUR_ENC | 0（空班，测试用） |
| 高数3重修班 | 144954656 | — | 26 |
| 高数1重修 | 144911494 | — | 86 |
| 数学建模 | 143878403 | — | 40 |

## 注意事项

- API必须在已登录的页面上下文中调用（需要有效的session cookies）
- 直接用 `requests` 调用会返回HTML（需要正确的Cookie header）
- `classEnc` 字段是班级的加密标识，用于构造活动列表URL
- 不同课程的班级列表相互独立
- 示例考试班属于高等数学（进阶），不在经济数学中
