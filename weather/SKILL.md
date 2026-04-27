---
name: weather
description: 高德地图天气服务，提供天气预报、实时天气等。当用户需要查询天气、规划出行天气准备时使用此 skill。
---

## 功能特性

- 🌤️ 多日天气预报（3 天）
- 🌡️ 实时天气数据
- 🏙️ 城市定位与搜索
- 🔑 使用高德 API Key 认证

## 配置

### 高德 API Key

**方式一：环境变量**
```bash
export AMAP_KEY=your_key
```

**方式二：配置文件**
在 `config.json` 中设置：
```json
{
  "amapKey": "你的高德 Web Service Key"
}
```

**获取 Key**：https://lbs.amap.com/api/webservice/create-project-and-key

## 触发条件

用户意图包含：
- 查询天气（如"杭州天气"、"明天会下雨吗"）
- 天气预报（如"周末天气怎么样"）
- 出行天气准备

## 使用方法

### 命令行调用

```bash
cd ~/.hermes/skills/weather

# 查询 3 天天气预报
node scripts/query.js --city=杭州

# 查询实时天气
node scripts/query.js --city=杭州 --type=realtime
```

### 在代码中调用

```javascript
const { getWeather, getRealtimeWeather, analyzeWeather } = require('~/.hermes/skills/weather/index.js');

// 获取天气预报
const weather = await getWeather('杭州');

// 获取实时天气
const realtime = await getRealtimeWeather('杭州');

// 分析天气给出建议
const advice = analyzeWeather(weather.casts[0]);
```

## API 接口

### 1. 获取城市 ADCode

```bash
curl -s "https://restapi.amap.com/v3/config/district?keywords=杭州&key=YOUR_KEY"
```

### 2. 天气预报

```bash
curl -s "https://restapi.amap.com/v3/weather/weatherInfo?city=ADCODE&extensions=all&key=YOUR_KEY"
```

### 3. 实时天气

```bash
curl -s "https://restapi.amap.com/v3/weather/weatherInfo?city=ADCODE&extensions=base&key=YOUR_KEY"
```

## 输出格式

### 天气预报示例

```markdown
### 🌤️ 杭州天气预报 (2024-04-26)

| 日期 | 白天天气 | 夜间天气 | 温度 | 风向 |
|------|---------|---------|------|------|
| 2024-04-26 | 晴 | 多云 | 17°C~27°C | 东风 3 级 |
| 2024-04-27 | 多云 | 阴 | 18°C~25°C | 东南风 2 级 |
| 2024-04-28 | 小雨 | 阴 | 19°C~23°C | 南风 3 级 |

### 💡 出行建议
- 2024-04-26：☀️ 晴天：注意防晒
- 2024-04-27：适宜出行
- 2024-04-28：☔ 有雨：带伞，优先室内
```

### 天气分析建议

| 天气条件 | 建议 |
|---------|------|
| 高温 (>35°C) | ⚠️ 避开 12-15 点户外 |
| 低温 (<5°C) | 🧥 注意保暖 |
| 雨天 | ☔ 带伞，优先室内 |
| 晴天 | ☀️ 注意防晒 |
| 温差>10°C | 🌡️ 建议带外套 |

## 文件结构

```
.hermes/skills/weather/
├── SKILL.md              # 本文件
├── index.js              # 核心函数库
├── package.json          # 依赖配置
├── config.json           # API Key 配置
└── scripts/
    └── query.js          # 天气查询脚本
```

## 相关链接

- [高德天气 API 文档](https://lbs.amap.com/api/webservice/guide/api/weatherinfo)
- [创建应用和获取 Key](https://lbs.amap.com/api/webservice/create-project-and-key)
