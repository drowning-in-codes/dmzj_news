import os

from rich.console import Console
import logging
from dotenv import load_dotenv
import time
from pathlib import Path

# load env
load_dotenv(verbose=True)


def print_info(info: str):
    console.log("INFO:", info, style="bold blue")


def print_warning(info: str):
    console.log("WARNING:", info, style="orange3")


def print_error(error: str):
    console.log("ERROR:", error, style="bold red")


# console setting
console = Console()

# config setting
config = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36"
    },
    **os.environ,
}


# download setting
download_dir = os.getenv("DOWNLOAD_DIR")
Path(download_dir).mkdir(parents=True, exist_ok=True)

# logger setting
logdir = os.getenv("LOG_DIR")
if not Path(logdir).exists():
    print_info(f"logdir:{logdir} not exists, create it...")
    Path(logdir).mkdir(parents=True)
file_name = os.path.basename(__file__) + str(int(time.time())) + ".log"
file_handler = logging.FileHandler(
    filename=os.path.join(logdir, file_name), encoding="utf-8"
)
# set formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# set logger
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
