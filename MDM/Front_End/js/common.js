/**
 * 公共工具函数
 */

// 获取URL查询参数
function getQueryParam(param) {
    var search = window.location.search.substring(1);
    var params = search.split("&");
    for (var i = 0; i < params.length; i++) {
        var pair = params[i].split("=");
        if (pair[0] === param) {
            return decodeURIComponent(pair[1]);
        }
    }
    return null;
}

// 发送AJAX请求的标准函数
function sendAjaxRequest(endpoint, method, data, successCallback, errorCallback) {
    // 拼接完整的API URL
    var url = CONFIG.API_BASE_URL + endpoint;
    $.ajax({
        url: url,
        type: method,
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        timeout: CONFIG.REQUEST_TIMEOUT,
        crossDomain: true,
        xhrFields: {withCredentials: true},
        success: function(response) {
            console.log(response);
            // 检查会话状态
            if (response.code === 401) {
                // 会话过期，重定向到登录页面
                sessionStorage.clear();
                window.location.href = "\\";
                return;
            }
            if (successCallback) {
                successCallback(response);
            }
        },
        error: function(error) {
            console.error("AJAX request error:", error);
            if (errorCallback) {
                errorCallback(error);
            }
        }
    });
}

// 显示成功消息
function showSuccessMessage(message) {
    if (typeof layer !== 'undefined') {
        layer.msg(message);
    } else {
        alert(message);
    }
}

// 显示错误消息
function showErrorMessage(message) {
    if (typeof layer !== 'undefined') {
        layer.alert(message);
    } else {
        alert("Error: " + message);
    }
} 