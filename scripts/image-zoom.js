/**
 * 图片点击放大灯箱 (Image Zoom Lightbox)
 * 点击页面中的图片即可放大悬浮查看，支持动画过渡、ESC/点击关闭、移动端适配
 *
 * 用法：在 HTML 的 </body> 前引入此脚本即可
 *   <script src="路径/scripts/image-zoom.js"></script>
 */
(function() {
    'use strict';

    // 防止重复初始化
    if (window.__imageZoomInitialized) return;
    window.__imageZoomInitialized = true;

    // ==================== 辅助函数 ====================

    // 判断图片是否太小（图标/装饰图，不放大）
    function isTooSmall(img) {
        var w = img.naturalWidth || img.width || 0;
        var h = img.naturalHeight || img.height || 0;
        // 一侧小于 50 且另一侧也小于 100 → 跳过
        if (w > 0 && h > 0 && (w < 50 || h < 50) && w < 100 && h < 100) return true;
        // 尺寸未知 → 不跳过（可能还未加载）
        return false;
    }

    // 判断是否在非图片链接内（跳转链接的缩略图不拦截）
    function isInsideNonImageLink(img) {
        var el = img;
        while (el) {
            if (el.tagName === 'A' && el.getAttribute('href')) {
                var href = el.getAttribute('href');
                if (href.indexOf('#') === 0) return false; // 锚点链接放行
                return !/\.(png|jpg|jpeg|gif|webp|svg|bmp|ico)$/i.test(href);
            }
            // 向上查 3 层，超出不查（性能）
            el = el.parentElement;
            if (el === document.body) break;
        }
        return false;
    }

    // 判断点击目标是否是"可放大图片"
    function isValidZoomTarget(img) {
        if (!img || img.tagName !== 'IMG') return false;
        // 跳过灯箱自身的大图
        if (img.closest && img.closest('#iz-overlay')) return false;
        if (img.parentElement && img.parentElement.id === 'iz-overlay') return false;
        // 跳过太小的图标
        if (isTooSmall(img)) return false;
        // 跳过非图片链接
        if (isInsideNonImageLink(img)) return false;
        return true;
    }

    // ==================== DOM 构建 ====================

    // 创建遮罩层
    var overlay = document.createElement('div');
    overlay.id = 'iz-overlay';
    overlay.setAttribute('aria-hidden', 'true');
    overlay.innerHTML =
        '<div class="iz-bg"></div>' +
        '<button class="iz-close" aria-label="关闭">&times;</button>' +
        '<div class="iz-container">' +
            '<img class="iz-image" src="" alt="">' +
            '<div class="iz-caption"></div>' +
        '</div>';

    // 注入样式
    var style = document.createElement('style');
    style.textContent = [
        '#iz-overlay {',
        '  position: fixed; top: 0; left: 0; width: 100%; height: 100%;',
        '  z-index: 99999; display: flex; align-items: center; justify-content: center;',
        '  opacity: 0; pointer-events: none;',
        '  transition: opacity 0.3s ease;',
        '}',
        '#iz-overlay.active {',
        '  opacity: 1; pointer-events: auto;',
        '}',
        '#iz-overlay .iz-bg {',
        '  position: absolute; inset: 0;',
        '  background: rgba(0, 0, 0, 0.88);',
        '}',
        '#iz-overlay .iz-container {',
        '  position: relative; z-index: 1;',
        '  display: flex; flex-direction: column; align-items: center;',
        '  max-width: 94vw; max-height: 94vh;',
        '}',
        '#iz-overlay .iz-image {',
        '  max-width: 94vw; max-height: 88vh;',
        '  object-fit: contain;',
        '  border-radius: 8px;',
        '  box-shadow: 0 20px 60px rgba(0,0,0,0.5);',
        '  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);',
        '  cursor: zoom-out;',
        '  user-select: none;',
        '  -webkit-user-drag: none;',
        '}',
        '#iz-overlay .iz-image.animating {',
        '  transform: scale(0.3);',
        '}',
        '#iz-overlay.active .iz-image {',
        '  transform: scale(1);',
        '}',
        '#iz-overlay .iz-caption {',
        '  color: rgba(255,255,255,0.7); font-size: 13px;',
        '  margin-top: 12px; text-align: center;',
        '  max-width: 90vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;',
        '}',
        '#iz-overlay .iz-close {',
        '  position: fixed; top: 20px; right: 20px;',
        '  width: 40px; height: 40px; z-index: 1;',
        '  display: flex; align-items: center; justify-content: center;',
        '  background: rgba(255,255,255,0.12); border: none; border-radius: 50%;',
        '  color: #fff; font-size: 22px;',
        '  cursor: pointer; transition: background 0.2s;',
        '  user-select: none;',
        '}',
        '#iz-overlay .iz-close:hover {',
        '  background: rgba(255,255,255,0.25);',
        '}',
        /* 移动端适配 */
        '@media (max-width: 600px) {',
        '  #iz-overlay .iz-container { max-width: 98vw; max-height: 96vh; }',
        '  #iz-overlay .iz-image { max-width: 98vw; max-height: 80vh; }',
        '  #iz-overlay .iz-close { top: 12px; right: 12px; width: 36px; height: 36px; font-size: 18px; }',
        '}'
    ].join('\n');

    // ==================== 状态 ====================

    var currentImg = null;
    var isOpen = false;

    // ==================== 打开灯箱 ====================

    function open(imgEl) {
        if (isOpen) return;
        isOpen = true;
        currentImg = imgEl;

        var overlayImg = overlay.querySelector('.iz-image');
        var caption    = overlay.querySelector('.iz-caption');

        overlayImg.src = imgEl.src;
        overlayImg.alt = imgEl.alt || '';
        overlayImg.classList.add('animating');

        var title = imgEl.alt || imgEl.title || '';
        caption.textContent = title;

        document.body.style.overflow = 'hidden';
        document.body.appendChild(overlay);

        requestAnimationFrame(function() {
            requestAnimationFrame(function() {
                overlay.classList.add('active');
                overlayImg.classList.remove('animating');
            });
        });

        overlay.setAttribute('aria-hidden', 'false');
        overlayImg.focus();
    }

    // ==================== 关闭灯箱 ====================

    function close() {
        if (!isOpen) return;
        isOpen = false;

        var overlayImg = overlay.querySelector('.iz-image');
        overlayImg.classList.add('animating');
        overlay.classList.remove('active');

        var onTransitionEnd = function() {
            overlayImg.removeEventListener('transitionend', onTransitionEnd);
            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
            document.body.style.overflow = '';
            overlay.setAttribute('aria-hidden', 'true');
            currentImg = null;
        };
        overlayImg.addEventListener('transitionend', onTransitionEnd);

        // 兜底：reduced motion 等场景
        setTimeout(function() {
            if (overlay.parentNode && !isOpen) {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
                document.body.style.overflow = '';
                overlay.setAttribute('aria-hidden', 'true');
            }
        }, 400);
    }

    // ==================== 事件绑定 ====================

    overlay.querySelector('.iz-close').addEventListener('click', function(e) {
        e.stopPropagation();
        close();
    });

    overlay.querySelector('.iz-bg').addEventListener('click', close);

    overlay.querySelector('.iz-image').addEventListener('click', close);

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isOpen) {
            close();
        }
    });

    // ★ 核心改动：事件委托，捕获阶段统一拦截，不再逐个绑定
    document.addEventListener('click', function(e) {
        var img = e.target;
        if (!isValidZoomTarget(img)) return;

        e.preventDefault();
        e.stopPropagation();
        open(img);
    }, true); // true = 捕获阶段，比子元素的 click 先触发

    // ==================== CSS 注入 ====================

    function injectStyles() {
        if (document.getElementById('iz-styles')) return;
        style.id = 'iz-styles';
        if (document.head) {
            document.head.appendChild(style);
        } else {
            document.addEventListener('DOMContentLoaded', function() {
                document.head.appendChild(style);
            });
        }
    }

    injectStyles();
})();
