import json

import requests
import asyncio
from argparse import ArgumentParser
import os
from lxml import etree
from configure import print_info, print_warning, print_error, config, logger
from markdownify import markdownify as md
from pathlib import Path


def get_args():
    """
    :return:
    """
    parser = ArgumentParser(description="Get the number of words in a URL")
    parser.add_argument("url", help="The URL to count words from", type=str)
    parser.add_argument(
        "-w", "--workers", help="Number of workers to use", type=int, default=1
    )
    return parser.parse_args()


def request_url(url, proxy=None):
    """
    :param url:
    :param proxy:
    :return:
    """
    response = requests.get(url, headers=config.get("headers"), proxies=proxy)
    if response.status_code != 200:
        print_warning(f"request url {url} failed")
        logger.warning(f"request url {url} failed")
    return response.text


def parser_page(html_doc: str, count: int, index: int):
    """
    :param html_doc:
    :param count:
    :param index:
    :return:
    """
    html = etree.HTML(html_doc)
    page_news_list = html.xpath("//div[@class='briefnews_con_li']")
    length_per_page = len(page_news_list)
    article_info = {}
    print_info(f"page {index} has {length_per_page} articles...\nstart parsing...")
    for idx, news in enumerate(page_news_list):
        if idx >= count:
            break
        print_info(f"parse {idx+1} article")
        title = news.xpath(".//h3/a/text()")[0]
        tags = " ".join(news.xpath(".//div[@class='u_comfoot']/a/span/text()"))
        href = news.xpath(".//h3/a/@href")[0]
        publish_time = news.xpath(".//p[@class='head_con_p_o']/span[1]/text()")[0]
        article_info["title"] = title
        article_info["tags"] = tags
        article_info["href"] = href
        article_info["publish_time"] = publish_time
        make_article(article_info)
    if length_per_page < count:
        next_page = html.xpath("//div[@class='page']/a[@class='next']/@href")[0]
        next_page_url = f"{os.getenv('URL')}{next_page}"
        print_info(f"next page url is {next_page_url}")
        res = request_url(next_page_url)
        parser_page(res, count - length_per_page, index + 1)
        print(next_page_url)


def remove_trivial(html_doc: etree.Element):
    """
    :param html_doc:
    :return:
    """
    for ele in html_doc.xpath("./div[contains(@class,'news_content_head')]")[0]:
        if ele.attrib.get("class") == "news_content_info":
            ele.getparent().remove(ele)

    for ele in html_doc.xpath(
        ".//div[@class='news_content_foot li_img_de']/div[@class='u_comfoot']"
    )[0]:
        if ele.attrib.get("class") == "bd_share":
            ele.getparent().remove(ele)
    content_str = etree.tostring(html_doc, encoding="utf-8").decode()
    return content_str


def make_article(article_info):
    """
    :param article_info:
    :return:
    """
    href = article_info.get("href")
    if href is None:
        print_warning(f"article {article_info.get('title')} href is None")
        logger.warning(f"article {article_info.get('title')} href is None")
    article_content = request_url(href)
    html = etree.HTML(article_content)
    content = html.xpath("//div[@class='news_content autoHeight']")[0]
    content_str = remove_trivial(content)
    md_content = md(content_str)
    print(md_content)
    with open(
        f"{download_dir}/{article_info.get('title')}.md", "w+", encoding="utf-8"
    ) as f:
        f.write(md_content)
    print_info(f"make article {article_info.get('title')} success")


def process_article(count, start_index):
    """
    :param count:
    :param start_index:
    :return:
    """
    url = os.getenv("URL")
    res = request_url(url)
    parser_page(res, count, start_index)


def process_available_models(res):
    """
    :param res:
    :return:
    """
    for i, r in enumerate(res):
        site = r.get["site"]
        model = ",".join(r.get["model"])
        print_info(f"index {i+1}:site:{site}, allowed models:{model}")
    site_idx = int(input("please choose a site to transform(index,default 1):"))
    models_list = res[site_idx - 1].get("model")
    models = ", ".join(str(i + 1) + ":" + model for i, model in enumerate(models_list))
    model_idx = int(
        input(f"please choose a model to transform(index,default 1):{models}")
    )
    model = models_list[model_idx - 1]
    return res[site_idx - 1].get["site"], model


def get_transform(content):
    """
    :param content:
    :return:
    """
    user_prompt = os.getenv("USER_PROMPT")
    llm_api = os.getenv("LLM_API")
    data = {"user_prompt": user_prompt, "content": content}
    res = requests.get(llm_api, data=data)
    if res.status_code == 200:
        process_available_models(res.json())


def request_img(img_page_count, index):
    """
    :param img_page_count:
    :return:
    """
    img_url = os.getenv("IMG_DOWNLOAD_URL")
    res = request_url(img_url)
    html = etree.HTML(res)
    img_list = html.xpath("//div[@class='briefnews_con']")[0]
    img_per_page = len(img_list)
    print_info(f"page {index} has {img_per_page} images...\nstart parsing...")
    for idx, img_url in enumerate(img_list):
        print_info(f"parse {idx+1} images")
        title = img_url.xpath(".//h3/a/text()")[0]
        img_url = img_url.xpath(".//h3/a/@href")[0]
        print_info(f"image url is {img_url}")
        logger.info(f"title:{title}|image url:{img_url}")
        parse_img(title, img_url)


def download_img(img_url, dir_path, title, proxy=None):
    """
    :param dir_path:
    :param img_url:
    :param title:
    :param proxy:
    :return:
    """
    res = requests.get(img_url, headers=config.get("headers"), proxy=proxy)
    if res.status_code != 200:
        print_warning(f"request url {img_url} failed")
        logger.warning(f"request url {img_url} failed")
    if not Path(dir_path).exists():
        print_info(f"dir {dir_path} doesn't exists,create it...")
        logger.info(f"dir {dir_path} doesn't exists,create it...")
        Path(dir_path).mkdir(parents=True)
    with open(os.path.join(dir_path, title), "wb") as f:
        f.write(res.content)
    print_info(f"download image {title} success")
    logger.info(f"download image {title} success")


def parse_img(file_title, img_url):
    res = request_url(img_url)
    html = etree.HTML(res)
    imgs = html.xpath("//div[@class='news_content_con']//p/img/@src")
    title_img = html.xpath("//div[@class='news_content_con']//p/img/@title")
    for img, title in zip(imgs, title_img):
        print_info(f"image url is {img}")
        logger.info(f"title:{title}|image url:{img}")
        dir_path = os.path.join(download_img_dir, file_title)
        download_img(img, dir_path, title)


if __name__ == "__main__":
    download_dir = os.getenv("DOWNLOAD_DIR")
    article_count = int(os.getenv("ARTICLE_COUNT"))
    start_page = int(os.getenv("START_PAGE"))
    process_article(article_count, start_page)
    download_img_dir = os.getenv("DOWNLOAD_IMG_DIR")
