/**
 * 入党积极分子综合评分系统 - UI增强
 * 提供动画、交互和视觉增强功能
 */

// 确保所有AJAX请求包含CSRF令牌
function setupCSRF() {
  const token = document.querySelector('meta[name="csrf-token"]');
  if (!token) return;
  
  const tokenValue = token.getAttribute('content');
  
  // 为所有AJAX请求添加CSRF令牌
  const originalFetch = window.fetch;
  window.fetch = function() {
    const args = Array.from(arguments);
    const resource = args[0];
    const options = args[1] || {};
    
    if (options.method && options.method.toUpperCase() !== 'GET') {
      options.headers = options.headers || {};
      options.headers['X-CSRFToken'] = tokenValue;
    }
    
    args[1] = options;
    return originalFetch.apply(this, args);
  };
  
  // 如果使用jQuery，也为jQuery AJAX添加
  if (typeof $ !== 'undefined' && $.ajaxSetup) {
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", tokenValue);
        }
      }
    });
  }
}

// 数字滚动动画
function animateNumber(element, targetNumber) {
  if (!element) return;
  
  // 确保目标是数字
  targetNumber = parseInt(targetNumber) || 0;
  
  // 获取当前数值
  const currentValue = parseInt(element.textContent) || 0;
  
  // 如果相同就不处理
  if (currentValue === targetNumber) return;
  
  // 设置动画参数
  const duration = 800;
  const framesPerSecond = 60;
  const frames = duration / 1000 * framesPerSecond;
  const step = (targetNumber - currentValue) / frames;
  
  let currentFrame = 0;
  let currentNumber = currentValue;
  
  // 创建动画函数
  function updateNumber() {
    currentFrame++;
    
    // 使用缓动函数使动画更自然
    const progress = currentFrame / frames;
    const easedProgress = easeOutExpo(progress);
    
    currentNumber = currentValue + (targetNumber - currentValue) * easedProgress;
    
    element.textContent = Math.round(currentNumber);
    
    if (currentFrame < frames) {
      requestAnimationFrame(updateNumber);
    } else {
      element.textContent = targetNumber;
    }
  }
  
  // 启动动画
  requestAnimationFrame(updateNumber);
}

// 缓动函数 - 指数式缓出
function easeOutExpo(x) {
  return x === 1 ? 1 : 1 - Math.pow(2, -10 * x);
}

// 添加按钮涟漪效果
function addRippleEffect() {
  document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('mousedown', function(e) {
      // 创建涟漪元素
      const ripple = document.createElement('span');
      ripple.classList.add('ripple-effect');
      
      // 将涟漪元素添加到按钮
      this.appendChild(ripple);
      
      // 计算涟漪大小和位置
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height) * 2.5;
      
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${e.clientX - rect.left - size/2}px`;
      ripple.style.top = `${e.clientY - rect.top - size/2}px`;
      
      // 激活涟漪动画
      ripple.classList.add('active');
      
      // 动画结束后移除元素
      setTimeout(() => {
        ripple.remove();
      }, 1000);
    });
  });
}

// 设置表格滚动效果
function setupTableScrollEffects() {
  const tables = document.querySelectorAll('.table-themed');
  tables.forEach(table => {
    const tableHeader = table.querySelector('thead');
    if (tableHeader) {
      document.addEventListener('scroll', () => {
        const tableRect = table.getBoundingClientRect();
        const headerRect = tableHeader.getBoundingClientRect();
        
        if (tableRect.top < 0 && tableRect.bottom > headerRect.height) {
          tableHeader.style.boxShadow = 'var(--shadow-header)';
        } else {
          tableHeader.style.boxShadow = 'none';
        }
      });
    }
  });
}

// 应用卡片悬停效果
function enhanceCards() {
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      // 添加轻微3D倾斜效果
      card.style.transform = 'translateY(-6px) rotateX(2deg)';
      card.style.boxShadow = 'var(--shadow-medium)';
    });
    
    card.addEventListener('mouseleave', () => {
      // 恢复默认状态
      card.style.transform = '';
      card.style.boxShadow = '';
    });
  });
}

// 处理Flash消息自动消失
function handleFlashMessages() {
  const flashMessages = document.querySelectorAll('.alert-dismissible');
  console.log('找到flash消息:', flashMessages.length);
  
  flashMessages.forEach(function(message) {
    // 添加淡出过渡效果
    message.style.transition = 'opacity 0.3s ease-out';
    
    // 3秒后自动关闭消息
    setTimeout(function() {
      message.style.opacity = '0';
      setTimeout(() => {
        // 使用Bootstrap的dismiss功能关闭警告框或直接移除
        const closeBtn = message.querySelector('.btn-close');
        if (closeBtn) {
          closeBtn.click();
        } else {
          message.remove();
        }
      }, 300); // 等待淡出动画完成
    }, 3000);

    // 点击消息时立即消失
    message.addEventListener('click', function() {
      this.style.opacity = '0';
      setTimeout(() => this.remove(), 300);
    });
  });
}

// 注册页面加载事件
document.addEventListener('DOMContentLoaded', function() {
  // 立即处理Flash消息，确保在页面加载后优先执行
  handleFlashMessages();
  
  // 设置CSRF令牌保护
  setupCSRF();
  
  // 为所有数据主要元素添加动画
  const countElements = document.querySelectorAll('.data-primary');
  if (countElements.length > 0) {
    // 为每个元素设置动画延迟，创造错落感
    countElements.forEach((el, index) => {
      const targetValue = el.textContent;
      el.textContent = '0';
      
      setTimeout(() => {
        animateNumber(el, targetValue);
      }, 300 + index * 150);
    });
  }
  
  // 添加按钮涟漪效果
  addRippleEffect();
  
  // 设置表格滚动效果
  setupTableScrollEffects();
  
  // 增强卡片交互
  enhanceCards();
  
  // 为徽章添加状态变更检测
  observeBadgeChanges();
  
  console.log('UI 增强功能已加载');
});

// 观察徽章状态变化并添加动画
function observeBadgeChanges() {
  // 使用MutationObserver监视徽章文本变化
  const badges = document.querySelectorAll('.badge-themed');
  
  badges.forEach(badge => {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'characterData' || mutation.type === 'childList') {
          // 添加动画类
          badge.classList.add('status-change');
          
          // 动画完成后移除类
          setTimeout(() => {
            badge.classList.remove('status-change');
          }, 1200);
        }
      });
    });
    
    // 配置观察选项
    observer.observe(badge, { 
      characterData: true,
      childList: true,
      subtree: true
    });
  });
} 