import logging

# 第一种方式是使用logging提供的模块级别的函数
# 第二种方式是使用Logging日志系统的四大组件

if __name__ == "__main__":
    # LOG_FORMAT = (
    #     "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "  # 配置输出日志格式
    # )
    # DATE_FORMAT = "%Y-%m-%d  %H:%M:%S %a "  # 配置输出时间的格式，注意月份和天数不要搞乱了
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format=LOG_FORMAT,
    #     datefmt=DATE_FORMAT,
    #     filename=r"d:\test\test.log",  # 有了filename参数就不会直接输出显示到控制台，而是直接写入文件
    # )
    # logging.debug("msg1")
    # logging.info("msg2")
    # logging.warning("msg3")
    # logging.error("msg4")
    # logging.critical("msg5")
    logger = logging.getLogger(__name__)
    # filehandler
    file_handler = logging.FileHandler(filename="test.log", encoding="utf-8")
    # file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    logger.info("test")
    logger.debug("fasf")
    # streamhandler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.debug("fasf")
