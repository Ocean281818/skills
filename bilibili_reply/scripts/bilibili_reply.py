#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili 评论回复脚本 - 自动回复 Bilibili 评论

安装依赖:
    pip3 install bilibili-api-python aiohttp

使用示例:
    # 获取评论列表
    python bilibili_reply.py list --bvid BV1xx411c7mD
    
    # 回复指定评论
    python bilibili_reply.py reply --rpid 123456 --message "感谢支持！"
    
    # AI 自动回复（需要设置环境变量）
    python bilibili_reply.py auto --bvid BV1xx411c7mD --count 5
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

try:
    from bilibili_api import video, Credential, get_session
    from bilibili_api.video import Video
    from bilibili_api import comment
    from bilibili_api.comment import CommentResourceType, OrderType
except ImportError:
    print("错误：未安装 bilibili-api-python")
    print("请运行：pip3 install bilibili-api-python aiohttp")
    sys.exit(1)


async def setup_request_headers():
    """设置请求头以绕过风控"""
    session = get_session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    session.headers['Referer'] = 'https://www.bilibili.com'


# 注意：不要硬编码凭证！请使用环境变量
# export BILI_SESSDATA="xxx"
# export BILI_BILI_JCT="xxx"


class BilibiliReplyBot:
    """Bilibili 评论回复机器人"""
    
    def __init__(self, sessdata=None, bili_jct=None):
        """
        初始化机器人
        
        Args:
            sessdata: Bilibili 登录凭证 SESSDATA
            bili_jct: Bilibili 登录凭证 bili_jct
        """
        # 从环境变量获取凭证
        if not sessdata:
            sessdata = os.environ.get('BILI_SESSDATA')
        if not bili_jct:
            bili_jct = os.environ.get('BILI_BILI_JCT')
        
        if not sessdata or not bili_jct:
            raise ValueError("需要提供 SESSDATA 和 bili_jct，请设置环境变量或在命令行中传入")
        
        self.credential = Credential(sessdata=sessdata, bili_jct=bili_jct)
    
    async def get_video_comments(self, bvid, page_size=20):
        """
        获取视频评论列表
        
        Args:
            bvid: 视频 BV 号
            page_size: 评论数量
            
        Returns:
            评论列表
        """
        try:
            v = Video(bvid=bvid, credential=self.credential)
            # 获取视频 aid
            info = await v.get_info()
            aid = info.get('aid', 0)
            
            # 获取评论
            comments = await comment.get_comments(
                oid=aid,
                type_=CommentResourceType.VIDEO,
                credential=self.credential
            )
            
            result = []
            for c in comments.get("replies", [])[:page_size]:
                result.append({
                    "rpid": c.get("rpid", 0),
                    "parent": c.get("parent", 0),
                    "root": c.get("root", 0),
                    "mid": c.get("member", {}).get("mid", 0),
                    "uname": c.get("member", {}).get("uname", ""),
                    "message": c.get("content", {}).get("message", ""),
                    "like": c.get("like", 0),
                    "ctime": c.get("ctime", 0),
                })
            return {"comments": result, "total": comments.get("page", {}).get("count", 0), "aid": aid}
        except Exception as e:
            return {"error": f"获取评论失败: {str(e)}"}
    
    async def reply_comment(self, oid, rpid, message, root=None):
        """
        回复评论
        
        Args:
            oid: 视频 aid
            rpid: 要回复的评论 ID
            message: 回复内容
            root: 根评论 ID（回复楼中楼时需要）
            
        Returns:
            回复结果
        """
        try:
            # root 是根评论ID，parent 是父评论ID
            # 如果 root 为空，说明是回复一级评论，root 和 parent 都设为 rpid
            # 如果 root 不为空，说明是回复楼中楼，parent 设为 rpid
            if root is None:
                root = rpid
                parent = rpid
            else:
                parent = rpid
            
            result = await comment.send_comment(
                text=message,
                oid=oid,
                type_=CommentResourceType.VIDEO,
                root=root,
                parent=parent,
                credential=self.credential
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def auto_reply(self, bvid, count=5, style="friendly"):
        """
        AI 自动回复评论
        
        Args:
            bvid: 视频 BV 号
            count: 回复数量
            style: 回复风格 (friendly, professional, funny)
            
        Returns:
            回复结果列表
        """
        # 获取评论列表
        comments_data = await self.get_video_comments(bvid, page_size=count)
        
        if "error" in comments_data:
            return comments_data
        
        comments = comments_data.get("comments", [])
        aid = comments_data.get("aid", 0)
        
        results = []
        for c in comments[:count]:
            # 生成回复内容
            reply_text = self._generate_reply(c["message"], style)
            
            # 发送回复
            result = await self.reply_comment(
                oid=aid,
                rpid=c["rpid"],
                message=reply_text,
                root=c["root"] if c["root"] else c["rpid"]
            )
            
            results.append({
                "original": c["message"],
                "uname": c["uname"],
                "reply": reply_text,
                "success": result.get("success", False),
                "error": result.get("error", "")
            })
            
            # 避免发送过快
            await asyncio.sleep(2)
        
        return {"results": results}
    
    def _generate_reply(self, original_message, style="friendly"):
        """
        根据原评论生成回复内容
        
        Args:
            original_message: 原评论内容
            style: 回复风格
            
        Returns:
            生成的回复
        """
        # 简单的回复模板（实际使用时可以接入 AI）
        templates = {
            "friendly": [
                "感谢支持！有什么问题欢迎继续交流~",
                "谢谢你的评论！希望能帮到你~",
                "收到！感谢观看，记得三连支持哦~",
                "感谢反馈！会继续努力的~",
            ],
            "professional": [
                "感谢您的反馈，我们会持续改进。",
                "收到您的建议，感谢支持。",
                "感谢关注，欢迎提出更多建议。",
            ],
            "funny": [
                "好家伙，你说得对！",
                "这波操作我给满分！",
                "懂的都懂，三连走起~",
            ]
        }
        
        # 根据评论关键词选择回复
        if "加油" in original_message or "支持" in original_message:
            return "感谢支持！会继续努力做出好内容的~"
        elif "教程" in original_message or "怎么" in original_message:
            return "感谢关注！有问题可以在评论区继续交流~"
        elif "好" in original_message or "赞" in original_message:
            return "谢谢认可！记得三连支持哦~"
        else:
            # 随机选择模板
            import random
            return random.choice(templates.get(style, templates["friendly"]))


def format_output(data):
    """格式化输出为 JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


async def main():
    parser = argparse.ArgumentParser(description="Bilibili 评论回复脚本")
    
    # 全局参数
    parser.add_argument("--sessdata", type=str, help="Bilibili SESSDATA")
    parser.add_argument("--bili_jct", type=str, help="Bilibili bili_jct")
    
    subparsers = parser.add_subparsers(dest="command", help="命令类型")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="获取评论列表")
    list_parser.add_argument("--bvid", type=str, required=True, help="视频 BV 号")
    list_parser.add_argument("--count", type=int, default=20, help="评论数量")
    
    # reply 命令
    reply_parser = subparsers.add_parser("reply", help="回复指定评论")
    reply_parser.add_argument("--bvid", type=str, required=True, help="视频 BV 号")
    reply_parser.add_argument("--rpid", type=int, required=True, help="评论 ID")
    reply_parser.add_argument("--message", type=str, required=True, help="回复内容")
    
    # auto 命令
    auto_parser = subparsers.add_parser("auto", help="AI 自动回复")
    auto_parser.add_argument("--bvid", type=str, required=True, help="视频 BV 号")
    auto_parser.add_argument("--count", type=int, default=5, help="回复数量")
    auto_parser.add_argument("--style", type=str, default="friendly", 
                            choices=["friendly", "professional", "funny"],
                            help="回复风格")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    await setup_request_headers()
    
    try:
        bot = BilibiliReplyBot(sessdata=args.sessdata, bili_jct=args.bili_jct)
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置环境变量 BILI_SESSDATA 和 BILI_BILI_JCT，或在命令行中传入 --sessdata 和 --bili_jct")
        sys.exit(1)
    
    if args.command == "list":
        result = await bot.get_video_comments(args.bvid, page_size=args.count)
    elif args.command == "reply":
        # 先获取视频 aid
        v = Video(bvid=args.bvid, credential=bot.credential)
        info = await v.get_info()
        aid = info.get('aid', 0)
        result = await bot.reply_comment(oid=aid, rpid=args.rpid, message=args.message)
    elif args.command == "auto":
        result = await bot.auto_reply(args.bvid, count=args.count, style=args.style)
    else:
        print(f"未知命令：{args.command}")
        sys.exit(1)
    
    format_output(result)


if __name__ == "__main__":
    asyncio.run(main())
