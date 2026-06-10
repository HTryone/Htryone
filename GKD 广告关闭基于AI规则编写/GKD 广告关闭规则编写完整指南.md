# GKD 广告关闭规则编写完整指南

> 2026-5

## 一、方案概述

本方案利用 DeepSeek（大语言模型）结合 GKD 快照文件，自动生成可导入 GKD 的广告跳过规则。用户通过 GKD 快照功能抓取广告界面，由 DeepSeek 分析快照并输出 JSON5 格式规则代码，全程无需手动编写选择器。

核心流程：抓快照 → 上传给 DeepSeek → 复制输出的代码 → 导入 GKD

---

## 二、操作流程

### 2.1 第一步：准备 GKD 快照

1. 打开 GKD 应用。
2. 进入 设置 → 高级设置 → 快照 → 悬浮窗服务，将该项开启。
3. 打开手机中需要去广告的 App。
4. 当广告弹出时，点击屏幕左上角出现的快照悬浮窗按钮。
5. 打开 GKD 首页，找到刚创建的快照记录。
6. 点击快照文件，选择 保存到下载。
7. 使用文件管理器进入手机存储的 Download 目录，找到对应的 zip 文件。
8. 解压 zip，得到一个无后缀的 JSON 文件和一张 PNG 图片。

### 2.2 第二步：上传到 DeepSeek

1. 打开 DeepSeek 网页（https://chat.deepseek.com），新建对话。
2. 将第三节的系统提示词完整复制粘贴到对话框，发送。
3. 在同一个对话中，上传解压得到的 JSON 文件和 PNG 图片。
4. 发送消息：帮我生成规则。

### 2.3 第三步：导入 GKD

1. 复制 DeepSeek 输出的 JSON5 代码块。
2. 打开 GKD → 首页 → 订阅 → 本地订阅 → 应用规则（或全局规则）。
3. 点击右上角的 + 号。
4. 将代码块粘贴到输入框中。
5. 点击确认保存。

### 2.4 第四步：测试与调试

1. 重新打开目标 App，验证广告是否被自动跳过或关闭。
2. 如果规则未生效，检查 GKD 是否已授权无障碍权限。
3. 如果出现报错（如 key 重复），将报错信息和已有规则一起发给 DeepSeek 修复合并。
4. 如果误触了正常按钮，将已有规则和现象描述发给 DeepSeek 修改选择器。

---

## 三、DeepSeek 系统提示词

将以下内容完整复制粘贴到 DeepSeek 对话框（一次性操作，之后每次只需发送快照）：

---

你是 GKD（手机广告跳过工具）规则开发者，精通 GKD 的 JSON5 语法和选择器规则。

你的任务是根据用户提供的快照文件（JSON 控件描述 + 截图），生成可直接导入 GKD 的 JSON5 规则代码。

### 输出要求

直接输出代码块，不要解释，不要废话。格式如下：

```json5
// 开屏广告
{
  id: 'com.example.app',
  name: '示例应用',
  groups: [
    {
      key: 0,
      name: '开屏广告',
      fastQuery: true,
      matchTime: 5000,
      actionMaximum: 1,
      resetMatch: 'app',
      rules: [
        {
          activityIds: 'com.example.app.MainActivity',
          matches: '[id="com.example:id/btn_skip"]',
        }
      ],
      snapshotUrls: ['https://i.gkd.li/i/XXXXXXX'],
    }
  ],
}
```

### 字段说明

id：App 包名，字符串，必填。来源：JSON 文件根节点的 id 字段。
name：App 显示名称，字符串，必填。
key：规则组编号，从 0 开始递增，必填。
name（组）：规则组名称，如"开屏广告"、"会员弹窗"。
fastQuery：布尔值，建议填 true，可提升匹配效率。
matchTime：最大匹配等待时间（毫秒），默认 5000，开屏广告建议 5000~10000，不超过 10000。
actionMaximum：最大触发次数，默认 1，防止重复点击。
resetMatch：切换 App 后是否重置次数，填 'app'。
activityIds：Activity 类名，应用规则专用，用于限定生效页面。
matches：CSS Selector 选择器，字符串，必填。
anyMatches：选择器数组，满足任一条件即匹配。
snapshotUrls：快照 URL 数组，可选，格式为 https://i.gkd.li/i/后跟快照ID。

### 选择器语法

按文字匹配：

```json5
[text="跳过"]                  // 精确匹配文字
[text*="跳过"]                 // 包含"跳过"
[text^="跳过"]                 // 以"跳过"开头
[text$="广告"]                  // 以"广告"结尾
[text.length<10]               // 文字长度小于 10
```

按控件 ID 匹配：

```json5
[id="com.example:id/btn_skip"]  // 完整 ID 精确匹配（最稳定）
[id$="btn_skip"]               // ID 以 btn_skip 结尾
[id^="ad_"]                     // ID 以 ad_ 开头
[id*="skip"]                   // ID 包含 skip
```

按 vid 匹配（推荐优先级高）：

```json5
[vid="img_close"]               // vid 资源名称匹配
[vid="iv_close"]
[vid="btn_close"]
```

按 content-desc 匹配：

```json5
[desc*="关闭"]                  // 包含"关闭"
[desc="关闭广告"]
```

组合条件：

```json5
[vid="img_close"][clickable=true]            // 同时满足两个条件
[text="跳过"][visibleToUser=true]            // 仅匹配可见元素
[text="关闭"][clickable=true][enabled=true]  // 可点击且可用
```

多个条件"或"：

```json5
anyMatches: [
  '[clickable=true][text*="跳过"]',
  '[clickable=true][desc*="跳过"]',
  '[clickable=true][id*="skip"]',
]
```

### 常用规则模板

```json5
// 开屏广告跳过（通用）
matches: '[clickable=true][text*="跳过"][text.length<5]'

// vid 关闭按钮
matches: '[vid="img_close"]'
matches: '[vid="iv_close"]'

// id 关闭按钮
matches: '[id$="iv_close"]'
matches: '[id$="btn_close"]'

// 文字关闭按钮
matches: '[text="关闭"][clickable=true]'
matches: '[text="跳过广告"][clickable=true]'

// 全局开屏广告兜底方案
{
  key: 0,
  name: '全局开屏广告（跳过）',
  fastQuery: true,
  matchTime: 10000,
  actionMaximum: 1,
  resetMatch: 'app',
  rules: [
    {
      anyMatches: [
        '[clickable=true][text*="跳过"]',
        '[clickable=true][desc*="跳过"]',
        '[clickable=true][id*="skip"]',
        '[clickable=true][id*="close"]',
      ]
    }
  ]
}
```

### 生成规则流程

第一步：读取 JSON 文件，找到根节点的 id 字段，这就是 App 包名。
第二步：读取 JSON 中的 activityIds 或 launchableActivityName，确定 Activity 类名。
第三步：遍历控件列表，找到可疑的关闭按钮（通常是小的、可见的、clickable 的控件），提取其 vid、id、text、desc 属性。
第四步：如果有多个广告弹窗，为每一个生成一条独立的规则组。
第五步：选择最精确的选择器。优先级：id > vid > text > desc > 组合条件 > anyMatches。
第六步：输出 JSON5 代码块，不要附带任何解释。

### 注意事项

1. 选择器必须精确。过于宽泛的选择器会误触正常按钮。
2. 优先使用 id，其次 vid，尽量避免单独使用 text。text 依赖开发者不改变文字，风险较高。
3. 全局规则的选择器要足够通用，但也要避免误触，建议始终加 [clickable=true]。
4. key 字段从 0 开始递增。如果用户已有规则，确保 key 不冲突。
5. fastQuery: true 建议始终填写。
6. matchTime 开屏广告建议 5000ms 以上、不超过 10000ms，因为广告可能延迟出现。
7. activityIds 建议填写，可以防止在应用内部误点。
8. 如果 JSON 中包含多个弹窗，分别为每个弹窗生成一条规则组。
9. 输出纯代码块，不需要任何解释性文字。

---

## 四、快照节点分析

### 4.1 关键属性说明

在 JSON 快照文件中找到关闭按钮节点，关注以下属性：

| 属性 | 说明 | 示例 |
|------|------|------|
| id | 资源 ID，最稳定可靠 | com.chaoxing.mobile:id/btn_jump |
| text | 显示文本 | "跳过3s" |
| desc | content-desc 内容描述 | "跳过广告" |
| vid | 视图资源名称 | img_close |
| clickable | 是否可点击 | true |
| visibleToUser | 是否可见 | true |
| enabled | 是否可用 | true |

### 4.2 定位技巧

优先使用 id，因为通常固定不变。
若 id 为空或随机化，改用 vid。
若 vid 也无，使用 text 或 desc 包含"跳过"、"关闭"等关键词。
若文本带动态秒数（如"跳过3s"），使用 [text*="跳过"] 模糊匹配。
若以上均无，尝试组合 [clickable=true][visibleToUser=true] 找可点击的可见元素。

### 4.3 快照节点示例

示例1：固定 id，无文本（12306）

```json
{
  "id": "com.MobileTicket:id/tv_skip",
  "clickable": true,
  "text": null
}
```

对应规则：

```json5
{
  id: 'com.MobileTicket',
  name: '铁路12306',
  groups: [
    {
      key: 0,
      name: '开屏广告',
      fastQuery: true,
      matchTime: 5000,
      actionMaximum: 1,
      resetMatch: 'app',
      rules: [
        {
          activityIds: 'com.MobileTicket.ui.activity.MainActivity',
          matches: '[id="com.MobileTicket:id/tv_skip"]',
        }
      ],
      snapshotUrls: ['https://i.gkd.li/i/1775155128184'],
    }
  ],
}
```

示例2：固定 id，文本带秒数（学习通）

```json
{
  "id": "com.chaoxing.mobile:id/btn_jump",
  "text": "跳过3s",
  "clickable": true
}
```

对应规则：

```json5
{
  id: 'com.chaoxing.mobile',
  name: '学习通',
  groups: [
    {
      key: 0,
      name: '开屏广告',
      fastQuery: true,
      matchTime: 5000,
      actionMaximum: 1,
      resetMatch: 'app',
      rules: [
        {
          activityIds: 'com.chaoxing.mobile.activity.SplashActivity',
          matches: '[id="com.chaoxing.mobile:id/btn_jump"]',
        }
      ],
      snapshotUrls: ['https://i.gkd.li/i/1775157698138'],
    }
  ],
}
```

示例3：无固定 id，靠文本匹配（知乎）

```json
{
  "id": null,
  "text": "跳过",
  "clickable": true
}
```

对应规则：

```json5
{
  id: 'com.zhihu.android',
  name: '知乎',
  groups: [
    {
      key: 0,
      name: '开屏广告',
      fastQuery: true,
      matchTime: 5000,
      actionMaximum: 1,
      resetMatch: 'app',
      rules: [
        {
          activityIds: 'com.zhihu.android.app.ui.activity.LaunchActivity',
          matches: '[clickable=true][text*="跳过"]',
        }
      ],
      snapshotUrls: ['https://i.gkd.li/i/13070251'],
    }
  ],
}
```

---

## 五、全局规则与局部规则对比

### 5.1 特性对比

| 特性 | 全局规则 | 应用规则 |
|------|---------|---------|
| 作用范围 | 所有应用 | 仅指定的一个应用 |
| id 字段 | 不需要 | 需要指定应用包名 |
| activityIds | 不支持 | 支持（强烈推荐填写） |
| 精确度 | 较低，可能误点 | 高，精准定位 |
| 适用场景 | 通用广告兜底 | 针对性广告、弹窗 |
| 优先级 | 低 | 高（应用规则优先生效） |

### 5.2 如何选择

优先写应用规则：针对常用 App（微信、支付宝、12306、学习通等），捕获快照后编写精确规则，最稳定。
全局规则作为补充：对于不常用的 App，或者来不及写精确规则的，用全局规则兜底。
无需担心冲突：如果一个广告同时被全局规则和应用规则匹配，GKD 会执行应用规则（更具体），不会重复点击。

---

## 六、调试与问题解决

### 6.1 规则不生效的排查步骤

1. 检查基础权限：
   - GKD 无障碍服务是否开启？
   - 是否允许自启动/后台运行？
2. 确认规则状态：
   - GKD 首页 → 订阅 → 本地订阅 → 应用规则，规则组开关是否打开？
3. 分析快照：
   - 重新捕获快照，确认跳过按钮的 id、text 与规则是否一致。
   - 注意 activityIds 是否匹配当前 Activity。
4. 简化测试：
   - 暂时去掉 activityIds、fastQuery 等字段，只保留最简 matches。
   - 若生效，再逐步加回限制。

### 6.2 常见错误及解决

| 错误提示 | 原因 | 解决 |
|---------|------|------|
| Expect EOF, got , | 使用了逗号分隔条件 | 改用 anyMatches 数组 |
| Expect char ], got i | 使用了 [id*="skip" i] 中的 i | 去掉 i |
| 规则不触发（无报错） | 匹配时机过早或选择器错误 | 增大 matchTime，重新分析快照 |
| 误点其他按钮 | 缺少 activityIds 限制 | 添加 activityIds 限定页面 |
| key 重复 | 新规则的 key 与已有规则冲突 | 将两条规则发给 DeepSeek 合并 |

### 6.3 最佳实践

优先使用 matches 而非 anyMatches，前者兼容性更好。
固定 id 最可靠，只要应用不更新 id，规则长期有效。
加上 activityIds，防止在应用内部误点。
matchTime 不宜过短，开屏广告建议 5000ms 以上、不超过 10000ms。
actionMaximum 建议设为 1，避免在应用内重复触发。
优先使用 id，其次 vid，尽量避免单独使用 text。

---

## 七、进阶操作

### 7.1 合并重复规则

将已有规则和新规则一起发给 DeepSeek，发送消息：帮我将这两条规则合并，确保 key 不重复。

### 7.2 调试不生效的规则

将 GKD 显示的报错信息、规则的完整代码、以及快照文件一起发给 DeepSeek，发送消息：这条规则报错，请帮我修复。

### 7.3 修改已有规则

将原规则代码发给 DeepSeek，说明要修改的地方，发送消息：请将上述规则中的选择器修改为 xxx，输出修改后的完整代码。

### 7.4 针对多个广告生成规则

如果同一个 App 有多种广告类型，可以在一次对话中上传多个快照，发送消息：这个 App 有以下几种广告，请分别生成规则。

---

## 八、注意事项汇总

1. GKD 必须授予无障碍权限，否则规则无法生效。
2. 快照必须包含广告弹出时的界面，不完整的快照会导致选择器错误。
3. DeepSeek 生成的选择器仅供参考，实际使用前建议先测试。
4. 全局规则会影响所有 App，生成前需确认选择器不会误触其他 App 的正常按钮。
5. key 冲突问题很常见，每次添加新规则前建议检查现有规则的 key 值。
6. 如果 App 更新后规则失效，需要重新抓快照并生成规则。
7. activityIds 建议始终填写，可以精确限定规则生效的页面。
8. 快照 URL 格式为 https://i.gkd.li/i/ 后跟快照文件名中的数字 ID。
9. 系统提示词只需要发送一次，不需要每次都重复发送。
10. 建议按 App 分别创建规则，便于管理和调试。

---

## 九、快速生成提示词

将以下内容发给 DeepSeek，附上快照文件即可：

根据这张 GKD 快照，为 [应用包名] 生成一条关闭开屏广告的规则。
要求使用 matches 匹配按钮的 id，同时包含 fastQuery、matchTime、actionMaximum、resetMatch 和 activityIds 字段。

---

## 十、速查表

| 场景 | 推荐策略 | 示例选择器 |
|------|---------|-----------|
| 按钮有固定 id | 直接用 [id="..."] | [id="com.xxx:id/btn_skip"] |
| 按钮无 id，有固定文本 | 用 [text*="跳过"] | [clickable=true][text*="跳过"] |
| 按钮文本带动态数字 | 用 [text*="跳过"] 模糊匹配 | 同上 |
| 按钮无文本无 id，有 desc | 用 [desc*="跳过"] | [clickable=true][desc*="跳过"] |
| 多个条件"或"匹配 | 用 anyMatches 数组 | anyMatches: [...] |
| 多个条件"且"匹配 | 组合选择器 | [vid="img_close"][clickable=true] |
| 全局兜底 | 全局规则 + anyMatches | 见第三节模板 |

核心原则：一次只针对一个应用，捕获快照，找到最稳定的属性，编写最简洁的选择器。

---

*文档版本：v1.0*
*适用平台：Android + GKD + DeepSeek 网页*
