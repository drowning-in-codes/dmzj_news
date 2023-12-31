# 项目名称
动漫新闻爬取
[EN](README.md)|[ZH](README_ZH.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
<br />
scape dmzj news and images and convert articles to markdown
爬取网站新闻和图片并转为markdown文件
使用<a href="https://openrouter.ai/docs">OpenRouter</a>上的模型来转换文章内容,目前模型`mistralai/mistral-7b-instruct`免费使用

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
### Env setting
```commandline .env 在目录下建立.env文件
;  log setting
LOG_DIR = "./logs"

; markdown setting
RESERVE_ORIGINAL = True
;  download setting
URL = 'https://news.idmzj.com'
DOWNLOAD_DIR = "./download"
START_PAGE = 1
ARTICLE_COUNT = 3

; llm setting
LLM_API = "https://openrouter.ai/api/v1/chat/completions"
MODEL_ID = "mistralai/mistral-7b-instruct"
USER_PROMPT = "将下面的文章风格改写为公众号风格,但基本内容不要变"
OPENROUTER_KEY = "" # your openrouter key
; img url
IMG_DOWNLOAD_URL = "https://news.idmzj.com/meituxinshang"
IMG_DOWNLOAD_DIR = "./download/img"
IMG_DOWNLOAD_PAGE_COUNT = 2
START_IMG_PAGE = 1

# proxy setting
HTTP_PROXY = ""
HTTPS_PROXY = ""
```
### 打包
下载pyinstaller
```bash
pyinstaller -F  -i dmzj.ico app.py
```

### Todo
- [x] 使用aiohttp支持协程
- [x] 增加大语言模型支持来美化内容
- [ ] 增加更多网站

### In Progress
- [ ] 增加更多网站

