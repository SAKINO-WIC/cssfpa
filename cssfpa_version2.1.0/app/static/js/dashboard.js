// 仪表板数据可视化JavaScript
console.log('开始加载dashboard.js');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM加载完成，初始化仪表板');
    
    // 打印出所有数据元素
    const dataElements = document.querySelectorAll('[id$="-data"]');
    console.log(`找到 ${dataElements.length} 个数据元素`);
    dataElements.forEach(el => {
        try {
            const data = JSON.parse(el.textContent);
            console.log(`${el.id} 内容:`, data);
        } catch (e) {
            console.error(`解析 ${el.id} 数据时出错:`, e);
            console.log(`${el.id} 原始内容:`, el.textContent);
        }
    });
    
    // 基础配置
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                font: {
                    size: 16
                }
            }
        }
    };

    // 性别分布饼图
    if(document.getElementById('genderChart')) {
        const genderData = JSON.parse(document.getElementById('gender-data').textContent);
        new Chart(document.getElementById('genderChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: ['男', '女'],
                datasets: [{
                    data: [genderData.male, genderData.female],
                    backgroundColor: ['#36a2eb', '#ff6384']
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '学生性别分布'
                    }
                }
            }
        });
    }

    // 政治面貌分布图
    if(document.getElementById('politicalStatusChart')) {
        const politicalData = JSON.parse(document.getElementById('political-data').textContent);
        const labels = Object.keys(politicalData);
        const data = Object.values(politicalData);
        const backgroundColors = generateColors(labels.length);

        new Chart(document.getElementById('politicalStatusChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '学生数量',
                    data: data,
                    backgroundColor: backgroundColors
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '政治面貌分布'
                    }
                }
            }
        });
    }

    // 班级分布图
    if(document.getElementById('classDistributionChart')) {
        const classData = JSON.parse(document.getElementById('class-data').textContent);
        const labels = Object.keys(classData);
        const data = Object.values(classData);
        const backgroundColors = generateColors(labels.length);

        new Chart(document.getElementById('classDistributionChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '学生数量',
                    data: data,
                    backgroundColor: backgroundColors
                }]
            },
            options: {
                ...chartOptions,
                indexAxis: 'y',
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '班级分布'
                    }
                }
            }
        });
    }

    // 入党申请趋势图
    if(document.getElementById('applicationTrendChart')) {
        const trendData = JSON.parse(document.getElementById('trend-data').textContent);
        const dates = Object.keys(trendData);
        const counts = Object.values(trendData);

        new Chart(document.getElementById('applicationTrendChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: '申请人数',
                    data: counts,
                    borderColor: '#4bc0c0',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '入党申请趋势'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    // 系部分布图
    if(document.getElementById('departmentChart')) {
        const deptData = JSON.parse(document.getElementById('department-data').textContent);
        const labels = Object.keys(deptData);
        const data = Object.values(deptData);
        const backgroundColors = generateColors(labels.length);

        new Chart(document.getElementById('departmentChart').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColors
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '系部分布'
                    }
                }
            }
        });
    }

    // 考试通过率图
    if(document.getElementById('examPassRateChart')) {
        const examData = JSON.parse(document.getElementById('exam-data').textContent);
        
        new Chart(document.getElementById('examPassRateChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: ['通过', '未通过', '未参加'],
                datasets: [{
                    data: [examData.passed, examData.failed, examData.not_taken],
                    backgroundColor: ['#4bc0c0', '#ff6384', '#9966ff']
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '考试通过率'
                    }
                }
            }
        });
    }

    // 综合成绩分布图
    if(document.getElementById('scoreDistributionChart')) {
        const scoreData = JSON.parse(document.getElementById('score-data').textContent);
        
        new Chart(document.getElementById('scoreDistributionChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['90分以上', '80-89分', '70-79分', '60-69分', '60分以下', '未评分'],
                datasets: [{
                    label: '学生数量',
                    data: [
                        scoreData.excellent, 
                        scoreData.good, 
                        scoreData.average, 
                        scoreData.pass, 
                        scoreData.fail,
                        scoreData.not_graded
                    ],
                    backgroundColor: [
                        '#4bc0c0', 
                        '#36a2eb', 
                        '#ffcd56', 
                        '#ff9f40', 
                        '#ff6384',
                        '#9966ff'
                    ]
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '综合成绩分布'
                    }
                }
            }
        });
    }

    // 入党申请情况图表
    if(document.getElementById('applicationStatusChart')) {
        const appData = JSON.parse(document.getElementById('application-data').textContent);
        
        new Chart(document.getElementById('applicationStatusChart').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['已提交申请', '未提交申请'],
                datasets: [{
                    data: [appData.submitted, appData.not_submitted],
                    backgroundColor: ['#4bc0c0', '#ff6384']
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '入党申请情况'
                    }
                }
            }
        });
    }

    // 班级推优状态图
    if(document.getElementById('approvalChart')) {
        const approvalData = JSON.parse(document.getElementById('class-approved-data').textContent);
        
        new Chart(document.getElementById('approvalChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: ['已通过班级推优', '未通过班级推优'],
                datasets: [{
                    data: [approvalData.approved, approvalData.not_approved],
                    backgroundColor: ['#36a2eb', '#ff6384']
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '班级推优状态'
                    }
                }
            }
        });
    }

    // 挂科情况图表
    if(document.getElementById('failedCourseChart')) {
        const failedCourseData = JSON.parse(document.getElementById('failed-course-data').textContent);
        
        new Chart(document.getElementById('failedCourseChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: ['有不及格课程', '无不及格课程'],
                datasets: [{
                    data: [failedCourseData.failed, failedCourseData.not_failed],
                    backgroundColor: ['#ff6384', '#4bc0c0']
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '学生挂科情况分析'
                    }
                }
            }
        });
    }

    // 志愿服务时长分布图
    if(document.getElementById('volunteerHoursChart')) {
        // 从数据元素中获取数据
        const volunteerDataElement = document.getElementById('volunteer-data');
        if(volunteerDataElement) {
            const volunteerInfo = JSON.parse(volunteerDataElement.textContent);
            
            new Chart(document.getElementById('volunteerHoursChart').getContext('2d'), {
                type: 'bar',
                data: {
                    labels: volunteerInfo.labels,
                    datasets: [{
                        label: '学生数量',
                        data: volunteerInfo.data,
                        backgroundColor: generateColors(volunteerInfo.labels.length)
                    }]
                },
                options: {
                    ...chartOptions,
                    plugins: {
                        ...chartOptions.plugins,
                        title: {
                            ...chartOptions.plugins.title,
                            text: '志愿服务时长分布'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        }
    }

    // 英语等级考试情况图表
    if(document.getElementById('englishLevelChart')) {
        // 尝试从隐藏元素获取数据
        let englishLabels = ['CET4及格', 'CET4不及格', 'CET6及格', 'CET6不及格', '未参加'];
        let englishData = [0, 0, 0, 0, 0]; // 默认数据
        
        // 从数据元素获取实际数据
        const englishDataElement = document.getElementById('english-data');
        if(englishDataElement) {
            try {
                const englishInfo = JSON.parse(englishDataElement.textContent);
                if(englishInfo.labels && englishInfo.labels.length > 0) {
                    englishLabels = englishInfo.labels;
                }
                if(englishInfo.data && englishInfo.data.length > 0) {
                    englishData = englishInfo.data;
                }
            } catch(e) {
                console.error('解析英语成绩数据出错:', e);
            }
        }
        
        new Chart(document.getElementById('englishLevelChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: englishLabels,
                datasets: [{
                    label: '学生数量',
                    data: englishData,
                    backgroundColor: generateColors(englishLabels.length)
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    title: {
                        ...chartOptions.plugins.title,
                        text: '英语等级考试情况'
                    }
                }
            }
        });
    }

    // 生成随机颜色数组
    function generateColors(count) {
        const colors = [
            '#4bc0c0', '#36a2eb', '#ffcd56', '#ff9f40', '#ff6384', 
            '#9966ff', '#c9cbcf', '#7cb5ec', '#f7a35c', '#90ed7d', 
            '#8085e9', '#f15c80', '#e4d354', '#8085e8', '#8d4653'
        ];
        
        // 如果预定义颜色不够，则生成随机颜色
        if (count > colors.length) {
            for (let i = colors.length; i < count; i++) {
                const r = Math.floor(Math.random() * 255);
                const g = Math.floor(Math.random() * 255);
                const b = Math.floor(Math.random() * 255);
                colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
            }
        }
        
        return colors.slice(0, count);
    }

    // 添加数据过滤功能
    const filterSelect = document.getElementById('dataFilterSelect');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            // 在这里实现数据过滤逻辑
            const selectedValue = this.value;
            // 根据选择更新图表数据
            updateChartsBasedOnFilter(selectedValue);
        });
    }

    // 数据过滤器实现
    function updateChartsBasedOnFilter(filter) {
        // 这里可以根据需要实现不同维度的数据过滤
        console.log('应用过滤器:', filter);
        // 在实际应用中，这里会通过AJAX获取过滤后的数据并更新图表
    }

    // 添加图表下载功能
    const downloadButtons = document.querySelectorAll('.chart-download-btn');
    if (downloadButtons.length > 0) {
        downloadButtons.forEach(button => {
            button.addEventListener('click', function() {
                const chartId = this.getAttribute('data-chart-id');
                const chartCanvas = document.getElementById(chartId);
                if (chartCanvas) {
                    const link = document.createElement('a');
                    link.download = `${chartId}-${new Date().toISOString().split('T')[0]}.png`;
                    link.href = chartCanvas.toDataURL('image/png');
                    link.click();
                }
            });
        });
    }

    // 安全地初始化工具提示，如果bootstrap存在
    try {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        } else {
            console.log('Bootstrap未加载，跳过Tooltip初始化');
        }
    } catch (e) {
        console.error('初始化Tooltip时出错:', e);
    }

    // 添加当前时间更新功能
    const currentTimeElement = document.getElementById('current-time');
    if (currentTimeElement) {
        const updateTime = () => {
            const now = new Date();
            currentTimeElement.textContent = now.toLocaleString('zh-CN');
        };
        updateTime();
        setInterval(updateTime, 1000);
    }
}); 