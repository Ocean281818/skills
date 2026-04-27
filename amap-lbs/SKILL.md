---
name: amap-lbs
description: 高德地图综合服务，支持POI搜索、路径规划、旅游规划、周边搜索和热力图数据可视化。当用户需要搜索地点、规划路线、查询周边信息、出行游玩时使用此 skill。
---

## 功能概览

- POI 搜索（关键词/周边/类型筛选）
- 路径规划（步行/驾车/骑行/公交）
- 智能旅游规划
- 热力图可视化

## 配置

设置环境变量：`export AMAP_KEY=your_key`，或编辑 `config.json`：

```json
{
  "webServiceKey": "你的key",
  "defaultLocation": {
    "name": "默认位置名称",
    "lnglat": "经度,纬度"
  }
}
```

## 触发条件

用户意图包含：搜索地点、周边查询、路线规划、旅游规划、数据可视化等。

---

## 核心方法

### 1. 简单搜索（无需 API Key）

生成高德地图搜索链接：
```
https://www.amap.com/search?query={关键词}
```

### 2. 地理编码（获取坐标）

```bash
curl -s "https://restapi.amap.com/v3/geocode/geo?address={地址}&key=${AMAP_KEY}"
# 返回 geocodes[0].location 格式：经度,纬度
```

### 3. IP 定位

```bash
curl -s "https://restapi.amap.com/v3/ip?key=${AMAP_KEY}"
# 返回省份、城市、矩形范围
```

### 4. POI 搜索

```bash
cd ~/.hermes/skills/amap-lbs

# 关键词搜索
node scripts/poi-search.js --keywords=肯德基 --city=北京

# 周边搜索
node scripts/poi-search.js --keywords=酒店 --location=116.397428,39.90923 --radius=1000
```

### 5. 路径规划

```bash
cd ~/.hermes/skills/amap-lbs

# 步行
node scripts/route-planning.js --type=walking --origin=116.397428,39.90923 --destination=116.427281,39.903719

# 驾车
node scripts/route-planning.js --type=driving --origin=起点坐标 --destination=终点坐标

# 公交（需指定城市）
node scripts/route-planning.js --type=transfer --origin=起点坐标 --destination=终点坐标 --city=北京
```

### 6. 旅游规划

```bash
cd ~/.hermes/skills/amap-lbs
node scripts/travel-planner.js --city=北京 --interests=景点,美食,酒店
```

### 7. 周边搜索链接

基于坐标生成搜索链接：
```
https://ditu.amap.com/search?query={类别}&query_type=RQBXY&longitude={经度}&latitude={纬度}&range=1000
```

### 8. 热力图可视化

```
http://a.amap.com/jsapi_demo_show/static/openclaw/heatmap.html?mapStyle={grey|light}&dataUrl={URL编码的数据地址}
```

---

## Python 调用示例

```python
import json, urllib.request, urllib.parse

AMAP_KEY = "your_key"

def amap_search(keyword, city, offset=5):
    params = {"keywords": keyword, "city": city, "key": AMAP_KEY, "offset": offset}
    url = "https://restapi.amap.com/v3/place/text?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

def amap_route(origin, destination, city="", route_type="transit"):
    params = {"origin": origin, "destination": destination, "key": AMAP_KEY}
    if city: params["city"] = city
    base = "https://restapi.amap.com/v3/direction/"
    url = base + {"transit": "transit/integrated", "walking": "walking", "driving": "driving"}[route_type]
    url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))
```

---

## 旅游规划工作流

### 步骤
1. 获取城市坐标 → 2. 搜索景点/美食 → 3. 规划路线 → 4. 生成地图链接

### 关键考虑因素
- **天气**：雨天→室内景点
- **人流**：热门景点→早晚时段
- **交通**：步行可达优先，城市间高铁优先

### 输出格式（精简版）

```markdown
## Day 1：城市名

### 📍 行程
| 时间 | 地点 | 类型 | 备注 |
|------|------|------|------|
| 上午 | 景点 A | 户外 | 早点避开人流 |
| 下午 | 景点 B | 室内 | 雨天备选 |
| 晚上 | 景点 C | 夜景 | |

### 🍜 美食
- 店名（距景点 X 米）：推荐菜

### 🚗 交通
- 景点 A→B：步行 10 分钟
- 景点 B→C：地铁 X 号线

### 🗺️ 地图链接
[点击查看](地图 URL)
```

### 地图数据格式
```javascript
const data = [
  {type:'poi',lnglat:[经度，纬度],text:'景点名'},
  {type:'route',routeType:'walking',start:[经度，纬度],end:[经度，纬度]}
];
`https://a.amap.com/jsapi_demo_show/static/openclaw/travel_plan.html?data=${encodeURIComponent(JSON.stringify(data))}`
```

**注意**：输出要简洁，避免冗长解释。多日游每天按上述格式输出，不要重复天气/人流分析过程，直接给出结论。

---

## 注意事项

1. API 返回的 `location` 格式为 `经度,纬度`（经度在前）
2. 周边搜索默认范围 1000 米
3. 所有 REST API 请求追加 `appname=amap-lbs-skill` 参数
4. 中文参数必须使用 `urlencode` 处理

## 相关链接

- [高德开放平台](https://lbs.amap.com/)
- [获取 Key](https://lbs.amap.com/api/webservice/create-project-and-key)
- [API 文档](https://lbs.amap.com/api/webservice/summary)
