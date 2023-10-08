
# Project Name
dmzj_news
[EN](README.md)|[ZH](README_ZH.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
<br />
scape dmzj news and images and convert articles to markdown

## Features
- logging and pretty print
- argument parser
- load variables from .env file

## usage

```bash
git clone https://github.com/drowning-in-codes/dmzj_news.git
python venv -m ./venv
source ./venv/bin/activate
pip install -r requirements.txt
python app.py
```
or use Poery
```bash
git clone https://github.com/drowning-in-codes/dmzj_news.git
poetry install
poetry shell
python app.py
```
### Env setting
```commandline .env
;  log setting
LOG_DIR = "./logs"

; markdown setting
RESERVE_ORIGINAL = True
;  download setting
URL = 'https://news.idmzj.com'
DOWNLOAD_DIR = "./download"
START_PAGE = 1
article_count = 3

; llm setting
llm_models_api = "http://host:port/supports"
llm_api = "http://host:port"
site_id = 1
model_id =
USER_PROMPT = "将下面的文章风格改写为公众号风格,但基本内容不要变"

; img url
IMG_URL = "https://news.idmzj.com/meituxinshang"
IMG_DOWNLOAD_DIR = "./download/img"
IMG_DOWNLOAD_PAGE_COUNT = 2
START_IMG_PAGE = 1

# proxy setting
http_proxy = "http://"
https_proxy = "https://"
```

### Todo

- [ ] coroutine support using aiohttp
- [ ] add more sites

### In Progress
- [ ] add llm support to transform content