import os
from pathlib import Path

import requests
from lxml import etree
from argparse import ArgumentParser
from markdownify import markdownify as md

from configure import print_info, print_warning, print_error, config, logger


def get_args():
    """
    :return:
    """
    parser = ArgumentParser(description="download the articles and images in the url")
    parser.add_argument(
        "--article",
        "-a",
        help="download count of articles",
        type=int,
        default=config.get("ARTICLE_COUNT", 3),
    )
    parser.add_argument(
        "--image",
        "-i",
        help="download count of imgs",
        default=config.get("IMG_DOWNLOAD_PAGE_COUNT", 0),
        type=int,
    )
    parser.add_argument(
        "--article-outputdir",
        "-ao",
        help="The URL to count words from",
        default=config.get("DOWNLOAD_DIR", "./download"),
        type=str,
    )
    parser.add_argument(
        "--image-outputdir",
        "-io",
        help="The URL to count words from",
        default=config.get("DOWNLOAD_IMG_DIR", "./download/imgs"),
        type=str,
    )
    parser.add_argument(
        "--article_start_page",
        "-as",
        help="The Page where parse article start",
        default=config.get("START_PAGE", 1),
        type=int,
    )
    parser.add_argument(
        "--img_start_page",
        "-is",
        help="The Page where parse imgs start",
        default=config.get("START_IMG_PAGE", 1),
        type=int,
    )
    parser.add_argument(
        "--http_proxy",
        "-p",
        help="set http proxy",
        default=config.get("http_proxy", None),
        type=str,
    )
    parser.add_argument(
        "--https_proxy",
        "-sp",
        help="set https proxy",
        default=config.get("https_proxy", None),
        type=str,
    )
    parser.add_argument(
        "--reserve",
        "-r",
        help="reserve original converted markdown file or not",
        default=config.get("RESERVE_ORIGINAL", True) in ["True", "true", "1", True],
        type=bool,
    )

    # 解析命令行参数
    params = parser.parse_args()
    return params


def request_url(url):
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
            print_info(f"page:{index}| parse {idx+1} article,exit...")
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
        next_page_url = f"{config.get('URL')}{next_page}"
        print_info(f"next page url is {next_page_url}")
        res = request_url(next_page_url)
        parser_page(res, count - length_per_page, index + 1)


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
    if args.reserve:
        with open(
            f"{args.download_dir}/{article_info.get('title')}.md",
            "w+",
            encoding="utf-8",
        ) as f:
            f.write(md_content)
        print_info(f"make article {article_info.get('title')} success")
    else:
        print_info(
            f"transform content of article {article_info.get('title')} using llm"
        )
        # TODO add support for llm


def process_article(count, start_index):
    """
    :param count:
    :param start_index:
    :return:
    """
    if count <= 0:
        print_info("parse article count is less than 0,exit...")
        return
    url = config.get("URL")
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
    user_prompt = config.get("USER_PROMPT")
    llm_api = config.get("LLM_API")
    data = {"user_prompt": user_prompt, "content": content}
    res = requests.get(llm_api, data=data)
    if res.status_code == 200:
        process_available_models(res.json())


def process_img(img_page_count, start_index):
    """
    :param start_index:
    :param img_page_count:
    :return:
    """
    if img_page_count <= 0:
        print_info("parse img count is less than 0,exit...")
        return
    url = config.get("IMG_DOWNLOAD_URL")
    res = request_url(url)
    count = args.img_download_page_count
    request_img(res, count, start_index)


def request_img(html_doc, img_page_count, index):
    """
    :param html_doc:
    :param index:
    :param img_page_count:
    :return:
    """
    html = etree.HTML(html_doc)
    img_list = html.xpath("//div[@class='briefnews_con']")[0]
    img_per_page = len(img_list)
    print_info(f"page {index} has {img_per_page} images...\nstart parsing...")
    for idx, img_url in enumerate(img_list):
        if idx >= img_page_count:
            print_info(f"page:{index}| parse {idx+1} image,exit...")
            break
        print_info(f"parse {idx+1} images")
        title = img_url.xpath(".//h3/a/text()")[0]
        img_url = img_url.xpath(".//h3/a/@href")[0]
        print_info(f"image url is {img_url}")
        logger.info(f"title:{title}|image url:{img_url}")
        parse_img(title, img_url)
    if img_page_count > img_per_page:
        next_page = html.xpath("//div[@class='page']/a[@class='next']/@href")[0]
        next_page_url = f"{args.IMG_URL}{next_page}"
        print_info(f"next page url is {next_page_url}")
        res = request_url(next_page_url)
        request_img(res, img_page_count - img_per_page, index + 1)


def download_img(img_url, dir_path, title):
    """
    :param dir_path:
    :param img_url:
    :param title:
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
    """
    :param file_title:
    :param img_url:
    :return:
    """
    res = request_url(img_url)
    html = etree.HTML(res)
    imgs = html.xpath("//div[@class='news_content_con']//p/img/@src")
    title_img = html.xpath("//div[@class='news_content_con']//p/img/@title")
    for img, title in zip(imgs, title_img):
        print_info(f"image url is {img}")
        logger.info(f"title:{title}|image url:{img}")
        dir_path = os.path.join(args.download_img_dir, file_title)
        download_img(img, dir_path, title)


if __name__ == "__main__":
    # parse args
    args = get_args()
    proxy = {
        "http": config.get("http_proxy"),
        "https": config.get("https_proxy"),
    }
    # process article and imgs
    process_article(args.article_count, args.start_page)
    process_img(args.img_download_page_count, args.start_img_page)
