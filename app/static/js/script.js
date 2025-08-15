document.addEventListener('DOMContentLoaded', function() {
    // 创建动态星星效果
    createStars();
    createShootingStars();
    
    // 聚焦效果
    document.querySelectorAll('.form-group input').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focus');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focus');
            }
        });
        
        // 检查初始状态
        if (input.value) {
            input.parentElement.classList.add('focus');
        }
    });
    
    // 登录按钮点击事件在login.html中已实现
    
    // 消息提示功能在login.html中已实现
});

// 创建星星背景
function createStars() {
    const starsContainer = document.querySelector('.stars');
    if (!starsContainer) return;
    
    const starsCount = 100;
    
    for (let i = 0; i < starsCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        
        // 随机大小
        const size = Math.random();
        if (size < 0.5) {
            star.classList.add('small');
            star.style.animationDuration = `${Math.random() * 5 + 2}s`;
        } else if (size < 0.8) {
            star.classList.add('medium');
            star.style.animationDuration = `${Math.random() * 4 + 3}s`;
        } else {
            star.classList.add('large');
            star.style.animationDuration = `${Math.random() * 3 + 4}s`;
        }
        
        // 随机位置
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        
        // 随机延迟
        star.style.animationDelay = `${Math.random() * 5}s`;
        
        starsContainer.appendChild(star);
    }
}

// 创建流星效果
function createShootingStars() {
    const container = document.getElementById('shooting-stars-container');
    if (!container) return;
    
    setInterval(() => {
        if (Math.random() > 0.7) {
            const shootingStar = document.createElement('div');
            shootingStar.classList.add('shooting-star');
            
            // 随机位置和角度
            const startX = Math.random() * container.offsetWidth;
            const startY = Math.random() * (container.offsetHeight / 2);
            
            shootingStar.style.left = `${startX}px`;
            shootingStar.style.top = `${startY}px`;
            shootingStar.style.animationDuration = `${Math.random() * 1 + 0.5}s`;
            
            container.appendChild(shootingStar);
            
            // 动画结束后移除
            setTimeout(() => {
                shootingStar.remove();
            }, 2000);
        }
    }, 1000);
} 