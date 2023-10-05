
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

### Todo

- [ ] coroutine support using aiohttp
- [ ] add more sites

### In Progress
- [ ] add llm support to transform content