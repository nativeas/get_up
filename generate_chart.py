# generate_chart.py
import os
import re
from datetime import datetime
import matplotlib.pyplot as plt
from github import Github  # 使用 PyGithub 库

# 1. 获取 GitHub Token 和仓库信息 (从 Action Secrets 或环境变量传入)
ACCESS_TOKEN = os.getenv('GH_TOKEN') or 'your_token'  # 实际用 secrets.GH_TOKEN
REPO_NAME = os.getenv('GITHUB_REPOSITORY')  # Action 环境自动提供，如 'nativeas/get_up'
ISSUE_NUMBER = 1  # 你的记录 Issue 编号

# 2. 连接 GitHub，获取 Issue 评论
g = Github(ACCESS_TOKEN)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(ISSUE_NUMBER)
comments = issue.get_comments()

# 3. 解析起床时间 (假设评论格式: "⏰ 起床啦！时间 (UTC): 2025-06-06 07:39:22")
wake_times = []
for comment in comments:
    if "起床啦" in comment.body:
        # 使用正则表达式提取时间字符串
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', comment.body)
        if match:
            time_str = match.group(1)
            try:
                # 解析时间 (注意时区，这里假设是 UTC)
                wake_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                wake_times.append(wake_time)
            except ValueError:
                pass  # 忽略格式错误的记录

# 4. 按日期排序
wake_times.sort()

# 5. 准备绘图数据 (日期和对应的时间 - 小时+分钟)
dates = [wt.date() for wt in wake_times]  # 日期部分
times = [wt.hour + wt.minute / 60.0 for wt in wake_times]  # 转换为小时小数 (如 7.5 = 7:30)

# 6. 生成折线图
plt.figure(figsize=(12, 6))
plt.plot(dates, times, 'o-', markersize=5)  # 圆点连线
plt.title('我的起床时间记录')
plt.xlabel('日期')
plt.ylabel('时间 (小时)')
plt.ylim(0, 24)  # 固定在 0-24 小时范围
plt.grid(True, alpha=0.3)
plt.tight_layout()

# 7. 保存图片
CHART_PATH = 'wake_up_chart.png'
plt.savefig(CHART_PATH)
print(f"图表已保存至: {CHART_PATH}")
