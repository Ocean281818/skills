# Ollama幼儿园级教程：玩转免费开源大模型

## Ollama是什么
本地运行开源大模型的工具和启动器，一行命令`ollama run 模型名`即可运行任意开源模型。

## 安装与基础使用

### 安装
- 官网下载适合系统的版本
- 一路默认安装

### 快速体验
```bash
ollama run qwen3    # 下载并运行千问3
ollama run llama3   # 下载并运行Llama3
```

## 修改模型存储位置

### 为什么改
默认下载到C盘系统盘，太占空间

### 两步操作
1. 设置环境变量`OLLAMA_MODELS=新路径`
2. 把原模型文件夹挪到新位置

**Windows**: 系统环境变量里新建`OLLAMA_MODELS`
**Mac**: 终端输入命令设置环境变量

**默认位置**:
- Windows: `C:\Users\用户名\.ollama\models`
- Mac: `~/.ollama/models`

## 如何选择模型

### 模型标签含义
- **tool**: 能调用工具
- **vision**: 多模态，可理解图片

### 命名规则
`模型名 + 参数量(B) + 量化精度(Q)`
- 参数量越大，性能越好，越占显存
- 量化精度越大，效果越好，越占显存

### 显存参考
| 模型大小 | 显存需求 |
|---------|---------|
| 1.1GB | ~1.5GB |
| 8B参数4bit | ~8GB显存 |
| 32B参数 | ~24GB显存 |

**建议**: 让AI根据你的显卡帮你推荐

## 常用命令

| 命令 | 作用 |
|------|------|
| `ollama list` | 查看已下载模型 |
| `ollama rm 模型名` | 删除模型 |
| `ollama run 模型名 --verbose` | 查看运行细节（速度、token数） |
| `/clear` | 清除上下文 |
| `/bye` | 退出聊天 |

## 创建自定义模型

### 使用场景
1. 官网没有的开源模型（如小米Memo）
2. 基于现有模型做特制版

### 创建步骤
1. 写ModelFile文件：
```
FROM qwen3:32B
PARAMETER temperature 0.8
SYSTEM """你是用户的18岁女友小甜甜..."""
```

2. 运行创建命令：
```bash
ollama create 甜甜 -f ./ModelFile
```

### 千问3特殊指令
- `/no_think` 关闭推理模式
- 默认带推理，系统提示词加`/no_think`变纯聊天

## 聊天界面推荐

### 终端聊天
- 直接`ollama run 模型名`
- 多模态：拖拽图片或输入图片路径

### 图形界面
- **Chatwise**: 简洁，支持MCP、Artifacts，一次性付费
- **Page Assist**: 浏览器插件，免费
- **Open WebUI**: 功能丰富
- **Cherry Studio**: 支持知识库

### MCP配置
本地千问跑MCP比Claude便宜1000倍，适合文件操作、搜索、爬取等低智商任务。

## 局域网共享：家庭AI服务器

### 修改服务地址
```bash
OLLAMA_HOST=0.0.0.0 ollama serve
```

### 保持模型常驻内存
```bash
OLLAMA_KEEP_ALIVE=-1 ollama serve
```

### 手机连接
1. 查看电脑IP地址
2. 手机安装Enchanted等App
3. 填入`http://电脑IP:11434`

### 外网访问
使用内网穿透（如ngrok、frp）

## 总结
- `ollama run 模型名` 快速使用模型
- 修改环境变量改变存储位置
- 根据显存选择合适模型
- `ollama list/rm` 管理模型
- ModelFile自定义模型
- 终端/桌面端/手机端多平台使用
