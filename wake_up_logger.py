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

def get_weather():
    """获取天气信息（示例：使用和风天气 API）"""
    try:
        # 这里需要替换成您的和风天气 API key
        api_key = os.getenv('WEATHER_API_KEY')
        if not api_key:
            return ""
            
        # 这里使用南京的经纬度作为示例
        lat = "32.0587"
        lon = "118.7969"
        url = f"https://api.qweather.com/v7/weather/now?location={lon},{lat}&key={api_key}"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather = data['now']
            return f"温度: {weather['temp']}°C, {weather['text']}"
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
        print("打卡成功！")
        
    except Exception as e:
        print(f"打卡失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()