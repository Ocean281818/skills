#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili 实时监控脚本 - 秋芝 Skill 专用
用于实时查看 Bilibili 数据，支持查看 UP 主信息、视频详情、排行榜等

安装依赖:
    pip3 install bilibili-api-python aiohttp

使用示例:
    # 查看秋芝 UP 主信息 (UID: 385670211)
    python bilibili_monitor.py user --uid 385670211
    
    # 查看视频详情
    python bilibili_monitor.py video --bvid BV1xx411c7mD
    
    # 查看排行榜
    python bilibili_monitor.py ranking
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime

try:
    from bilibili_api import video, user, Credential, sync, get_session
    from bilibili_api.video import Video
    from bilibili_api.user import User
    video_module = video
except ImportError:
    print("错误：未安装 bilibili-api-python")
    print("请运行：pip3 install bilibili-api-python aiohttp")
    sys.exit(1)


async def setup_request_headers():
    """设置请求头以绕过风控"""
    session = get_session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    session.headers['Referer'] = 'https://www.bilibili.com'


class BilibiliMonitor:
    """Bilibili 数据监控器 - 供秋芝 Skill 调用"""
    
    def __init__(self, sessdata=None, bili_jct=None):
        """
        初始化监控器
        
        Args:
            sessdata: Bilibili 登录凭证 SESSDATA (可选)
            bili_jct: Bilibili 登录凭证 bili_jct (可选)
        """
        self.credential = None
        if sessdata and bili_jct:
            self.credential = Credential(sessdata=sessdata, bili_jct=bili_jct)
    
    async def get_video_info(self, bvid=None, aid=None):
        """
        获取视频详细信息
        
        Args:
            bvid: 视频 BV 号
            aid: 视频 AV 号
            
        Returns:
            视频信息字典
        """
        try:
            if bvid:
                v = Video(bvid=bvid, credential=self.credential)
            elif aid:
                v = Video(aid=aid, credential=self.credential)
            else:
                return {"error": "请提供 bvid 或 aid"}
            
            info = await v.get_info()
            
            # 获取统计数据，可能来自 info 中的 stat 字段
            stat = info.get("stat", {})
            if not stat:
                try:
                    stat = await v.get_stat()
                    # 如果返回的是 VideoStatus 对象，转换为字典
                    if hasattr(stat, '__dict__'):
                        stat = {k: v for k, v in stat.__dict__.items() if not k.startswith('_')}
                except Exception:
                    stat = {}
            
            return {
                "bvid": info.get("bvid", ""),
                "aid": info.get("aid", 0),
                "title": info.get("title", ""),
                "desc": (info.get("desc", "") or "")[:200],
                "owner": info.get("owner", {}),
                "pubdate": info.get("pubdate", 0),
                "duration": info.get("duration", 0),
                "stat": stat,
            }
        except Exception as e:
            return {"error": f"获取视频信息失败: {str(e)}"}
    
    async def get_user_info(self, uid):
        """
        获取用户信息
        
        Args:
            uid: 用户 UID
            
        Returns:
            用户信息字典
        """
        try:
            u = User(uid, credential=self.credential)
            info = await u.get_user_info()
            
            # 获取粉丝数和关注数 (需要单独调用 get_relation_info)
            follower = 0
            following = 0
            try:
                relation_info = await u.get_relation_info()
                follower = relation_info.get("follower", 0)
                following = relation_info.get("following", 0)
            except Exception:
                pass
            
            # 获取视频数量 (需要单独调用 get_overview_stat)
            archive_count = 0
            try:
                overview = await u.get_overview_stat()
                archive_count = overview.get("video", 0)
            except Exception:
                pass
            
            return {
                "uid": uid,
                "name": info.get("name", ""),
                "sign": info.get("sign", ""),
                "level": info.get("level", 0),
                "follower": follower,
                "following": following,
                "archive_count": archive_count,
                "face": info.get("face", ""),
                "official": info.get("official", {}),
            }
        except Exception as e:
            return {"error": f"获取用户信息失败: {str(e)}"}
    
    async def get_user_videos(self, uid, page_size=10):
        """
        获取 UP 主视频列表
        
        Args:
            uid: UP 主 UID
            page_size: 返回视频数量
            
        Returns:
            视频列表
        """
        try:
            u = User(uid, credential=self.credential)
            videos = await u.get_videos(ps=page_size)
            result = []
            for v in videos.get("list", {}).get("vlist", [])[:page_size]:
                result.append({
                    "bvid": v.get("bvid", ""),
                    "title": v.get("title", ""),
                    "play": v.get("play", 0),
                    "likes": v.get("likes", 0),
                    "comments": v.get("comments", 0),
                    "length": v.get("length", 0),
                    "created": v.get("created", 0),
                })
            return {"videos": result, "total": videos.get("list", {}).get("count", 0)}
        except Exception as e:
            return {"error": f"获取用户视频列表失败: {str(e)}"}
    
    async def get_ranking(self, rid=0, pt=3):
        """
        获取排行榜
        
        Args:
            rid: 分区 ID (0=全站)
            pt: 时间 (3=三日，7=七日)
            
        Returns:
            排行榜数据
        """
        try:
            ranking = await video_module.get_popular(rid=rid, pt=pt)
            result = []
            for v in ranking.get("list", [])[:10]:
                result.append({
                    "bvid": v.get("bvid", ""),
                    "title": v.get("title", ""),
                    "play": v.get("stat", {}).get("view", 0),
                    "like": v.get("stat", {}).get("like", 0),
                    "coin": v.get("stat", {}).get("coin", 0),
                })
            return {"ranking": result}
        except Exception as e:
            return {"error": f"获取排行榜失败: {str(e)}"}
    
    async def get_video_comments(self, bvid, page_size=10):
        """
        获取视频评论
        
        Args:
            bvid: 视频 BV 号
            page_size: 评论数量
            
        Returns:
            评论列表
        """
        try:
            v = Video(bvid=bvid, credential=self.credential)
            comments = await v.get_comments(page_size=page_size)
            result = []
            for c in comments.get("replies", [])[:page_size]:
                result.append({
                    "oid": c.get("oid", 0),
                    "uname": c.get("member", {}).get("uname", ""),
                    "message": c.get("content", {}).get("message", ""),
                    "like": c.get("like", 0),
                    "reply": c.get("rcount", 0),
                })
            return {"comments": result, "total": comments.get("page", {}).get("count", 0)}
        except Exception as e:
            return {"error": f"获取视频评论失败: {str(e)}"}


def format_output(data):
    """格式化输出为 JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


async def main():
    await setup_request_headers()
    parser = argparse.ArgumentParser(description="Bilibili 实时监控脚本 - 秋芝 Skill 专用")
    subparsers = parser.add_subparsers(dest="command", help="命令类型")
    
    # video 命令
    video_parser = subparsers.add_parser("video", help="查看视频详情")
    video_parser.add_argument("--bvid", type=str, help="视频 BV 号")
    video_parser.add_argument("--aid", type=int, help="视频 AV 号")
    
    # user 命令
    user_parser = subparsers.add_parser("user", help="查看用户信息")
    user_parser.add_argument("--uid", type=int, required=True, help="用户 UID")
    
    # videos 命令
    videos_parser = subparsers.add_parser("videos", help="查看 UP 主视频列表")
    videos_parser.add_argument("--uid", type=int, required=True, help="UP 主 UID")
    videos_parser.add_argument("--count", type=int, default=10, help="返回视频数量")
    
    # ranking 命令
    ranking_parser = subparsers.add_parser("ranking", help="查看排行榜")
    ranking_parser.add_argument("--rid", type=int, default=0, help="分区 ID (0=全站)")
    ranking_parser.add_argument("--pt", type=int, default=3, help="时间 (3=三日，7=七日)")
    
    # comments 命令
    comments_parser = subparsers.add_parser("comments", help="查看视频评论")
    comments_parser.add_argument("--bvid", type=str, required=True, help="视频 BV 号")
    comments_parser.add_argument("--count", type=int, default=10, help="返回评论数量")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    monitor = BilibiliMonitor()
    
    if args.command == "video":
        if not args.bvid and not args.aid:
            print("错误：请提供 --bvid 或 --aid")
            sys.exit(1)
        result = await monitor.get_video_info(bvid=args.bvid, aid=args.aid)
    elif args.command == "user":
        result = await monitor.get_user_info(args.uid)
    elif args.command == "videos":
        result = await monitor.get_user_videos(args.uid, page_size=args.count)
    elif args.command == "ranking":
        result = await monitor.get_ranking(rid=args.rid, pt=args.pt)
    elif args.command == "comments":
        result = await monitor.get_video_comments(args.bvid, page_size=args.count)
    else:
        print(f"未知命令：{args.command}")
        sys.exit(1)
    
    format_output(result)


if __name__ == "__main__":
    asyncio.run(main())
