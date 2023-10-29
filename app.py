"""
@description: download the articles and images in the url
"""
import json
import os
from pathlib import Path

import requests
import aiohttp
import asyncio
from lxml import etree
from argparse import ArgumentParser
from markdownify import markdownify as md
from tqdm import tqdm
from configure import print_info, print_warning, config, logger


def get_args():
    """
    :return:
    """
    parser = ArgumentParser(description="download the articles and images in the url")
    parser.add_argument(
        "--article_count",
        "-a",
        help="download count of articles",
        type=int,
        default=config.get("ARTICLE_COUNT", 0),
    )
    parser.add_argument(
        "--image_download_page_count",
        "-i",
        help="download count of imgs",
        default=config.get("IMG_DOWNLOAD_PAGE_COUNT", 0),
        type=int,
    )
    parser.add_argument(
        "--article_outputdir",
        "-ao",
        help="The URL to count words from",
        default=config.get("DOWNLOAD_DIR", "./download"),
        type=str,
    )
    parser.add_argument(
        "--image_outputdir",
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
        default=config.get("HTTP_PROXY", None),
        type=str,
    )
    parser.add_argument(
        "--https_proxy",
        "-sp",
        help="set https proxy",
        default=config.get("HTTPS_PROXY", None),
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
    :return:
    """
    response = get_rq(url)
    if response.status_code != 200:
        print_warning(f"request url {url} failed")
        logger.warning(f"request url {url} failed")
    return response.text


async def parser_page(html_doc: str, count: int, index: int):
    """
    :param html_doc:
    :param count:
    :param index:
    :return:
    """
    html = etree.HTML(html_doc)
    page_news_list = html.xpath("//div[@class='briefnews_con_li']")
    length_per_page = len(page_news_list)
    article_infos = []
    print_info(f"page {index} has {length_per_page} articles...\nstart parsing...")
    with tqdm(total=length_per_page) as pbar:
        for idx, news in enumerate(page_news_list):
            if idx >= count:
                print_info(f"page:{index}| parse {idx+1} article,exit...")
                break
            article_info = {}
            pbar.set_description(f"page {index} parsing|parse {idx+1} articles")
            title = news.xpath(".//h3/a/text()")[0]
            tags = " ".join(news.xpath(".//div[@class='u_comfoot']/a/span/text()"))
            href = news.xpath(".//h3/a/@href")[0]
            publish_time = news.xpath(".//p[@class='head_con_p_o']/span[1]/text()")[0]
            article_info["title"] = title
            article_info["tags"] = tags
            article_info["href"] = href
            article_info["publish_time"] = publish_time
            article_infos.append(article_info)
            pbar.update()

    tasks = []
    for article_info in article_infos:
        task = asyncio.ensure_future(make_article(article_info))
        tasks.append(task)
    await asyncio.gather(*tasks)

    if length_per_page < count:
        next_page = html.xpath("//div[@class='page']/a[@class='next']/@href")[0]
        next_page_url = f"{config.get('URL')}{next_page}"
        print_info(f"next page url is {next_page_url}")
        res = request_url(next_page_url)
        await parser_page(res, count - length_per_page, index + 1)


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


async def make_article(article_info):
    """
    :param article_info:
    :return:
    """
    href = article_info.get("href")
    if href is None:
        print_warning(f"article {article_info.get('title')} href is None")
        logger.warning(f"article {article_info.get('title')} href is None")
    async with aiohttp.ClientSession() as session:
        async with session.get(href, proxy=proxy) as res:
            # article_content = request_url(href)
            article_content = await res.text()
            html = etree.HTML(article_content)
            content = html.xpath("//div[@class='news_content autoHeight']")[0]
            content_str = remove_trivial(content)
            md_content = md(content_str)
            if args.reserve:
                try:
                    with open(
                        f"{args.article_outputdir}/{article_info.get('title')}.md",
                        "w+",
                        encoding="utf-8",
                    ) as f:
                        f.write(md_content)
                    print_info(
                        f"make original article {article_info.get('title')} success"
                    )
                except Exception as e:
                    print_warning(
                        f"make original article {article_info.get('title')} failed,{e}"
                    )
                    logger.warning(
                        f"make original article {article_info.get('title')} failed,{e}"
                    )
            else:
                print_info(
                    f"transform content of article {article_info.get('title')} using llm"
                )
            transform_msg = await get_transform(content_str)
            md_content = md(transform_msg)
            try:
                with open(
                    f"{args.article_outputdir}/{article_info.get('title')}_transformed.md",
                    "w+",
                    encoding="utf-8",
                ) as f:
                    f.write(md_content)
                    print_info(
                        f"make transformed article {article_info.get('title')} success"
                    )
            except Exception as e:
                print_warning(
                    f"make transformed article {article_info.get('title')} failed,{e}"
                )
                logger.error(
                    f"make transformed article {article_info.get('title')} failed,{e}"
                )


async def process_article(count, start_index):
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
    await parser_page(res, count, start_index)


async def get_transform(content):
    """
    :param content:
    :return:
    """
    openrouter_key = config.get("OPENROUTER_KEY")
    if not openrouter_key:
        print_warning("openrouter key is None,please set key  in .env")
        logger.warning("openrouter key is None,please set key in .env")
        return
    user_prompt = config.get("USER_PROMPT", "作为一名动画评鉴大师,请改编下面一段话使其有趣通俗易懂")
    llm_api = config.get("LLM_API")
    data = json.dumps(
        {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": f"{user_prompt}:{content}"}],
        }
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=llm_api,
                data=data,
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "HTTP-Referer": "http://localhost:3000",  # To identify your app. Can be set to e.g. http://localhost:3000 for testing
                    "X-Title": "dmzj_news",  # Optional. Shows on openrouter.ai
                },
            ) as resp:
                resp_txt = await resp.text()
                return resp_txt
    except Exception as e:
        print_warning(f"transform content failed,{e}")
        logger.warning(f"transform content failed,{e}")


async def process_img(img_page_count, start_index):
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
    await request_img(res, img_page_count, start_index)


async def request_img(html_doc, img_page_count, index):
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
    titles = []
    img_urls = []
    pbar = tqdm(total=img_per_page)
    for idx, img_url in enumerate(img_list):
        if idx >= img_page_count:
            print_info(f"page:{index}| parse {idx+1} image,exit...")
            break
        pbar.set_description(f"page {index} parsing|parse {idx+1} images")
        title = img_url.xpath(".//h3/a/text()")[0]
        img_url = img_url.xpath(".//h3/a/@href")[0]
        titles.append(title)
        img_urls.append(img_url)
        print_info(f"image url is {img_url}")
        logger.info(f"title:{title}|image url:{img_url}")
        pbar.update()
    pbar.close()

    tasks = []
    for title, img_url in zip(titles, img_urls):
        task = asyncio.ensure_future(parse_img(title, img_url))
        tasks.append(task)
    await asyncio.gather(*tasks)

    if img_page_count > img_per_page:
        next_page = html.xpath("//div[@class='page']/a[@class='next']/@href")[0]
        next_page_url = f"{args.IMG_URL}{next_page}"
        print_info(f"next page url is {next_page_url}")
        res = request_url(next_page_url)
        await request_img(res, img_page_count - img_per_page, index + 1)


def get_rq(url, data=None):
    """
    :param data:
    :param url:
    :return:
    """
    if proxy:
        res = requests.get(
            url, headers=config.get("headers"), proxies=proxy, timeout=10, params=data
        )
    else:
        res = requests.get(url, headers=config.get("headers"), timeout=100, params=data)
    return res


async def download_img(img_url, dir_path, title):
    """
    :param dir_path:
    :param img_url:
    :param title:
    :return:
    """
    # res = get_rq(img_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url, proxy=proxy) as res:
            code = res.status
            if code != 200:
                print_warning(f"request url {img_url} failed")
                logger.warning(f"request url {img_url} failed")
            if not Path(dir_path).exists():
                print_info(f"dir {dir_path} doesn't exists,create it...")
                logger.info(f"dir {dir_path} doesn't exists,create it...")
                Path(dir_path).mkdir(parents=True)
            content = await res.read()
            with open(os.path.join(dir_path, title), "wb") as f:
                f.write(content)
            print_info(f"download image {title} success")
            logger.info(f"download image {title} success")


async def parse_img(file_title, img_url):
    """
    :param file_title:
    :param img_url:
    :return:
    """
    res = request_url(img_url)
    html = etree.HTML(res)
    logger.info(f"download {file_title} images...")
    print_info(f"download {file_title} images...")
    imgs = html.xpath("//div[@class='news_content_con']//p/img/@src")
    title_img = html.xpath("//div[@class='news_content_con']//p/img/@title")
    for img, title in zip(imgs, title_img):
        print_info(f"image url is {img}")
        logger.info(f"title:{title}|image url:{img}")
        dir_path = os.path.join(args.image_outputdir, file_title)
        await download_img(img, dir_path, title)


def check_proxy(p):
    """
    :param p:
    :return:
    """
    ip = p.get("http", p.get("https", "")).split("//")[-1].split(":")[0]
    if not ip:
        print_warning(f"proxy {p} is invalid,use localhost instead")
        logger.warning(f"proxy {p} is invalid,use localhost instead")
        return False
    try:
        requests.get("https://www.baidu.com", proxies=p, timeout=10)
    except Exception as e:
        print_warning(f"proxy {p} is invalid,use localhost instead")
        logger.warning(f"proxy {p} is invalid,use localhost instead")
        return False


if __name__ == "__main__":
    # parse args
    args = get_args()
    proxy = {"http": args.http_proxy, "https": args.https_proxy}
    if not check_proxy(proxy):
        proxy = None
    print_info(f"proxy is {proxy}")
    logger.info(f"proxy is {proxy}")
    # process article and imgs
    asyncio.run(process_article(args.article_count, args.article_start_page))
    asyncio.run(process_img(args.image_download_page_count, args.img_start_page))
