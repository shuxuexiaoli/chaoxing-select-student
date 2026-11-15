// 学习通班级活动导航脚本
// 使用方法：在浏览器控制台中执行

function navigateToClassActivity() {
  // 点击左侧菜单"班级活动"
  const menuItems = document.querySelectorAll('.menu-item, .nav-item');
  menuItems.forEach(item => {
    if (item.textContent.includes('班级活动')) {
      item.click();
    }
  });
}

function navigateToClassList(courseId, classId, className) {
  // 在班级列表中查找目标班级
  const classItems = document.querySelectorAll('li.class-list');
  
  classItems.forEach(item => {
    const classname = item.getAttribute('classname');
    if (classname === className) {
      // 点击活动列表按钮
      const btn = item.querySelector('.jb_btn');
      if (btn) {
        btn.scrollIntoView();
        btn.click();
      }
    }
  });
}

// 示例用法：
// navigateToClassActivity();
// setTimeout(() => {
//   navigateToClassList(200000001, 100000002, '示例班级B');
// }, 2000);
