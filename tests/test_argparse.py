import os
from argparse import ArgumentParser

parser = ArgumentParser(description="download the articles and images in the url")
t = os.getenv("fsadfsa")
print(t)
parser.add_argument(
    "--article", "-a", help="The URL to count words from", default=t, type=int
)
parser.add_argument(
    "--image", "-i", help="The URL to count words from", default=2, type=int
)
parser.add_argument(
    "--article-outputdir",
    "-ao",
    help="The URL to count words from",
    default="fasdfd",
    type=str,
)
parser.add_argument(
    "--image-outputdir",
    "-io",
    help="The URL to count words from",
    default="fasdfd",
    type=str,
)


# 解析命令行参数
args = parser.parse_args()
print(args)
