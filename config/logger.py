import sys
from pathlib import Path
from loguru import logger

# Đường dẫn thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "webgenbench.log"

# Xóa cấu hình mặc định của loguru
logger.remove()

# Handler hiển thị console có màu sắc
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

# Handler ghi log ra file với mã hóa UTF-8 hỗ trợ tiếng Việt
logger.add(
    str(LOG_FILE),
    rotation="10 MB",
    retention="14 days",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
)

__all__ = ["logger", "LOG_FILE"]

