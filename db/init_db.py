# -*- coding: utf-8 -*-
"""
DataHerd Database Initialization

This module handles the initialization of the DataHerd database.
"""

from sqlalchemy import create_engine, text
from config.config import username, password, hostname, database_name, SQLALCHEMY_DATABASE_URI
from db.base import Base, engine, SessionLocal
from db.models import CattleRecord, CleaningRule, OperationLog, BatchInfo, LotInfo


# 检查数据库是否存在，并在需要时创建数据库（仅适用于 MySQL）
def create_database_if_not_exists(username: str, password: str, hostname: str, database_name: str):
    # 只有在使用 MySQL 时才需要预先创建数据库
    if not SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
        # 创建一个连接到数据库的引擎（没有指定数据库名）
        engine_for_check = create_engine(f"mysql+pymysql://{username}:{password}@{hostname}?charset=utf8mb4")

        with engine_for_check.connect() as connection:
            # 执行 SQL 查询，检查数据库是否存在
            result = connection.execute(text(f"SHOW DATABASES LIKE '{database_name}'"))
            if result.fetchone() is None:
                # 数据库不存在，执行创建数据库
                connection.execute(
                    text(f"CREATE DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                print(f"Database '{database_name}' created successfully.")
            else:
                print(f"Database '{database_name}' already exists.")
    else:
        print("Using SQLite database - no pre-creation needed.")


# 定义数据库模型初始化函数
def initialize_database():
    try:
        # 检查数据库是否存在，如果不存在，先继续进行创建（仅适用于 MySQL）
        create_database_if_not_exists(username, password, hostname, database_name)

        # 创建所有表
        Base.metadata.create_all(engine)
        print("DataHerd database tables created successfully.")
        return True

    except Exception as e:
        print("Error occurred during database initialization:", e)
        return False


def delete_database():
    # 删除所有表
    Base.metadata.drop_all(engine)
    return True


if __name__ == '__main__':
    initialize_database()
    # delete_database()