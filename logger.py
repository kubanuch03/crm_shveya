import logging
import colorlog

LOG_FORMAT = "%(log_color)s[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Создаем обработчик логов (вывод в консоль)
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# Создаем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)