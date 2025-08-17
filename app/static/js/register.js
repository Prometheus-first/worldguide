document.addEventListener('DOMContentLoaded', function() {
    // 添加短暂延迟后标记页面已加载
    setTimeout(function() {
        document.body.classList.add('loaded');
    }, 100);
    
    // 表单组件淡入动画
    setTimeout(function() {
        document.querySelectorAll('.form-group, .terms-checkbox, .register-btn, .login-link').forEach(function(el, index) {
            setTimeout(function() {
                el.classList.add('fade-in');
            }, index * 150);
        });
    }, 500);
    
    // 修复密码可见性切换
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            // 找到当前按钮所在表单组中的密码输入框
            const input = this.closest('.form-group').querySelector('input');
            
            // 切换密码可见性
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            // 更新图标
            const eyeIcon = this.querySelector('svg');
            if (type === 'text') {
                eyeIcon.innerHTML = `
                    <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                `;
            } else {
                eyeIcon.innerHTML = `
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 14a2 2 0 100-4 2 2 0 000 4z" fill="currentColor"/>
                `;
            }
        });
    });
    
    // 添加输入框聚焦效果
    document.querySelectorAll('.form-group input').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
    
    // 添加随机动画效果
    const glow = document.querySelector('.glow-effect');
    
    function moveGlow() {
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        glow.style.left = `${x}%`;
        glow.style.top = `${y}%`;
        
        setTimeout(moveGlow, 5000);
    }
    
    moveGlow();
    
    // 消息提示
    const messageContainer = document.getElementById('message-container');
    const messageText = document.getElementById('message-text');
    const closeBtn = document.querySelector('.close-btn');
    
    // 关闭消息提示
    closeBtn.addEventListener('click', function() {
        messageContainer.classList.remove('show');
    });
    
    // 注册表单提交
    document.getElementById('register-btn').addEventListener('click', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const terms = document.getElementById('terms').checked;
        
        // 表单验证
        if (!username || !email || !password || !confirmPassword) {
            showMessage('请填写所有必填字段', 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            showMessage('两次输入的密码不一致', 'error');
            return;
        }
        
        if (!terms) {
            showMessage('请同意服务条款和隐私政策', 'error');
            return;
        }
        
        // 创建表单数据
        const formData = new FormData();
        formData.append('username', username);
        formData.append('email', email);
        formData.append('password', password);
        formData.append('confirm_password', confirmPassword);
        
        // 发送注册请求
        fetch('/auth/api/register', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                
                // 延迟后重定向到登录页面
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 1500);
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('注册错误:', error);
            showMessage('注册过程中发生错误，请重试', 'error');
        });
    });
    
    // 显示消息提示
    function showMessage(message, type) {
        messageText.textContent = message;
        messageContainer.className = 'message-container show';
        messageContainer.querySelector('.message').className = `message ${type}`;
        
        // 自动关闭消息
        setTimeout(() => {
            messageContainer.classList.remove('show');
        }, 5000);
    }
}); 