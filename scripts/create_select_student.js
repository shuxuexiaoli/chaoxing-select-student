// 学习通创建选人活动脚本
// 使用方法：在浏览器控制台中执行
// 正确的CSS选择器：
//   - 添加活动按钮: .add-activate-icon
//   - 选人选项: .btnSelectPerson (不是 .title-name)

function createSelectStudentActivity() {
  // 点击"添加活动"按钮（使用 .add-activate-icon 类）
  const addBtn = document.querySelector('.add-activate-icon');
  if (addBtn) {
    addBtn.click();
  }
  
  // 等待菜单弹出
  setTimeout(() => {
    // 查找并点击"选人"（使用 .btnSelectPerson 类）
    const selectBtn = document.querySelector('.btnSelectPerson');
    if (selectBtn) {
      selectBtn.click();
    }
  }, 500);
}

// 示例用法：
// createSelectStudentActivity();
