import os
import re
from datetime import datetime
import matplotlib.pyplot as plt
from github import Github
import requests  # 添加 requests 库

# 获取环境变量
ACCESS_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('GITHUB_REPOSITORY')  # 格式: "owner/repo"
ISSUE_NUMBER = 1  # 你的记录 Issue 编号

# 使用更底层的 API 调用绕过 PyGithub 的限制
def get_issue_comments():
    url = f"https://api.github.com/repos/{REPO_NAME}/issues/{ISSUE_NUMBER}/comments"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    return response.json()

# 主逻辑
try:
    print(f"开始获取 Issue #{ISSUE_NUMBER} 的评论...")
    comments = get_issue_comments()
    print(f"成功获取 {len(comments)} 条评论")
    
    # 解析起床时间
    wake_times = []
    for comment in comments:
        body = comment["body"]
        if "起床啦" in body:
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', body)
            if match:
                time_str = match.group(1)
                try:
                    wake_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    wake_times.append(wake_time)
                    print(f"找到记录: {time_str}")
                except ValueError:
                    pass
    
    # 如果没有记录，创建空图表
    if not wake_times:
        print("没有找到有效的起床时间记录")
        plt.figure(figsize=(12, 6))
        plt.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=20)
        plt.savefig('wake_up_chart.png')
        exit(0)
    
    # 按日期排序
    wake_times.sort()
    
    # 准备绘图数据
    dates = [wt.date() for wt in wake_times]
    times = [wt.hour + wt.minute / 60.0 for wt in wake_times]
    
    # 生成折线图
    plt.figure(figsize=(12, 6))
    plt.plot(dates, times, 'o-', markersize=5)
    plt.title('我的起床时间记录')
    plt.xlabel('日期')
    plt.ylabel('时间 (小时)')
    plt.ylim(0, 24)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('wake_up_chart.png')
    print("图表生成成功")
    
except Exception as e:
    print(f"发生错误: {str(e)}")
    # 创建错误图表
    plt.figure(figsize=(12, 6))
    plt.text(0.5, 0.5, '图表生成失败', ha='center', va='center', fontsize=20, color='red')
    plt.text(0.5, 0.4, str(e), ha='center', va='center', fontsize=12)
    plt.savefig('wake_up_chart.png')
    exit(1)
