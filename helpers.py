import random
import re
#import logging
from datetime import datetime, timedelta
from typing import Optional




def parse_toutiao_time(time_str: str) -> Optional[datetime]:
    """解析微博时间字符串"""
    if not time_str:
        return None

    try:
        # 清理时间字符串
        time_str = time_str.strip()

        # 处理相对时间
        if '秒前' in time_str:
            seconds = int(re.search(r'(\d+)', time_str).group(1))
            return datetime.now() - timedelta(seconds=seconds)

        elif '分钟前' in time_str:
            minutes = int(re.search(r'(\d+)', time_str).group(1))
            return datetime.now() - timedelta(minutes=minutes)

        elif '小时前' in time_str:
            hours = int(re.search(r'(\d+)', time_str).group(1))
            return datetime.now() - timedelta(hours=hours)

        elif '天前' in time_str:
            days = int(re.search(r'(\d+)', time_str).group(1))
            return datetime.now() - timedelta(days=days)

        elif '今天' in time_str:
            # 提取时间部分
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                today = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                return today

        elif '昨天' in time_str:
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                yesterday = datetime.now() - timedelta(days=1)
                yesterday = yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return yesterday

        # 处理绝对时间格式
        time_formats = [
            '%a %b %d %H:%M:%S %z %Y',  # RFC 2822格式: Mon Mar 01 01:27:11 +0800 2021
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%m-%d %H:%M',
            '%m月%d日 %H:%M',
            '%m月%d日',
            '%Y年%m月%d日 %H:%M:%S',
            '%Y年%m月%d日 %H:%M',
            '%Y年%m月%d日'
        ]

        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(time_str, fmt)
                # 如果没有年份，使用当前年份
                if parsed_time.year == 1900:
                    parsed_time = parsed_time.replace(year=datetime.now().year)
                return parsed_time
            except ValueError:
                continue

        # 如果都无法解析，返回当前时间
        print(f"无法解析时间字符串: {time_str}")
        return datetime.now()

    except Exception as e:
        print(f"解析时间失败: {e}")
        return datetime.now()