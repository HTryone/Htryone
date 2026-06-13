/**
 * 智能深色模式算法库
 * 被 dark-mode-toggle.js 动态加载
 * 使用: SmartDarkMode.enable() / SmartDarkMode.disable()
 */
window.SmartDarkMode = (function() {
    'use strict';

    let smartStyleEl = null;
    let elementsMarked = false;

    // ========== 颜色工具 ==========
    function rgbToHsl(r, g, b) {
        r /= 255; g /= 255; b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;
        if (max === min) { h = s = 0; }
        else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
                case g: h = ((b - r) / d + 2) / 6; break;
                case b: h = ((r - g) / d + 4) / 6; break;
            }
        }
        return { h: h * 360, s: s * 100, l: l * 100 };
    }

    function hslToRgb(h, s, l) {
        h /= 360; s /= 100; l /= 100;
        let r, g, b;
        if (s === 0) { r = g = b = l; }
        else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1; if (t > 1) t -= 1;
                if (t < 1/6) return p + (q - p) * 6 * t;
                if (t < 1/2) return q;
                if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
            };
            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1/3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1/3);
        }
        return { r: Math.round(r * 255), g: Math.round(g * 255), b: Math.round(b * 255) };
    }

    function parseColor(colorStr) {
        if (!colorStr || colorStr === 'transparent' || colorStr === 'none') return null;
        const div = document.createElement('div');
        div.style.color = colorStr;
        document.body.appendChild(div);
        const computed = getComputedStyle(div).color;
        document.body.removeChild(div);
        const match = computed.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
        if (!match) return null;
        return { r: parseInt(match[1]), g: parseInt(match[2]), b: parseInt(match[3]), a: match[4] ? parseFloat(match[4]) : 1 };
    }

    function colorToString(rgb) {
        if (rgb.a < 1) return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${rgb.a})`;
        return `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
    }

    function convertToDark(colorStr, type) {
        const rgb = parseColor(colorStr);
        if (!rgb) return null;
        const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
        let nh = { ...hsl };
        if (type === 'background') {
            nh.l = Math.max(5, Math.min(25, (100 - hsl.l) * 0.3));
            nh.s = Math.min(hsl.s * 0.7, 30);
        } else if (type === 'text') {
            if (hsl.l < 50) {
                nh.l = Math.min(90, 70 + (50 - hsl.l) * 0.5);
                nh.s = Math.min(hsl.s, 40);
            } else {
                nh.l = Math.max(75, hsl.l - 10);
            }
        } else if (type === 'border') {
            nh.l = Math.max(15, Math.min(40, (100 - hsl.l) * 0.4));
            nh.s = Math.min(hsl.s * 0.5, 25);
        }
        const nr = hslToRgb(nh.h, nh.s, nh.l);
        return colorToString({ ...nr, a: rgb.a });
    }

    // ========== 标记原色 ==========
    function markOriginalColors() {
        if (elementsMarked) return;
        const all = document.querySelectorAll('body *');
        for (const el of all) {
            if (el.id === 'unified-dark-toggle' || el.matches('script,style,iframe,video,canvas,svg,img')) continue;
            const cs = getComputedStyle(el);
            const bg = cs.backgroundColor;
            if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') el.setAttribute('data-orig-bg', bg);
            const c = cs.color;
            if (c) el.setAttribute('data-orig-color', c);
            const b = cs.borderColor;
            if (b && b !== 'rgba(0, 0, 0, 0)') el.setAttribute('data-orig-border', b);
        }
        elementsMarked = true;
    }

    // ========== 生成动态样式 ==========
    function generateSmartStyles() {
        const rules = [];
        const done = new Set();
        const all = document.querySelectorAll('body *');
        const bgColors = new Set(), textColors = new Set(), borderColors = new Set();

        for (const el of all) {
            if (el.id === 'unified-dark-toggle' || el.matches('script,style,iframe,video,canvas,svg,img')) continue;
            const rect = el.getBoundingClientRect();
            if (rect.width === 0 && rect.height === 0) continue;
            const cs = getComputedStyle(el);
            const bg = cs.backgroundColor;
            if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') bgColors.add(bg);
            const c = cs.color;
            if (c) textColors.add(c);
            const b = cs.borderColor;
            if (b && b !== 'rgba(0, 0, 0, 0)') borderColors.add(b);
        }

        for (const color of bgColors) {
            if (done.has('bg:' + color)) continue;
            done.add('bg:' + color);
            const dark = convertToDark(color, 'background');
            if (dark) rules.push(`[data-unified-mode="smart"] [data-orig-bg="${color}"] { background-color: ${dark} !important; }`);
        }
        for (const color of textColors) {
            if (done.has('t:' + color)) continue;
            done.add('t:' + color);
            const dark = convertToDark(color, 'text');
            if (dark) rules.push(`[data-unified-mode="smart"] [data-orig-color="${color}"] { color: ${dark} !important; }`);
        }
        for (const color of borderColors) {
            if (done.has('b:' + color)) continue;
            done.add('b:' + color);
            const dark = convertToDark(color, 'border');
            if (dark) rules.push(`[data-unified-mode="smart"] [data-orig-border="${color}"] { border-color: ${dark} !important; }`);
        }
        return rules.join('\n');
    }

    // ========== 公共 API ==========
    function enable() {
        markOriginalColors();
        if (!smartStyleEl) {
            const css = generateSmartStyles();
            smartStyleEl = document.createElement('style');
            smartStyleEl.id = 'smart-dark-styles';
            smartStyleEl.textContent = `
                [data-unified-mode="smart"] { background-color: #0a0a0f !important; }
                [data-unified-mode="smart"] body { background-color: #0a0a0f !important; }
                [data-unified-mode="smart"] * { background-image: none !important; box-shadow: none !important; }
                [data-unified-mode="smart"] #write table tbody tr:hover td,
                [data-unified-mode="smart"] #write table tbody tr:hover th {
                    background-color: rgba(255, 255, 255, 0.05) !important;
                }
                [data-unified-mode="smart"] .typora-export-sidebar .outline-item:hover,
                [data-unified-mode="smart"] .outline-item:hover {
                    background-color: rgba(255, 255, 255, 0.08) !important;
                    color: rgba(255, 255, 255, 0.8) !important;
                }
                [data-unified-mode="smart"] #write a:hover {
                    background-color: rgba(255, 255, 255, 0.08) !important;
                }
                [data-unified-mode="smart"] ::selection {
                    background-color: rgba(180,180,180,0.10) !important;
                    color: inherit !important;
                }
                ${css}
            `;
            document.head.appendChild(smartStyleEl);
        }
        document.documentElement.setAttribute('data-unified-mode', 'smart');
    }

    function disable() {
        // 只移除标记，样式保留以便下次快速启用
        // 实际清除由 toggle 控制器处理
    }

    return { enable, disable };
})();
