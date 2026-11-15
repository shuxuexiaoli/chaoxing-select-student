// 学习通课程导航脚本
// 使用方法：在浏览器控制台中执行

function navigateToCourse(courseName) {
  // 点击左侧菜单"课程"
  const menuItems = document.querySelectorAll('.menu-item, .nav-item');
  menuItems.forEach(item => {
    if (item.textContent.includes('课程')) {
      item.click();
    }
  });
  
  // 等待iframe加载
  setTimeout(() => {
    // 在iframe中查找课程
    const iframe = document.querySelector('#frame_content');
    if (iframe) {
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      const courseItems = iframeDoc.querySelectorAll('.course-item, .course-list-item');
      
      courseItems.forEach(item => {
        if (item.textContent.includes(courseName)) {
          item.click();
        }
      });
    }
  }, 2000);
}

// 示例用法：
// navigateToCourse('经济数学 第11次开课');
