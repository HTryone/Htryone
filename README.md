# Htryone

个人经历记录 — 历程、感悟、经验总结。

## 项目简介

本仓库用于记录个人历程类内容，源文件以 Markdown 编写，通过 Typora 导出为 HTML 后部署为静态网站。内容涵盖技术笔记、数码测评、个人感悟等，支持深色模式、图片放大、全文搜索等阅读体验。

- **在线访问**：通过 Cloudflare Pages 自动构建部署
- **许可证**：[CC BY-NC 4.0](./LICENSE)（可分享、不可商用）

## 目录结构

```
.
├── index.html              # 主页（由脚本生成，勿手动编辑）
├── home_template.html       # 主页模板
├── index.md                 # Markdown 索引（旧方案，update_index.py 生成）
├── generate_index_html.py   # 索引生成脚本（主页 + 门户页 + 数据文件）
├── update_index.py          # Markdown 目录索引生成脚本
├── scripts/                 # 前端脚本与样式
│   ├── dark-mode-toggle.js  # 深色模式三档切换（light / fixed / smart）
│   ├── dark-mode.js         # 固定深色模式加载器
│   ├── smart-dark-mode.js   # 智能深色模式（HSL 压暗算法）
│   ├── image-zoom.js        # 图片点击放大灯箱
│   ├── css/
│   │   ├── home.css         # 非常规页面浅色样式（home 索引页等）
│   │   ├── home-dark.css    # 非常规页面深色样式（fixed + smart）
│   │   └── dark-mode.css    # Typora 导出页 fixed 深色样式（VS Code Dark+）
│   └── data/
│       └── site_data.js     # 站点文件索引数据（脚本生成）
├── personal/                # 个人笔记
└── 科技数码相关/             # 科技数码类内容
```

## 网站架构

### 页面类型

| 页面 | 模板 | 生成方式 | 说明 |
|------|------|----------|------|
| 主页 `index.html` | `home_template.html` | 脚本原样复制模板 | 左侧文件夹树 + 右侧文件卡片，数据由 `site_data.js` 运行时加载 |
| 门户页 `page2.html` | 脚本内 f-string | 脚本生成 | 顶级文件夹下的子分类页面 |

### 数据流

```
generate_index_html.py
  ├── 扫描磁盘 .html/.htm/.pdf 文件
  ├── 生成 scripts/data/site_data.js  →  const SITE_DATA = {...}
  ├── 复制 home_template.html → index.html
  └── 生成 各门户 page2.html
```

主页和门户页在浏览器运行时从 `site_data.js` 加载数据，通过内联 JS 渲染文件列表。

### CSS 文件分工

| 文件 | 适用页面 | 职责 |
|------|----------|------|
| `home.css` | 非常规页面（home 索引页等） | 浅色样式 |
| `home-dark.css` | 非常规页面 | 深色样式（fixed + smart） |
| `dark-mode.css` | Typora 导出页 | fixed 深色样式（VS Code Dark+ 配色，通用兜底，不区分/适配主题） |

**追加规则**：非常规页面样式写 `home.css` / `home-dark.css`，Typora 导出页样式写 `dark-mode.css`，按页面类型归类，不混写。

### JS 注入

模板（`home_template.html`、门户页 f-string）**自带** `dark-mode-toggle.js` 和 `image-zoom.js` 的引用，并带有注入标记注释（`__DARK_MODE_INJECTED__` / `__IMAGE_ZOOM_INJECTED__`），生成时即写入，无需脚本补注入。

内容页（Typora 导出的 HTML）通过 `scripts/apply-dark-mode.py` 或 `scripts/watch-dark-mode.py` 自动注入，靠标记注释去重。

## 使用方法

### 生成索引

```bash
python generate_index_html.py
```

扫描工作区所有 `.html/.htm/.pdf` 文件，生成主页 `index.html`、门户页 `page2.html` 及数据文件 `scripts/data/site_data.js`。

### 内容页深色模式注入

```bash
# 一次性批量注入
python scripts/apply-dark-mode.py

# 常驻监控自动注入（watchdog）
python scripts/watch-dark-mode.py
```

## 部署

已连接 Cloudflare Pages，推送至 GitHub 后自动构建部署，无框架预设。

## 技术栈

- **内容编写**：Markdown + Typora
- **前端**：原生 HTML / CSS / JavaScript（无框架）
- **自动化**：Python 脚本
- **部署**：Cloudflare Pages
- **版本控制**：Git + GitHub
