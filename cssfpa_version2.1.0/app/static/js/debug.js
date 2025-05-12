// 诊断脚本 - 用于排查图表渲染问题
console.log('正在运行诊断脚本 debug.js');

window.addEventListener('load', function() {
    // 检查Chart.js是否成功加载
    if (typeof Chart === 'undefined') {
        console.error('无法找到Chart对象，Chart.js未成功加载');
        // 添加错误提示到页面
        document.querySelectorAll('.chart-container').forEach(container => {
            container.innerHTML = '<div class="alert alert-danger">图表库加载失败，请检查网络连接</div>';
        });
        return;
    }

    console.log('Chart.js版本:', Chart.version);
    
    // 检查canvas元素
    const canvases = document.querySelectorAll('canvas');
    console.log(`找到 ${canvases.length} 个Canvas元素`);
    
    if (canvases.length === 0) {
        console.error('没有找到canvas元素，无法渲染图表');
        return;
    }
    
    canvases.forEach(canvas => {
        console.log(`Canvas ${canvas.id}: 尺寸=${canvas.width}x${canvas.height}, 可见性=${window.getComputedStyle(canvas).display}`);
        
        // 确保canvas可见
        if (window.getComputedStyle(canvas).display === 'none') {
            canvas.style.display = 'block';
        }
        
        // 获取父容器尺寸
        const container = canvas.parentElement;
        console.log(`  父容器: ${container.className}, 尺寸=${container.offsetWidth}x${container.offsetHeight}`);
        
        // 检查父容器是否有高度
        if (container.offsetHeight < 50) {
            console.warn(`  警告: ${canvas.id} 的父容器高度不足`);
            container.style.height = '300px';
        }
    });
    
    // 渲染测试图表
    try {
        // 找到可用的容器
        const containers = document.querySelectorAll('.chart-container');
        if (containers.length === 0) {
            console.error('没有找到.chart-container元素');
            return;
        }
        
        // 在第一个遇到问题的容器中创建测试图表
        containers.forEach(container => {
            const canvas = container.querySelector('canvas');
            if (!canvas) return;
            
            // 如果canvas已经有内容，跳过
            if (canvas.getAttribute('data-debug-drawn') === 'true') return;
            
            try {
                // 尝试获取canvas上下文
                const ctx = canvas.getContext('2d');
                if (!ctx) {
                    console.error(`无法获取Canvas ${canvas.id} 的绘图上下文`);
                    return;
                }
                
                // 绘制简单矩形以测试canvas是否工作
                ctx.fillStyle = 'red';
                ctx.fillRect(10, 10, 100, 100);
                
                console.log(`成功在Canvas ${canvas.id} 上绘制测试矩形`);
                canvas.setAttribute('data-debug-drawn', 'true');
            } catch (e) {
                console.error(`绘制测试图形到 ${canvas.id} 时出错:`, e);
            }
        });
    } catch (e) {
        console.error('尝试创建测试图表时出错:', e);
    }
}); 