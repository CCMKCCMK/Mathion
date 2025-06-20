/**
 * 全局配置文件
 * 包含API基础URL和其他应用设置
 */

// API配置
const CONFIG = {
    // API基础URL，所有API请求将使用此URL作为前缀
    API_BASE_URL: "https://www.jerrykongzzz.top",
    // API_BASE_URL: "http://172.31.228.41:7001", // 使用主域名下的api路径
    // 注释掉旧的URL配置
    // API_BASE_URL: "https://frp-fit.com:14569", 
    
    // 其他全局设置
    APP_VERSION: "1.0.6",
    DEBUG_MODE: false,
    
    // 超时设置（毫秒）
    REQUEST_TIMEOUT: 10000,
};