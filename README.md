# Skills 集合

这是一个 Hermes AI 助手技能集合仓库，包含多个实用的 Skill 模块。

## 📁 项目结构

```
skills/
├── qiuzhi/           # 求职技能
├── amap-lbs/         # 高德地图服务
├── bilibili_reply/   # B 站评论回复
├── travel-planner/   # 智能旅游规划
└── weather/          # 天气服务
```

## 📦 Skills 介绍

### 1. qiuzhi - 求职技能

**位置**: `qiuzhi/qiuzhi_skill/`

求职辅助技能，包含：
- B 站视频监控脚本 (`bilibili_monitor.py`)
- 大量 AI 学习资料和教程
- OpenClaw 相关文档

**主要功能**:
- 监控 B 站 UP 主视频更新
- 获取 AI 领域最新资讯和教程

### 2. amap-lbs - 高德地图综合服务

**位置**: `amap-lbs/`

基于高德地图 Web Service API 的地理数据服务。

**功能特性**:
- ✅ POI 搜索（关键词/周边/类型筛选）
- ✅ 路径规划（步行/驾车/骑行/公交）
- ✅ 智能旅游规划助手
- ✅ 地图可视化链接生成
- ✅ 热力图数据可视化

**快速开始**:
```bash
cd amap-lbs
npm install

# 配置 API Key
export AMAP_KEY=your_key

# POI 搜索
node scripts/poi-search.js --keywords=肯德基 --city=北京

# 路径规划
node scripts/route-planning.js --type=walking --origin=起点坐标 --destination=终点坐标
```

**文档**: [README.md](amap-lbs/README.md) | [SKILL.md](amap-lbs/SKILL.md)

### 3. bilibili_reply - B 站评论自动回复

**位置**: `bilibili_reply/`

自动回复 Bilibili 视频评论的 Skill。

**功能特性**:
- 获取视频评论列表
- 筛选未回复的评论
- 以 AI 助手身份发送回复
- 自动汇报回复详情

**配置**: 需要在 `SKILL.md` 中配置 `sessdata` 和 `bili_jct` 凭证

**使用示例**:
```bash
cd bilibili_reply/scripts

# 获取评论列表
python3 bilibili_reply.py list --bvid BV1xx411c7mD

# 回复评论
python3 bilibili_reply.py reply --bvid BV 号 --rpid 评论 ID --message "回复内容"
```

**文档**: [SKILL.md](bilibili_reply/SKILL.md)

### 4. travel-planner - 智能旅游规划助手

**位置**: `travel-planner/`

根据天气、人流量、交通方式等因素详细安排每天行程的旅游规划助手。

**功能特性**:
- 📅 多日游行程规划（1 天 ~N 天）
- 🌤️ 天气因素分析（雨天改室内、高温避正午）
- 👥 人流量分析（节假日/周末/热门时段）
- 🚗 交通方式优化（步行/公交/驾车/高铁）
- 🏨 酒店位置推荐
- 🗺️ 地图可视化链接生成

**快速开始**:
```bash
cd travel-planner
npm install

# 配置 API Key
export AMAP_KEY=your_key

# 3 天游规划
node scripts/plan.js --city=杭州 --days=3 --startDate=2024-05-01
```

**文档**: [SKILL.md](travel-planner/SKILL.md)

### 5. weather - 高德天气服务

**位置**: `weather/`

使用高德地图天气 API 提供天气预报服务。

**功能特性**:
- 🌤️ 多日天气预报（3 天）
- 🌡️ 实时天气数据
- 🏙️ 城市定位与搜索
- 💡 智能出行建议

**快速开始**:
```bash
cd weather
npm install

# 配置 API Key
export AMAP_KEY=your_key

# 查询 3 天天气预报
node scripts/query.js --city=杭州

# 查询实时天气
node scripts/query.js --city=杭州 --type=realtime
```

**文档**: [SKILL.md](weather/SKILL.md)

## 🔑 API Key 配置

大部分 Skills 需要配置相应的 API Key：

### 高德地图 API Key

1. 访问 [高德开放平台](https://lbs.amap.com/api/webservice/create-project-and-key)
2. 创建应用并获取 Web Service Key
3. 配置方式：
   - 环境变量：`export AMAP_KEY=your_key`
   - 配置文件：在对应目录创建 `config.json`

### B 站凭证

在 `bilibili_reply/SKILL.md` 的 YAML frontmatter 中配置：
```yaml
credentials:
  sessdata: "your_sessdata"
  bili_jct: "your_bili_jct"
```

## 📝 使用说明

### 安装依赖

每个 Skill 都是独立的模块，进入对应目录安装依赖：

```bash
# Node.js 项目
cd <skill-directory>
npm install

# Python 项目
cd <skill-directory>
pip install -r requirements.txt
```

### 运行脚本

```bash
# Node.js
node scripts/xxx.js --param=value

# Python
python3 scripts/xxx.py --param=value
```

## ⚠️ 注意事项

1. **API Key 安全**: 请勿将包含真实 API Key 的 `config.json` 提交到公开仓库
2. **调用频率**: 各平台 API 有调用频率限制，请合理使用
3. **凭证有效期**: B 站凭证会过期，需要定期更新
4. **node_modules**: 建议删除后重新运行 `npm install`

## 📄 License

各项目采用 MIT License，详见各目录下的 LICENSE 文件。

## 🔗 相关链接

- [高德开放平台](https://lbs.amap.com/)
- [B 站开放平台](https://open.bilibili.com/)
- [Hermes Agent](https://github.com/ych18/hyperagents)
