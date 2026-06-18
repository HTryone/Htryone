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

    // ==================== DOM 构建 ====================

    // 获取脚本所在目录（处理相对路径）
    function getScriptDir() {
        var scripts = document.getElementsByTagName('script');
        for (var i = scripts.length - 1; i >= 0; i--) {
            var src = scripts[i].src;
            if (src && src.indexOf('image-zoom.js') !== -1) {
                var lastSlash = src.lastIndexOf('/');
                return lastSlash >= 0 ? src.substring(0, lastSlash + 1) : '';
            }
        }
        return '';
    }

    var scriptDir = getScriptDir();

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
        '  background: rgba(255,255,255,0.12); border: none; border-radius: 50%;',
        '  color: #fff; font-size: 24px; line-height: 40px; text-align: center;',
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
        '  #iz-overlay .iz-close { top: 12px; right: 12px; width: 36px; height: 36px; font-size: 20px; line-height: 36px; }',
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

        // 设置大图
        overlayImg.src = imgEl.src;
        overlayImg.alt = imgEl.alt || '';
        overlayImg.classList.add('animating');

        // 设置标题
        var title = imgEl.alt || imgEl.title || '';
        caption.textContent = title;

        // 禁止背景滚动
        document.body.style.overflow = 'hidden';
        document.body.appendChild(overlay);

        // 触发动画
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

        // 动画结束后移除
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

        // 兜底：如果动画没触发 transitionend（如 reduced motion），强制移除
        setTimeout(function() {
            if (overlay.parentNode && !isOpen) {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
                document.body.style.overflow = '';
                overlay.setAttribute('aria-hidden', 'true');
            }
        }, 400);
    }

    // ==================== 事件绑定 ====================

    // 关闭按钮
    overlay.querySelector('.iz-close').addEventListener('click', function(e) {
        e.stopPropagation();
        close();
    });

    // 点击背景关闭
    overlay.querySelector('.iz-bg').addEventListener('click', close);

    // 点击大图也关闭（切换 zoom-out 光标暗示了这一点）
    overlay.querySelector('.iz-image').addEventListener('click', close);

    // ESC 键关闭
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isOpen) {
            close();
        }
    });

    // 绑定图片点击
    function bindImages() {
        // 主要扫描 #write 区域内的图片（Typora 导出格式）
        var container = document.getElementById('write') || document.body;
        var images = container.querySelectorAll('img');

        for (var i = 0; i < images.length; i++) {
            var img = images[i];

            // 跳过已绑定的
            if (img.dataset.izBound === '1') continue;

            // 跳过太小或装饰性图片
            if (img.naturalWidth > 0 && img.naturalWidth < 40 && img.naturalHeight < 40) continue;

            // 跳过已经在链接中的图片（用户可能想跳转链接而非放大）
            var parent = img.parentElement;
            if (parent && parent.tagName === 'A' && parent.getAttribute('href') && parent.getAttribute('href').indexOf('#') !== 0) {
                // 如果链接指向的是图片文件本身，仍然绑定灯箱
                var href = parent.getAttribute('href').toLowerCase();
                if (!/\.(png|jpg|jpeg|gif|webp|svg|bmp|ico)$/i.test(href)) {
                    continue;
                }
            }

            img.dataset.izBound = '1';
            img.style.cursor = 'zoom-in';

            img.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                open(this);
            });
        }
    }

    // ==================== 初始化 ====================

    function init() {
        // 先注入样式
        if (!document.getElementById('iz-styles')) {
            style.id = 'iz-styles';
            document.head.appendChild(style);
        }

        // DOM 就绪后绑定
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', bindImages);
        } else {
            bindImages();
        }

        // 监听动态加载的图片（如 lazyload）
        if (window.MutationObserver) {
            var observer = new MutationObserver(function() {
                bindImages();
            });
            var target = document.getElementById('write') || document.body;
            observer.observe(target, { childList: true, subtree: true });
        }
    }

    init();
})();
