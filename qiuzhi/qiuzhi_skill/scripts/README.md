# Scripts 目录

此目录用于存放可执行脚本，供秋芝 skill 调用。

## 用途说明

脚本文件只执行不读取，不占用 token。适合以下场景：

- 自动生成视频脚本模板
- 批量处理 AI 工具测评数据
- 自动化内容发布流程
- 数据采集和分析脚本
- **实时查看 Bilibili 数据**

## 可用脚本

### 1. bilibili_monitor.py - Bilibili 实时监控脚本

基于 [bilibili-api](https://github.com/Nemo2011/bilibili-api) 实现，用于实时查看 Bilibili 数据。

#### 安装依赖

```bash
pip3 install bilibili-api-python aiohttp
```

#### 功能列表

| 命令 | 说明 | 参数 |
|------|------|------|
| `user` | 查看用户信息 | `--uid` 用户 UID |
| `videos` | 查看 UP 主视频列表 | `--uid` 用户 UID, `--count` 数量 |
| `video` | 查看视频详情 | `--bvid` BV 号 或 `--aid` AV 号 |
| `ranking` | 查看排行榜 | `--rid` 分区 ID, `--pt` 时间 |
| `comments` | 查看视频评论 | `--bvid` BV 号，`--count` 数量 |

#### 使用示例

```bash
# 查看用户信息 (秋芝2046 UID: 385670211)
python bilibili_monitor.py user --uid 385670211

# 查看 UP 主最新 10 个视频
python bilibili_monitor.py videos --uid 385670211 --count 10

# 查看视频详情
python bilibili_monitor.py video --bvid BV1xx411c7mD

# 查看全站热门排行榜
python bilibili_monitor.py ranking

# 查看科技区排行榜 (rid=36 为科技区)
python bilibili_monitor.py ranking --rid 36 --pt 7

# 查看视频评论
python bilibili_monitor.py comments --bvid BV1xx411c7mD --count 20
```

#### 输出格式

所有命令输出均为 JSON 格式，便于程序解析：

```json
{
  "uid": 12345678,
  "name": "秋芝",
  "sign": "AI 工具测评 | Agent 配置教程 | 国产 AI 安利",
  "level": 6,
  "follower": 100000,
  "likes": 500000,
  "archive_count": 150
}
```

#### 常用分区 ID (rid)

| 分区 | rid |
|------|-----|
| 全站 | 0 |
| 动画 | 1 |
| 游戏 | 4 |
| 音乐 | 3 |
| 科技 | 36 |
| 数码 | 188 |
| 生活 | 160 |

#### 时间参数 (pt)

| 参数 | 说明 |
|------|------|
| 3 | 三日热门 |
| 7 | 七日热门 |

### 2. 其他脚本

可根据需要添加：
- `generate_script.py` - 生成视频脚本
- `analyze_data.py` - 分析测评数据
- `publish_helper.py` - 发布辅助工具

## 在秋芝 Skill 中调用

在 skill 中可以通过执行脚本获取实时数据：

```python
import subprocess
import json

# 获取秋芝的 B 站数据
result = subprocess.run(
    ["python", "scripts/bilibili_monitor.py", "user", "--uid", "385670211"],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
print(f"秋芝当前粉丝数：{data['follower']}")
```

## 注意事项

1. 部分功能需要登录凭证（SESSDATA 和 bili_jct），可在需要时传入
2. 请遵守 Bilibili 的使用条款，不要频繁调用导致被封禁
3. 本脚本仅供学习和测试使用
