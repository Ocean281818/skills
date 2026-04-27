# Scripts 目录

此目录用于存放 Bilibili 评论回复相关脚本。

## bilibili_reply.py - Bilibili 评论回复脚本

### 功能

- 获取视频评论列表
- 回复指定评论
- AI 自动回复（根据评论内容生成回复）

### 安装依赖

```bash
pip3 install bilibili-api-python aiohttp
```

### 获取登录凭证

⚠️ **发送评论需要登录凭证**

1. 登录 Bilibili 网站
2. 按 F12 打开开发者工具
3. 切换到 Application → Cookies → https://www.bilibili.com
4. 找到 `SESSDATA` 和 `bili_jct` 的值

### 使用方法

#### 方式一：设置环境变量（推荐）

```bash
export BILI_SESSDATA="你的SESSDATA"
export BILI_BILI_JCT="你的bili_jct"

python bilibili_reply.py list --bvid BV1xx411c7mD
```

#### 方式二：命令行传入

```bash
python bilibili_reply.py --sessdata "你的SESSDATA" --bili_jct "你的bili_jct" list --bvid BV1xx411c7mD
```

### 命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `list` | 获取评论列表 | `python bilibili_reply.py list --bvid BV1xx411c7mD` |
| `reply` | 回复指定评论 | `python bilibili_reply.py reply --bvid BV1xx411c7mD --rpid 123456 --message "感谢支持！"` |
| `auto` | AI 自动回复 | `python bilibili_reply.py auto --bvid BV1xx411c7mD --count 5` |

### 回复风格

`auto` 命令支持三种回复风格：

- `friendly` - 友好亲切（默认）
- `professional` - 专业正式
- `funny` - 幽默风趣

```bash
python bilibili_reply.py auto --bvid BV1xx411c7mD --count 5 --style funny
```

### 注意事项

1. 请遵守 Bilibili 社区规范，不要发送违规内容
2. 回复频率不要过高，避免被判定为刷屏
3. 凭证会过期，需要定期更新
4. 本脚本仅供学习研究使用
