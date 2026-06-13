/**
 * 固定深色模式样式 (Typora 导出页面专用)
 * 被 dark-mode-toggle.js 动态加载
 * 选择器: [data-unified-mode="fixed"]
 */
(function() {
    'use strict';
    if (document.getElementById('dark-mode-fixed-styles')) return;

    const style = document.createElement('style');
    style.id = 'dark-mode-fixed-styles';
    style.textContent = `
        /* ===== 固定深色模式 - Typora 导出页面适配 ===== */

        /* 基础变量 */
        [data-unified-mode="fixed"] {
            --bg-color: #0a0a0f !important;
            --text-color: #b8bfc6 !important;
            --select-text-bg-color: transparent !important;
            --select-text-font-color: inherit !important;
        }

        /* 页面背景 */
        [data-unified-mode="fixed"] html {
            background-color: #0a0a0f !important;
        }
        [data-unified-mode="fixed"] body {
            background-color: #0a0a0f !important;
            color: #b8bfc6 !important;
        }

        /* 选中文字 */
        [data-unified-mode="fixed"] ::selection {
            background-color: transparent !important;
            color: inherit !important;
        }
        [data-unified-mode="fixed"] ::-moz-selection {
            background-color: transparent !important;
            color: inherit !important;
        }

        /* 全局关阴影 + 超链接 hover */
        [data-unified-mode="fixed"] * { box-shadow: none !important; }
        [data-unified-mode="fixed"] #write a:hover { background-color: rgba(255,255,255,0.08) !important; }

        /* 内容区域 */
        [data-unified-mode="fixed"] #write {
            background-color: #0a0a0f !important;
        }

        /* 标题 */
        [data-unified-mode="fixed"] #write h1,
        [data-unified-mode="fixed"] #write h2,
        [data-unified-mode="fixed"] #write h3,
        [data-unified-mode="fixed"] #write h4,
        [data-unified-mode="fixed"] #write h5,
        [data-unified-mode="fixed"] #write h6 {
            color: #dedede !important;
        }

        /* 段落和正文 */
        [data-unified-mode="fixed"] #write p,
        [data-unified-mode="fixed"] #write li {
            color: #b8bfc6 !important;
        }

        /* 链接 */
        [data-unified-mode="fixed"] #write a {
            color: #7ec8ff !important;
        }
        [data-unified-mode="fixed"] #write a:hover {
            color: #a8ddff !important;
        }

        /* 代码块 - 深黑背景 */
        [data-unified-mode="fixed"] #write pre,
        [data-unified-mode="fixed"] #write pre.md-fences {
            background-color: #0d1117 !important;
            border-color: #30363d !important;
        }
        [data-unified-mode="fixed"] #write pre .CodeMirror,
        [data-unified-mode="fixed"] #write pre .CodeMirror-scroll,
        [data-unified-mode="fixed"] #write pre .CodeMirror-sizer,
        [data-unified-mode="fixed"] #write pre .CodeMirror-lines,
        [data-unified-mode="fixed"] #write pre .CodeMirror-code {
            background-color: #0d1117 !important;
        }
        [data-unified-mode="fixed"] #write pre .CodeMirror-activeline-background,
        [data-unified-mode="fixed"] #write pre .CodeMirror-linebackground {
            background-color: #161b22 !important;
        }
        [data-unified-mode="fixed"] #write pre code {
            background-color: transparent !important;
            color: #b8bfc6;
        }
        [data-unified-mode="fixed"] #write pre .CodeMirror-line {
            background-color: transparent !important;
            color: #b8bfc6 !important;
        }
        /* 语法高亮 */
        [data-unified-mode="fixed"] #write pre .cm-comment { color: #f0a050 !important; }
        [data-unified-mode="fixed"] #write pre .cm-string { color: #ff7b72 !important; }
        [data-unified-mode="fixed"] #write pre .cm-keyword { color: #ff7b72 !important; }
        [data-unified-mode="fixed"] #write pre .cm-property,
        [data-unified-mode="fixed"] #write pre .cm-variable { color: #79c0ff !important; }
        [data-unified-mode="fixed"] #write pre .cm-number { color: #79c0ff !important; }
        [data-unified-mode="fixed"] #write pre .cm-tag { color: #7ee787 !important; }
        [data-unified-mode="fixed"] #write pre .cm-attribute { color: #79c0ff !important; }
        [data-unified-mode="fixed"] #write pre .cm-operator { color: #ff7b72 !important; }
        [data-unified-mode="fixed"] #write pre .cm-atom { color: #ff7b72 !important; }

        /* 普通 HTML 代码块 */
        [data-unified-mode="fixed"] pre:not(#write pre) {
            background-color: #0d1117 !important;
            border: 1px solid #30363d !important;
            border-radius: 5px;
            padding: 15px;
        }
        [data-unified-mode="fixed"] pre:not(#write pre) code {
            background-color: transparent !important;
            color: #b8bfc6 !important;
        }

        /* 行内代码 */
        [data-unified-mode="fixed"] #write code:not(pre code) {
            background-color: #21262d !important;
            color: #d0d0d0 !important;
            border-color: #30363d !important;
        }

        /* 引用块 */
        [data-unified-mode="fixed"] #write blockquote {
            background-color: #252535 !important;
            border-left-color: #6dc1e7 !important;
            color: #b8bfc6 !important;
        }

        /* 表格 */
        [data-unified-mode="fixed"] #write table {
            background-color: #1e1e2f !important;
        }
        [data-unified-mode="fixed"] #write th,
        [data-unified-mode="fixed"] #write td {
            border-color: #4a4a5e !important;
            color: #b8bfc6 !important;
        }
        [data-unified-mode="fixed"] #write th {
            background-color: #2d2d3a !important;
        }
        [data-unified-mode="fixed"] #write tr:nth-child(even) {
            background-color: #242436 !important;
        }
        [data-unified-mode="fixed"] #write table tbody tr:hover td,
        [data-unified-mode="fixed"] #write table tbody td:hover {
            background-color: #1a1a28 !important;
            color: #b8bfc6 !important;
            box-shadow: none !important;
        }

        /* 水平线 */
        [data-unified-mode="fixed"] #write hr {
            border-color: #4a4a5e !important;
        }

        /* 图片 */
        [data-unified-mode="fixed"] #write img {
            opacity: 0.92;
        }

        /* 侧边栏大纲 */
        [data-unified-mode="fixed"] .typora-export-sidebar {
            background-color: #2e3033 !important;
            border-right-color: #404050 !important;
        }
        [data-unified-mode="fixed"] .outline-content .outline-item-wrapper {
            background-color: transparent !important;
        }
        [data-unified-mode="fixed"] .outline-content .outline-label {
            color: #b8bfc6 !important;
        }
        [data-unified-mode="fixed"] .outline-content .outline-item:hover {
            background-color: rgba(255,255,255,0.05) !important;
        }
        [data-unified-mode="fixed"] .outline-content .outline-item-active > .outline-item > .outline-label {
            color: #6dc1e7 !important;
            background-color: rgba(109,193,231,0.12) !important;
        }
        [data-unified-mode="fixed"] .outline-content .outline-expander {
            color: #888 !important;
        }
        [data-unified-mode="fixed"] .outline-content .outline-expander:hover {
            color: #b8bfc6 !important;
        }
        [data-unified-mode="fixed"] .typora-export-sidebar ::-webkit-scrollbar {
            width: 6px;
        }
        [data-unified-mode="fixed"] .typora-export-sidebar ::-webkit-scrollbar-track {
            background: #2e3033;
        }
        [data-unified-mode="fixed"] .typora-export-sidebar ::-webkit-scrollbar-thumb {
            background: #505050;
            border-radius: 3px;
        }
        [data-unified-mode="fixed"] .outline-content {
            background-color: #2e3033 !important;
        }

        /* 滚动条 */
        [data-unified-mode="fixed"] ::-webkit-scrollbar {
            width: 8px; height: 8px;
        }
        [data-unified-mode="fixed"] ::-webkit-scrollbar-track {
            background: #0a0a0f;
        }
        [data-unified-mode="fixed"] ::-webkit-scrollbar-thumb {
            background: #505060;
            border-radius: 4px;
        }
        [data-unified-mode="fixed"] ::-webkit-scrollbar-thumb:hover {
            background: #70717d;
        }
    `;
    document.head.appendChild(style);
})();
