import requests
from lxml import etree
from markdownify import markdownify as md


res = requests.get("https://news.idmzj.com/article/79307.html")
html = etree.HTML(res.text)
content_html = html.xpath("//div[@class='news_content autoHeight']")[0]
for ele in content_html.xpath("./div[contains(@class,'news_content_head')]")[0]:
    if ele.attrib.get("class") == "news_content_info":
        ele.getparent().remove(ele)

for ele in content_html.xpath(
    ".//div[@class='news_content_foot li_img_de']/div[@class='u_comfoot']"
)[0]:
    if ele.attrib.get("class") == "bd_share":
        ele.getparent().remove(ele)
content_str = etree.tostring(content_html, encoding="utf-8").decode()
content_md = md(content_str)
print(content_md)
with open("test.md", "w", encoding="utf-8") as f:
    f.write(content_md)
