/**
 * 深色模式三模式切换控制器
 * 模式循环: 🌞 原色 → 🌙 固定深色 → ⚡ 智能深色 → 🌞 ...
 * 自动加载 dark-mode.js (固定样式) 和 smart-dark-mode.js (智能算法)
 */
(function() {
    'use strict';

    const STORAGE_KEY = 'unified-dark-mode';
    const MODES = ['light', 'fixed', 'smart'];
    const ICONS = { light: '\u2600', fixed: '\u263D', smart: '\u26A1' };
    const TITLES = {
        light: '原色模式 (点击切换固定深色)',
        fixed: '固定深色 (点击切换智能深色)',
        smart: '智能深色 (点击切换原色)'
    };

    let currentMode = 'light';
    let loaded = { fixed: false, smart: false };

    // 获取 toggle 脚本所在的基础路径
    function getBasePath() {
        const el = document.querySelector('script[src*="dark-mode-toggle"]');
        if (!el) return '';
        const src = el.getAttribute('src');
        // 如果是相对路径如 ../../dark-mode-toggle.js，保留 ../ 部分
        const lastSlash = src.lastIndexOf('/');
        return lastSlash >= 0 ? src.substring(0, lastSlash + 1) : '';
    }

    // 动态加载外部脚本
    function loadScript(url) {
        return new Promise((resolve, reject) => {
            // 检查是否已加载
            const existing = document.querySelector('script[src="' + url + '"]');
            if (existing) { resolve(); return; }
            const s = document.createElement('script');
            s.src = url;
            s.onload = resolve;
            s.onerror = reject;
            document.head.appendChild(s);
        });
    }

    // 确保固定深色样式已加载
    async function ensureFixed() {
        if (loaded.fixed) return;
        await loadScript(getBasePath() + 'dark-mode.js');
        loaded.fixed = true;
    }

    // 确保智能深色算法已加载
    async function ensureSmart() {
        if (loaded.smart) return;
        await loadScript(getBasePath() + 'smart-dark-mode.js');
        loaded.smart = true;
    }

    // 应用指定模式
    async function applyMode(mode) {
        const html = document.documentElement;

        // 清除所有深色标记
        html.removeAttribute('data-unified-mode');
        html.removeAttribute('data-theme');
        document.body.classList.remove('dark-mode');

        if (mode === 'light') {
            // 原色模式：什么都不做
            if (window.SmartDarkMode) window.SmartDarkMode.disable();
        }
        else if (mode === 'fixed') {
            await ensureFixed();
            html.setAttribute('data-unified-mode', 'fixed');
            html.setAttribute('data-theme', 'dark');
            document.body.classList.add('dark-mode');
            if (window.SmartDarkMode) window.SmartDarkMode.disable();
        }
        else if (mode === 'smart') {
            await ensureSmart();
            html.setAttribute('data-unified-mode', 'smart');
            html.setAttribute('data-theme', 'dark');
            document.body.classList.add('dark-mode');
            if (window.SmartDarkMode) window.SmartDarkMode.enable();
        }

        updateButton(mode);
    }

    // 切换到下一个模式
    function nextMode() {
        const idx = MODES.indexOf(currentMode);
        currentMode = MODES[(idx + 1) % MODES.length];
        applyMode(currentMode);
        try { localStorage.setItem(STORAGE_KEY, currentMode); } catch (e) {}
    }

    // 创建切换按钮
    function createButton() {
        if (document.getElementById('unified-dark-toggle')) return;
        const btn = document.createElement('button');
        btn.id = 'unified-dark-toggle';
        btn.setAttribute('aria-label', '切换主题模式');
        Object.assign(btn.style, {
            position: 'fixed',
            top: '16px',
            right: '16px',
            zIndex: '99999',
            width: '42px',
            height: '42px',
            borderRadius: '50%',
            border: 'none',
            background: 'rgba(128,128,128,0.2)',
            color: 'inherit',
            fontSize: '18px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.3s ease',
            backdropFilter: 'blur(4px)',
            userSelect: 'none'
        });
        btn.addEventListener('click', nextMode);
        document.body.appendChild(btn);
    }

    // 更新按钮外观
    function updateButton(mode) {
        const btn = document.getElementById('unified-dark-toggle');
        if (!btn) return;
        btn.textContent = ICONS[mode] || '\u2600';
        btn.title = TITLES[mode] || '切换主题';
        if (mode === 'light') {
            btn.style.background = 'rgba(128,128,128,0.2)';
            btn.style.color = 'inherit';
        } else {
            btn.style.background = 'rgba(255,255,255,0.15)';
            btn.style.color = '#b8bfc6';
        }
    }

    // 初始化
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        createButton();

        // 读取保存的偏好
        let saved = null;
        try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) {}

        // 兼容旧数据: 'dark'/'light' 是旧的二元存储
        if (saved === 'dark') saved = 'fixed';

        currentMode = MODES.includes(saved) ? saved : 'light';
        applyMode(currentMode);
    }

    init();
})();
