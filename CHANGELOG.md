# 更新日志

## 2026-07-11

- 新增：share/ 目录，头孢类抗生素与酒精相互作用文章（HTML + MD）
- 新增：vpwork/ 图床文件夹，图床教程图片（ng1~ng4.jpg, 1.png, 2.png）
- 新增：网站验证文件 c013e8906ad8b04ce7aef6997ae2d092.txt
- 更新：头孢文章 MD 重命名（补充"与医学断言核查报告"后缀）

## 2026-06-29

- 新增：personal/p1 无界云图标（SVG + PNG），测试用

## 2026-06-21

- 新增：《银行卡管理与资金分配经验分享》文章（HTML + MD + Excalidraw 配图）
- 新增：personal/p1/ 目录用于存放文章配图

## 2026-06-20

- 新增：《沟通的"知识诅咒"》文章
- 新增：personal/utils 门户子页面（md目录生成器等）
- 新增：generate_index_html.py 添加 page2.html 增量生成逻辑
- 修复：门户页面 page2.html 文件链接丢失子目录层级的问题
  - 原因：`rsplit("/", 1)[-1]` 只取文件名，砍掉了中间文件夹路径
  - 修复：改为截取相对于门户文件夹的完整路径，保留所有子目录层级
- 修复：`generate_index_html.py` 中 page2.html 写入代码缩进在 for 循环外的 bug
  - 原因：多个门户时只有最后一个会被写入文件
  - 修复：缩进移入 for 循环内部

## 2026-06-19

- 新增：首页「最近更新」Tab，展示最近改动的 10 篇文件（含文件夹名、格式、日期）
- 新增：generate_index_html.py 文件数据加入 mtime 和 folder 字段
- 优化：固定深色模式改为纯黑背景（#000），小字颜色加深（#999）保证可读
- 优化：home-dark.css 补充固定+智能深色模式完整静态规则
- 优化：smart-dark-mode.js 首页和 page2 跳过动态注入，走 home-dark.css 静态规则
- 修复：updateTime 改为最新文件真实修改时间，非脚本运行时间
- 修复：scripts/css/home.css 补充 Tab 按钮浅色样式
- 修复：手机端 .tree-item.active 配色改为暖棕色，补 .toolbar 桌面端 flex 样式
- 重构：新建 `refactor/dark-mode` 分支，dark-mode.css 配色从 GitHub Dark 切换为 VS Code Dark+
  - 色值：背景 #1e1e1e、代码块 #252526、边框 #3d3d3d、文字 #d4d4d4
  - 语法高亮：关键字 #569cd6(蓝)、字符串 #ce9178(橙)、注释 #6a9955(绿)
- 新增：dark-mode.css 补充 16 个缺失模块覆盖（脚注、图表面板、行内公式、Alert 告警、kbd 等）
- 清理：dark-mode.css 删除导出 HTML 中不存在的编辑器专属选择器
- 优化：次要文字灰色 #858585→#a0a0b0，大纲展开箭头提亮
- 优化：侧边栏大纲深色模式（hover/active 交回原主题处理）
- 文档：三个 CSS 文件头部注释补充分工说明，README.md 同步更新 CSS 分工表

## 2026-06-18

- 优化：手机端侧边栏改为横向胶囊标签条，节省屏幕空间
- 清理：移除 home.css/home-dark.css 中未使用的 .stats 和 .search-box 选择器

## 2026-06-13

- 新增：Git 命令大全（HTML + MD）
- 新增：深色模式自动监控脚本 watch-dark-mode.py（watchdog 事件驱动）
- 新增：Windows 双击启动脚本 start-watch.bat
- 新增：深色模式自动注入技术实现文档（完整技术方案和踩坑记录）
- 优化：apply-dark-mode.py 使用唯一注入标记判断，避免误判代码示例
- 优化：为所有 HTML 文件注入深色模式脚本支持
- 优化：Git 命令大全精简冗余章节，补充 git init、reset--hard 最省事用法
- 优化：Git 命令大全 HTML 表格边框改用 CSS 变量，删除 td:hover box-shadow
- 修复：smart-dark-mode.js 智能深色模式下表格/目录 hover 白色背景刺眼问题
- 修复：清理旧标记 @#@，统一使用 __DARK_MODE_INJECTED__ 标记
- 修复：监控脚本判断逻辑，避免死循环

## 2026-06-11

- 新增：浏览器指南（HTML + MD + 图片资源）
- 新增：节点搭建指南（HTML + MD + 图片资源）
- 新增：科技数码相关/极限压缩终极指南（HTML）
- 新增：每日安全新闻目录
- 重组：创建科技数码相关父目录，归类 GKD、浏览器指南等内容
- 优化：index.html 主题色改为普鲁士蓝（#1D4E89）
- 优化：索引页更新（7 篇笔记）

## 2026-06-10

- 初始化仓库：创建 README.md、LICENSE（CC BY-NC 4.0）、.gitignore
- 新增：索引生成脚本 update_index.py
- 新增：index.html / index.md 索引页
- 优化：索引脚本修复相对路径、排除 .workbuddy 目录
- 优化：索引脚本改为只扫描 HTML/PDF 文件，排除 MD
- 优化：文件名统一全小写（Index.html → index.html, Index.md → index.md）
- 新增：GKD 广告关闭基于AI规则编写完整指南（HTML + MD）
- 新增：DOCS/Openlist 安装win部署应用文档（PDF + DOCX）
- 新增：DOCS/学堂不正常优化文档（PDF + DOCX）
- 优化：索引脚本增加 PDF 文件支持
