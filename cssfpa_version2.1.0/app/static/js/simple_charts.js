// 简化版图表脚本
console.log('简化版图表脚本已加载');

// 定义通用的颜色
var chartColors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#5a5c69', '#6f42c1'];
var chartBorderColors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#5a5c69', '#6f42c1'];

// 安全的JSON解析函数
function safeJSONParse(str, defaultValue) {
    try {
        return JSON.parse(str);
    } catch (e) {
        console.error('JSON解析错误:', e);
        return defaultValue || {};
    }
}

// 检查Chart.js是否可用
function isChartAvailable() {
    return typeof Chart !== 'undefined';
}

// 窗口加载后初始化图表
window.addEventListener('load', function() {
    console.log('窗口已加载，开始初始化图表');
    try {
        if (!isChartAvailable()) {
            console.error('Chart.js未加载，尝试手动加载');
            // 可以在这里添加动态加载Chart.js的代码
            return;
        }
        
        // 创建测试图表确认Chart.js工作正常
        createTestChart();
        
        // 初始化所有图表
        initializeCharts();
    } catch (e) {
        console.error('图表初始化失败:', e);
    }
});

// 创建测试图表以验证Chart.js功能
function createTestChart() {
    try {
        const testCanvas = document.getElementById('testChart');
        if (!testCanvas) return;
        
        console.log('创建测试图表');
        new Chart(testCanvas, {
            type: 'pie',
            data: {
                labels: ['测试1', '测试2'],
                datasets: [{
                    data: [50, 50],
                    backgroundColor: ['#4e73df', '#1cc88a']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } catch (e) {
        console.error('测试图表创建失败:', e);
    }
}

// 初始化所有图表
function initializeCharts() {
    console.log('开始初始化所有图表');
    
    // 创建各种饼图
    createGenderChart();
    createPoliticalStatusChart();
    createApplicationStatusChart();
    createApprovalChart();
    createExamPassRateChart();
    createDepartmentChart();
}

// 通用饼图创建函数
function createSimplePieChart(canvasId, dataElementId, defaultData = {}) {
    try {
        const canvas = document.getElementById(canvasId);
        const dataElement = document.getElementById(dataElementId);
        
        if (!canvas) {
            console.warn(`图表canvas不存在: ${canvasId}`);
            return;
        }
        
        let chartData = defaultData;
        if (dataElement) {
            try {
                const dataContent = dataElement.textContent.trim();
                if (dataContent) {
                    chartData = JSON.parse(dataContent);
                }
            } catch (e) {
                console.error(`解析${dataElementId}数据失败:`, e);
            }
        } else {
            console.warn(`数据元素不存在: ${dataElementId}`);
        }
        
        // 提取标签和数据
        const labels = Object.keys(chartData);
        const data = Object.values(chartData);
        
        // 为饼图生成颜色
        const backgroundColor = generateColors(labels.length);
        
        console.log(`创建图表: ${canvasId}`, { labels, data });
        
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColor
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 10
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total ? Math.round((value / total) * 100) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (e) {
        console.error(`创建${canvasId}图表失败:`, e);
    }
}

// 性别分布图表
function createGenderChart() {
    const defaultData = { '男': 0, '女': 0 };
    createSimplePieChart('genderChart', 'gender-data', defaultData);
}

// 政治面貌分布图表
function createPoliticalStatusChart() {
    const defaultData = { '中共党员': 0, '预备党员': 0, '共青团员': 0, '群众': 0 };
    createSimplePieChart('politicalStatusChart', 'political-data', defaultData);
}

// 申请状态图表
function createApplicationStatusChart() {
    const defaultData = { '已提交': 0, '未提交': 0 };
    createSimplePieChart('applicationStatusChart', 'application-data', defaultData);
}

// 班级推优状态图表
function createApprovalChart() {
    const defaultData = { '已通过': 0, '未通过': 0 };
    createSimplePieChart('approvalChart', 'class-approved-data', defaultData);
}

// 考试通过状态图表
function createExamPassRateChart() {
    const defaultData = { '已通过': 0, '未通过': 0 };
    createSimplePieChart('examPassRateChart', 'exam-data', defaultData);
}

// 院系分布图表
function createDepartmentChart() {
    createSimplePieChart('departmentChart', 'department-data', {});
}

// 生成颜色数组
function generateColors(count) {
    // 预定义的颜色数组
    const colors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#5a5c69', '#6610f2', '#fd7e14', '#20c9a6', '#858796'
    ];
    
    if (count <= colors.length) {
        return colors.slice(0, count);
    }
    
    // 如果需要更多颜色，就随机生成
    const result = [...colors];
    for (let i = colors.length; i < count; i++) {
        const r = Math.floor(Math.random() * 200);
        const g = Math.floor(Math.random() * 200);
        const b = Math.floor(Math.random() * 200);
        result.push(`rgb(${r}, ${g}, ${b})`);
    }
    
    return result;
} 