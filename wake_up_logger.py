import os
import sys
import requests
from datetime import datetime
import pytz
from github import Github

# 配置
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('GITHUB_REPOSITORY')
ISSUE_NUMBER = int(os.getenv('ISSUE_NUMBER', '2'))  # 默认使用 Issue #2
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

def send_telegram_message(message):
    """发送消息到 Telegram 频道"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("未配置 Telegram 机器人令牌或频道 ID")
        return False
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Telegram 消息发送成功！")
            return True
        else:
            print(f"Telegram 消息发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"发送 Telegram 消息时出错: {str(e)}")
        return False

def get_weather():
    """获取天气信息（使用 wttr.in API）"""
    try:
        # 使用无锡的天气信息，设置温度为摄氏度
        url = "https://wttr.in/Wuxi?format=%l:+%c+%t+%w+%h&lang=zh&u=c"
        response = requests.get(url)
        if response.status_code == 200:
            weather_info = response.text.strip()
            # 替换英文城市名为中文
            weather_info = weather_info.replace("Wuxi", "无锡")
            # 重新格式化湿度显示
            parts = weather_info.split()
            if len(parts) >= 4:
                # 重新组合天气信息，将湿度放在最后
                weather_info = f"{parts[0]}: {parts[1]} {parts[2]} {parts[3]} 湿度: {parts[4]} %"
            return weather_info
    except Exception as e:
        print(f"获取天气信息失败: {str(e)}")
    return ""

def get_poem():
    """获取每日一句诗词"""
    try:
        response = requests.get("https://v1.jinrishici.com/all")
        if response.status_code == 200:
            data = response.json()
            return data.get('content', '')
    except Exception as e:
        print(f"获取诗词失败: {str(e)}")
    return "赏花归去马如飞，去马如飞酒力微，酒力微醒时已暮，醒时已暮赏花归。"

def create_wake_up_message():
    """创建起床打卡消息"""
    # 获取北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    wake_up_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 获取天气信息
    weather_info = get_weather()
    
    # 获取诗词
    poem = get_poem()
    
    # 组装消息
    message = f"⏰ 起床啦！\n\n"
    message += f"时间 (北京时间): {wake_up_time}\n\n"
    
    if weather_info:
        message += f"今日天气: {weather_info}\n\n"
    
    message += f"今日一句诗:\n{poem}"
    
    return message

def main():
    try:
        # 初始化 GitHub 客户端
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        issue = repo.get_issue(ISSUE_NUMBER)
        
        # 创建打卡消息
        message = create_wake_up_message()
        
        # 在 Issue 中添加评论
        issue.create_comment(message)
        print("GitHub 打卡成功！")
        
        # 发送到 Telegram
        send_telegram_message(message)
        
    except Exception as e:
        print(f"打卡失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()