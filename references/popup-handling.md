# 学习通页面弹窗处理详解

## 常见弹窗类型

### 1. 权限设置弹窗 (popPermission)
- CSS类：`.popDiv.popPermission`, `.maskDiv.popPerSet`
- 内容：允许管理我的课堂活动 + 教师列表
- 出现时机：进入活动列表时

### 2. 通讯录弹窗 (pick-container)
- CSS类：`.pick-container.mod.have-head`
- 内容：联系人、单位、加入的小组、我的课程
- 出现时机：添加活动时

### 3. 资源选择弹窗 (popMove)
- CSS类：`.popDiv.popMove`, `.popCellShowHide`
- 内容：收藏的专题、全部文件
- 出现时机：添加活动时

### 4. 确认弹窗
- CSS类：`.popBottom.shadowBox`, `.confirm-class`
- 内容：确定、取消按钮
- 出现时机：提交操作时

## 按钮被隐藏的症状

```javascript
// 检查按钮状态
btn_info = page.evaluate('''() => {
    const all = document.querySelectorAll('a, button, div');
    for (let el of all) {
        if ((el.textContent||'').trim() === '立即开始') {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return {
                display: style.display,      // 可能是 'none'
                visibility: style.visibility, // 可能是 'visible' 但 display=none
                width: rect.width,           // 可能是 0
                height: rect.height,         // 可能是 0
            };
        }
    }
}''')
```

**典型问题**：display='none', width=0, height=0

## 完整的弹窗关闭函数

```python
def close_popups(page):
    """关闭所有弹窗"""
    page.evaluate('''() => {
        const selectors = [
            '.popDiv', '.maskDiv', '.popBottom', 
            '.pick-container', '.popPermission', 
            '.popMove', '.popCellShowHide'
        ];
        for (let sel of selectors) {
            const els = document.querySelectorAll(sel);
            for (let el of els) {
                el.style.display = 'none';
            }
        }
    }''')
    time.sleep(1)
```

## 强制显示按钮函数

```python
def force_show_and_click(page, button_text):
    """强制显示并点击按钮"""
    result = page.evaluate(f"""() => {{
        const all = document.querySelectorAll('a, button, div');
        for (let el of all) {{
            if ((el.textContent||'').trim() === '{button_text}') {{
                el.style.display = 'block';
                el.style.visibility = 'visible';
                el.style.width = 'auto';
                el.style.height = 'auto';
                el.style.opacity = '1';
                el.style.position = 'relative';
                el.style.zIndex = '9999';
                el.click();
                return 'clicked';
            }}
        }}
        return 'not found';
    }}""")
    return result
```

## 调试技巧

### 查看页面上所有相关按钮
```python
btns = page.evaluate('''() => {
    const all = document.querySelectorAll('a, button, div');
    const result = [];
    for (let el of all) {
        const text = (el.textContent||'').trim();
        if (text.includes('立即开始') || text.includes('确定') || text.includes('提交')) {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            result.push({
                text: text.substring(0, 50),
                tag: el.tagName,
                class: el.className.substring(0, 50),
                display: style.display,
                width: rect.width,
                height: rect.height
            });
        }
    }
    return result;
}''')

for btn in btns:
    print(f"  - {btn['text']} ({btn['tag']}) display={btn['display']} width={btn['width']}")
```

## 各班级差异

不同班级的页面弹窗可能不同：
- 示例班级B：弹窗较多，需要多次关闭弹窗
- 其他班级：弹窗较少

**建议**：对所有班级都使用弹窗关闭逻辑，避免偶发失败。
