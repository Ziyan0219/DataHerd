import logging
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 获取项目的根目录路径
base_path = os.path.dirname(os.path.abspath(__file__))


def setup_logging():
    """
    格式化服务实时日志信息
    :return:
    """
    # 创建一个logger
    logger = logging.getLogger()

    # 设置日志级别为INFO
    logger.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 创建一个handler，用于写入日志文件
    log_file_path = os.path.join(base_path, 'dataherd_runtime.log')
    file_handler = logging.FileHandler(log_file_path)  # 使用完整路径指定日志文件名
    file_handler.setFormatter(formatter)  # 设置日志格式

    # 创建一个handler，用于将日志输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# Database configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dataherd.db")

# For backward compatibility, support MySQL configuration
username = os.getenv("DB_USERNAME", "root")
database_name = os.getenv("DB_NAME", "DataHerd")
password = os.getenv("DB_PASSWORD", "Xzy580021*")

# 检查环境变量USE_DOCKER，若不存在或为False，则使用相对路径挂载静态文件
if os.getenv("USE_DOCKER") == "True":
    hostname = 'db'  # Docker环境
else:
    hostname = os.getenv("DB_HOST", "localhost")  # 个人环境开发配置

# Use DATABASE_URL if provided, otherwise construct MySQL URL
if DATABASE_URL.startswith("sqlite"):
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}?charset=utf8mb4"

assistant_instructions = """
You are DataHerd, an intelligent cattle data cleaning agent designed to streamline and automate data quality processes for Elanco.
You possess the following key capabilities:
1. Natural Language Rule Understanding: You can interpret and apply data cleaning rules described in plain English, allowing for flexible and intuitive rule definition.
2. Contextual Rule Application: You can adjust cleaning rules based on specific client names (e.g., Elanco) or other batch-specific criteria, ensuring tailored data quality.
3. Data Preview and Rollback: You can provide a preview of the data changes before they are applied, and you support rolling back operations if unintended changes occur.
4. Rule Memory and Persistence: You can remember cleaning rules applied to specific client batches, and users can request to permanently save or modify these rules for future use.
5. Comprehensive Reporting: You can generate detailed reports of all data cleaning operations, providing transparency and an audit trail.

In essence, you are a powerful, flexible, and user-friendly intelligent agent focused on enhancing data quality for cattle lot management.
Please maintain a helpful, supportive, and patient demeanor in your responses.
"""


if __name__ == '__main__':
    # 创建数据库连接字符串（不包含数据库名）
    SQLALCHEMY_DATABASE_URI_TEST = f"mysql+pymysql://{username}:{password}@{hostname}/"
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URI_TEST)

        # 尝试连接到数据库
        with engine.connect() as connection:
            print("数据库连接成功 !")

    except OperationalError as e:
        # 捕获数据库连接错误
        print(f"连接数据库出错: {e}")
    except Exception as e:
        # 捕获其他类型的错误
        print(f"发生意外错误: {e}")