/**
 * 固定深色模式 CSS 加载器
 * 通过 <link> 标签加载 dark-mode.css，被 dark-mode-toggle.js 动态调用
 * CSS 文件位置：scripts/css/dark-mode.css
 */
(function() {
    'use strict';

    var styleId = 'dark-mode-fixed-styles';

    // 已注入过则跳过
    if (document.getElementById(styleId)) return;

    // 从自身 script 路径推算 CSS 路径
    // dark-mode.js → css/dark-mode.css
    var scriptSrc = document.currentScript
        ? document.currentScript.src
        : '';
    var cssHref = scriptSrc.replace(/dark-mode\.js(\?.*)?$/, 'css/dark-mode.css');

    var link = document.createElement('link');
    link.id = styleId;
    link.rel = 'stylesheet';
    link.href = cssHref;
    document.head.appendChild(link);
})();
