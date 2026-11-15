// 学习通登录脚本
// 使用方法：在浏览器控制台中执行

function loginToChaoxing(phone, password) {
  // 填入手机号
  const phoneInput = document.querySelector('#phone');
  if (phoneInput) {
    phoneInput.value = phone;
  }
  
  // 填入密码
  const pwdInput = document.querySelector('#pwd');
  if (pwdInput) {
    pwdInput.value = password;
  }
  
  // 点击登录按钮
  const loginBtn = document.querySelector('.login-btn');
  if (loginBtn) {
    loginBtn.click();
  }
  
  // 处理隐私政策弹窗（如果有）
  setTimeout(() => {
    const agreeBtn = document.querySelector('.agree-btn');
    if (agreeBtn) {
      agreeBtn.click();
    }
  }, 1000);
}

// 示例用法：
// loginToChaoxing('YOUR_PHONE', 'your_password');
