# 项目名称
动漫新闻爬取
[EN](README.md)|[ZH](README_ZH.md)
<br />
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
scape dmzj news and images and convert articles to markdown
爬取网站新闻和图片并转为markdown文件
## Features
- 日志与美化打印
- 参数解析
- 从.env文件中加载变量

## usage

```bash
git clone https://github.com/drowning-in-codes/dmzj_news.git
python venv -m ./venv
source ./venv/bin/activate
pip install -r requirements.txt
python app.py
```
或者使用Poetry管理依赖
```bash
git clone https://github.com/drowning-in-codes/dmzj_news.git
poetry install
poetry shell
python app.py
```

### Todo

- [ ] 使用aiohttp支持协程
- [ ] 增加更多网站
- 
### In Progress
- [ ] 增加大语言模型支持来美化内容