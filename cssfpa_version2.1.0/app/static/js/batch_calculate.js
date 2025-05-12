// 全局函数 - 全选/取消全选所有学生
function toggleAllCheckboxes(checkbox) {
    console.log("全选框被点击，新状态:", checkbox.checked);
    var studentCheckboxes = document.querySelectorAll('.student-checkbox');
    console.log("找到学生复选框数量:", studentCheckboxes.length);
    
    for (var i = 0; i < studentCheckboxes.length; i++) {
        studentCheckboxes[i].checked = checkbox.checked;
    }
}

// 更新全选框状态
function updateSelectAllCheckbox() {
    var studentCheckboxes = document.querySelectorAll('.student-checkbox');
    var selectAllCheckbox = document.getElementById('selectAll');
    
    if (!studentCheckboxes.length) return;
    
    var allChecked = true;
    for (var i = 0; i < studentCheckboxes.length; i++) {
        if (!studentCheckboxes[i].checked) {
            allChecked = false;
            break;
        }
    }
    
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = allChecked;
    }
}

// 计算所有筛选学生的分数
function calculateAllScores() {
    console.log("计算按钮被点击");
    
    // 显示加载指示器
    var calculateAllBtn = document.getElementById('calculateAllBtn');
    calculateAllBtn.disabled = true;
    calculateAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 计算中...';
    
    // 获取筛选表单
    var filterForm = document.getElementById('filterForm');
    if (!filterForm) {
        console.error("未找到筛选表单");
        return;
    }
    
    // 创建临时表单进行提交
    var tempForm = document.createElement('form');
    tempForm.method = 'GET';
    tempForm.action = window.location.pathname;
    
    // 复制所有现有字段
    var formElements = filterForm.elements;
    for (var i = 0; i < formElements.length; i++) {
        if (formElements[i].name) {
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = formElements[i].name;
            input.value = formElements[i].value;
            tempForm.appendChild(input);
        }
    }
    
    // 添加计算标记
    var calculateInput = document.createElement('input');
    calculateInput.type = 'hidden';
    calculateInput.name = 'calculate';
    calculateInput.value = '1';
    tempForm.appendChild(calculateInput);
    
    // 添加到文档并提交
    document.body.appendChild(tempForm);
    tempForm.submit();
}

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    console.log("批量计算页面初始化...");
    
    // 添加全选框事件
    var selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('click', function() {
            toggleAllCheckboxes(this);
        });
    }
    
    // 添加单个复选框事件
    var studentCheckboxes = document.querySelectorAll('.student-checkbox');
    for (var i = 0; i < studentCheckboxes.length; i++) {
        studentCheckboxes[i].addEventListener('click', updateSelectAllCheckbox);
    }
    
    // 初始化全选框状态
    updateSelectAllCheckbox();
    
    // 添加计算按钮事件
    var calculateAllBtn = document.getElementById('calculateAllBtn');
    if (calculateAllBtn) {
        calculateAllBtn.addEventListener('click', calculateAllScores);
    }
    
    // 保存选中按钮事件
    var saveSelectedBtn = document.getElementById('saveSelectedBtn');
    if (saveSelectedBtn) {
        saveSelectedBtn.addEventListener('click', function(event) {
            // 检查是否有选中的学生
            var checkedStudents = document.querySelectorAll('.student-checkbox:checked');
            if (checkedStudents.length === 0) {
                alert('请至少选择一名学生来保存评分结果');
                event.preventDefault();
                return false;
            }
            return true;
        });
    }
}); 