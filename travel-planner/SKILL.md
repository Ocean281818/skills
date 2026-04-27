---
name: travel-planner
description: 智能旅游规划助手，根据天气、人流量、交通方式等因素详细安排每天行程。支持多日游规划、景点推荐、美食推荐、路线优化。
---

## 功能特性

- 📅 多日游行程规划（1 天 ~N 天）
- 🌤️ 天气因素分析（雨天改室内、高温避正午）
- 👥 人流量分析（节假日/周末/热门时段）
- 🚗 交通方式优化（步行/公交/驾车/高铁）
- 🏨 酒店位置推荐（靠近景点/交通枢纽）
- 🗺️ 地图可视化链接生成

## 配置

### 必需配置

**高德 API Key**（用于 POI 搜索、路径规划、天气查询）
```bash
export AMAP_KEY=your_key
```
获取：https://lbs.amap.com/api/webservice/create-project-and-key

### 可选配置

在 `config.json` 中设置偏好：
```json
{
  "amapKey": "高德 key",
  "preferences": {
    "travelStyle": "relaxed",
    "budgetLevel": "medium",
    "interests": ["景点", "美食", "购物"]
  }
}
```

### 说明

- 天气查询通过 weather-skill 实现（使用高德天气 API）
- 无需单独配置天气 API，共用高德 API Key 即可

### 配置文件（可选）

在 `config.json` 中设置偏好：
```json
{
  "amapKey": "高德 key",
  "preferences": {
    "travelStyle": "relaxed",
    "budgetLevel": "medium",
    "interests": ["景点", "美食", "购物"]
  }
}
```

## 触发条件

用户意图包含：
- 规划 X 天游/多日游
- 安排行程/制定计划
- 旅游推荐/怎么玩
- 包含"天气"、"人流量"、"路线"等关键词

## 使用方法

### 基础用法

```bash
cd ~/.hermes/skills/travel-planner

# 3 天游规划
node scripts/plan.js --city=杭州 --days=3 --startDate=2024-05-01

# 带兴趣点偏好
node scripts/plan.js --city=北京 --days=2 --interests=景点，美食 --travelStyle=relaxed

# 完整参数
node scripts/plan.js --city=杭州 --days=3 --startDate=2024-05-01 \
  --interests=景点，美食，购物 \
  --travelStyle=relaxed \
  --budgetLevel=medium \
  --avoidCrowds=true
```

### 参数说明

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| --city | 是 | 目的地城市 | - |
| --days | 否 | 游玩天数 | 1 |
| --startDate | 否 | 出发日期 | 今天 |
| --interests | 否 | 兴趣点（逗号分隔） | 景点，美食 |
| --travelStyle | 否 | relaxed=休闲/compact=紧凑 | relaxed |
| --budgetLevel | 否 | budget/medium/luxury | medium |
| --avoidCrowds | 否 | 是否避开人流高峰 | true |

## 核心 API

### 1. 天气查询

```bash
# 获取城市天气 ID
curl -s "https://geoapi.qweather.com/v2/city/lookup?location=杭州&key=${WEATHER_KEY}"

# 获取天气预报
curl -s "https://dev.qweather.com/v7/weather/3d?location=城市 ID&key=${WEATHER_KEY}"
```

### 2. POI 搜索

```bash
cd ~/.hermes/skills/travel-planner
node scripts/poi-search.js --keywords=西湖 --city=杭州 --offset=5
```

### 3. 路径规划

```bash
# 步行
node scripts/route.js --type=walking --origin=起点坐标 --destination=终点坐标

# 公交
node scripts/route.js --type=transfer --origin=起点坐标 --destination=终点坐标 --city=杭州

# 驾车
node scripts/route.js --type=driving --origin=起点坐标 --destination=终点坐标
```

### 4. 智能规划（主程序）

```bash
node scripts/plan.js --city=杭州 --days=3
```

## 输出格式

```markdown
## Day 1：杭州

### 🌤️ 天气
18-28°C 多云，可能有阵雨 | 建议：带伞、防晒

### 👥 人流预警
- 西湖：建议早上 8 点前或晚上 7 点后
- 灵隐寺：早上 9 点前到达

### 📍 行程
| 时间 | 地点 | 类型 | 交通 | 备注 |
|------|------|------|------|------|
| 08:00 | 西湖 | 户外 | - | 避开人流 |
| 12:00 | 楼外楼 | 美食 | 步行 10 分钟 | 杭帮菜 |
| 14:00 | 灵隐寺 | 文化 | 公交 30 分钟 | 雨天备选 |
| 19:00 | 河坊街 | 夜景 | 步行 15 分钟 | 小吃街 |

### 🍜 美食推荐
- 楼外楼（西湖边）：西湖醋鱼、龙井虾仁
- 知味观（河坊街）：杭州小吃

### 🏨 酒店推荐
- 西湖国宾馆（豪华）：距西湖 500 米
- 全季酒店（经济）：距地铁站 200 米

### 🗺️ 地图
[查看路线图](https://a.amap.com/...?data=...)
```

## Python 调用示例

```python
import json, urllib.request, urllib.parse

AMAP_KEY = "your_key"
WEATHER_KEY = "your_weather_key"

def get_weather(location, days=3):
    """获取天气预报"""
    # 先获取城市 ID
    city_url = f"https://geoapi.qweather.com/v2/city/lookup?location={location}&key={WEATHER_KEY}"
    with urllib.request.urlopen(city_url) as r:
        city_data = json.loads(r.read())
    location_id = city_data['location'][0]['id']
    
    # 获取天气预报
    weather_url = f"https://dev.qweather.com/v7/weather/{days}d?location={location_id}&key={WEATHER_KEY}"
    with urllib.request.urlopen(weather_url) as r:
        return json.loads(r.read())

def plan_travel(city, days=3, interests=None):
    """智能旅游规划"""
    # 1. 获取天气
    weather = get_weather(city, days)
    
    # 2. 搜索景点
    # ... 调用高德 API
    
    # 3. 规划路线
    # ... 调用路径规划 API
    
    return {
        'weather': weather,
        'itinerary': [],  # 每日行程
        'mapLink': ''     # 地图链接
    }
```

## 规划逻辑

### 天气适配规则

| 天气 | 策略 |
|------|------|
| 晴/多云 | 正常安排户外景点 |
| 小雨 | 上午户外，下午室内 |
| 中雨/大雨 | 全天室内（博物馆、商场） |
| 高温 (>35°C) | 避开 12:00-15:00 户外 |
| 低温 (<5°C) | 增加室内活动 |

### 人流规避规则

| 场景 | 策略 |
|------|------|
| 节假日 | 热门景点早 8 点前/晚 7 点后 |
| 周末 | 避开 10:00-16:00 高峰 |
| 工作日 | 正常安排 |
| 顶级热门（迪士尼等） | 建议买早享卡或放弃 |

### 交通优选规则

| 距离 | 推荐方式 |
|------|----------|
| <1.5km | 步行 |
| 1.5-5km | 公交/地铁 |
| 5-20km | 地铁优先 |
| >20km | 打车/驾车 |
| 城市间 | 高铁 > 驾车（节假日） |

## 文件结构

```
.hermes/skills/travel-planner/
├── SKILL.md           # 本文件
├── config.json        # 配置文件
├── index.js           # 核心函数库
├── scripts/
│   ├── plan.js        # 主规划程序
│   ├── poi-search.js  # POI 搜索
│   ├── route.js       # 路径规划
│   └── weather.js     # 天气查询

## 注意事项

1. **API Key 安全**：不要将 Key 提交到代码仓库
2. **调用频率**：高德 API 有每日限额，请合理使用
3. **天气数据**：和风天气免费版有调用限制
4. **中文参数**：URL 中的中文必须 urlencode 编码
5. **脚本语法问题**：index.js 中存在模板字符串语法错误（第 37 行），Node.js 某些版本可能不兼容。如遇 `SyntaxError: Unexpected template string` 错误，建议直接使用 API 调用或手动规划行程。
6. **跨城市多日游**：当前脚本仅支持单城市规划。跨城市行程（如宁波 - 舟山 - 上海）需手动规划，注意城市间交通衔接和住宿安排。
7. **依赖安装**：运行脚本前需执行 `npm install axios` 安装依赖。如遇 `Cannot find module 'axios'` 错误，先安装依赖。
8. **API Key 验证**：如遇 `INVALID_USER_KEY` 错误，检查 API Key 是否有效。高德 Web Service API 需在控制台开通对应服务（天气、路径规划等）。

## 五一/节假日出行特别提示

### 人流规避策略（热门景点）

| 景点类型 | 高峰时段 | 建议游览时间 |
|---------|---------|-------------|
| 顶级热门（普陀山、迪士尼） | 09:00-15:00 | **开门即入**（7:00-8:00） |
| 城市地标（外滩、西湖） | 18:00-21:00 | 19:30 后或清晨 |
| 博物馆/室内 | 10:00-16:00 | 开门即入或 16:00 后 |
| 海滩/海岛 | 11:00-16:00 | 08:00 前或 16:00 后 |

### 预订清单（提前 15 天）

1. ✅ 高铁票：12306 提前 15 天放票，节假日秒光
2. ✅ 酒店/民宿：五一价格翻倍，尽早预订
3. ✅ 景点门票：部分景点（普陀山、天一阁）需公众号预约
4. ✅ 机票：跨城市航班提前预订价格更优

### 跨城市交通建议

| 距离 | 推荐方式 | 节假日注意事项 |
|------|---------|---------------|
| 省内（<200km） | 高铁/大巴 | 高铁优先，大巴易堵车 |
| 跨省（200-500km） | 高铁 | 提前 15 天抢票 |
| 远距离（>500km） | 飞机 > 高铁 | 早班机价格低且准点率高 |

## 相关链接

- [高德开放平台](https://lbs.amap.com/)
- [和风天气](https://dev.qweather.com/)
- [高德路径规划 API](https://lbs.amap.com/api/webservice/guide/api-newroute/route-planning)
