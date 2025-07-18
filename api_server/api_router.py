#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException, Body
import uvicorn
import json
import argparse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from pydantic import BaseModel
from fastapi import Query
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, File, UploadFile, Form
from typing import List, Optional
import shutil
from server.utils import (SessionLocal,
                          check_and_initialize_db,
                          upsert_agent_by_user_id,
                          )
from server.identity_verification.utils import validate_api_key
from sse_starlette.sse import EventSourceResponse
from db.base_model import (
                           DbBase,
                           MessageModel,
                           ThreadModel,
                           )
from sqlalchemy import func
import os
from dotenv import load_dotenv, find_dotenv
from db.init_db import initialize_database
from dataherd.data_processor import DataProcessor
from dataherd.rule_manager import RuleManager
from dataherd.report_generator import ReportGenerator

load_dotenv(find_dotenv())

# 获取当前文件所在目录的上一级目录
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')

# 创建上传文件夹（如果不存在）
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class ChatRequest(BaseModel):
    question: str = Body("", embed=True)
    chat_stream: bool = Body(False, embed=True)


class DataCleaningRequest(BaseModel):
    batch_id: str = Body(..., description="Batch ID for the cattle data")
    cleaning_rules: str = Body(..., description="Natural language cleaning rules")
    apply_permanently: bool = Body(False, description="Whether to apply rules permanently")


class DataPreviewRequest(BaseModel):
    batch_id: str = Body(..., description="Batch ID for the cattle data")
    natural_language_rules: str = Body(..., description="Natural language cleaning rules to preview")
    client_name: str = Body(None, description="Client name for specific rule adjustments")


class DataRollbackRequest(BaseModel):
    batch_id: str = Body(..., description="Batch ID for the cattle data")
    operation_log_id: str = Body(..., description="ID of the operation log to rollback")


class SaveRuleRequest(BaseModel):
    client_name: str = Body(..., description="Client name associated with the rule")
    natural_language_rule: str = Body(..., description="Natural language description of the rule")
    is_permanent: bool = Body(False, description="Whether this rule should be permanently saved")


class UpdatePermanentRuleRequest(BaseModel):
    rule_id: str = Body(..., description="ID of the permanent rule to update")
    new_natural_language_rule: str = Body(..., description="New natural language description for the rule")


class GenerateReportRequest(BaseModel):
    batch_id: Optional[str] = Body(None, description="Optional Batch ID to filter report")
    operator_id: Optional[str] = Body(None, description="Optional Operator ID to filter report")
    start_date: Optional[str] = Body(None, description="Optional start date (YYYY-MM-DD) to filter report")
    end_date: Optional[str] = Body(None, description="Optional end date (YYYY-MM-DD) to filter report")


class CodeExecutionRequest(BaseModel):
    python_code: str
    thread_id: str


class SQLExecutionRequest(BaseModel):
    thread_id: str
    db_info_id: str
    sql_query: str


def create_app():
    app = FastAPI(
        title="DataHerd API Server",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载路由
    mount_app_routes(app)

    # 重定向到 index.html
    @app.get("/", include_in_schema=False)
    def read_root():
        return RedirectResponse(url='/index.html')

    # 挂载 前端 项目构建的前端静态文件夹 (对接前端静态文件的入口)
    if os.getenv("USE_DOCKER") == "True":
        app.mount("/", StaticFiles(directory="/app/static/dist"), name="static")
    else:
        app.mount("/", StaticFiles(directory="../static/dist"), name="static")
    return app


def mount_app_routes(app: FastAPI):
    """
    DataHerd API Routes for Cattle Data Cleaning
    """

    @app.get("/api/check_initialization", tags=["Initialization"],
             summary="Check if the system is initialized")
    def check_database_initialization():
        """
        Check if the database is initialized.
        """
        db_session = SessionLocal()
        try:
            if check_and_initialize_db(db_session, "dataherd_user") == '':
                return {"status": 400,
                        "data": {"message": "System needs initialization. Please set up API key."}}

            return {"status": 200, "data": {"message": "System is ready for data cleaning operations."}}
        except Exception:
            db_session.rollback()
            raise
        finally:
            db_session.close()

    @app.post("/api/set_api_key", tags=["Initialization"], summary="Set API Key for AI operations")
    def save_api_key(api_key: str = Body(..., description="API Key for AI operations", embed=True),
                     ):
        db_session = SessionLocal()
        try:
            if not validate_api_key(api_key):
                return {"status": 400, "data": {"message": "Invalid API Key."}}

            if upsert_agent_by_user_id(db_session, api_key, user_id='dataherd_user'):
                return {"status": 200, "data": {"message": "API Key configured successfully."}}

            return {"status": 500, "data": {"message": "Failed to configure API Key."}}

        except Exception:
            raise HTTPException(status_code=500, detail="Internal server error.")
        finally:
            db_session.close()

    @app.post("/api/clean_data", tags=["Data Cleaning"],
              summary="Clean cattle data based on natural language rules")
    async def clean_data(request: DataCleaningRequest):
        """
        Main data cleaning endpoint that processes cattle data based on natural language rules.
        """
        try:
            data_processor = DataProcessor()
            # In a real scenario, you would load data, apply rules, and save results
            # For now, this is a placeholder for the actual cleaning logic.
            # If apply_permanently is True, save the cleaned data to the database.
            # Otherwise, it's a preview or temporary application.
            return {
                "status": 200,
                "data": {
                    "message": "Data cleaning rules processed successfully",
                    "batch_id": request.batch_id,
                    "rules_applied": request.cleaning_rules,
                    "permanent": request.apply_permanently
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail="Data cleaning failed.")

    @app.post("/api/preview_cleaning", tags=["Data Cleaning"],
              summary="Preview data cleaning operation without applying changes")
    async def preview_cleaning(request: DataPreviewRequest):
        """
        Previews the data cleaning operation based on natural language rules.
        """
        try:
            data_processor = DataProcessor()
            preview_results = data_processor.preview_cleaning_operation(
                request.batch_id, request.natural_language_rules, request.client_name
            )
            return {"status": 200, "data": preview_results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Preview failed: {e}")

    @app.post("/api/rollback_cleaning", tags=["Data Cleaning"],
              summary="Rollback a previous data cleaning operation")
    async def rollback_cleaning(request: DataRollbackRequest):
        """
        Rolls back a specific data cleaning operation.
        """
        try:
            data_processor = DataProcessor()
            rollback_status = data_processor.rollback_operation(
                request.batch_id, request.operation_log_id
            )
            return {"status": 200, "data": rollback_status}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Rollback failed: {e}")

    @app.post("/api/save_rule", tags=["Rule Management"],
              summary="Save a new cleaning rule")
    async def save_cleaning_rule(request: SaveRuleRequest):
        """
        Saves a new cleaning rule, optionally marking it as permanent.
        """
        try:
            rule_manager = RuleManager()
            result = rule_manager.save_rule(
                request.client_name, request.natural_language_rule, request.is_permanent
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save rule: {e}")

    @app.post("/api/update_permanent_rule", tags=["Rule Management"],
              summary="Update an existing permanent cleaning rule")
    async def update_permanent_cleaning_rule(request: UpdatePermanentRuleRequest):
        """
        Updates an existing permanent cleaning rule.
        """
        try:
            rule_manager = RuleManager()
            result = rule_manager.update_permanent_rule(
                request.rule_id, request.new_natural_language_rule
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update permanent rule: {e}")

    @app.get("/api/get_client_rules/{client_name}", tags=["Rule Management"],
             summary="Get all cleaning rules for a specific client")
    async def get_client_rules(client_name: str):
        """
        Retrieves all cleaning rules associated with a given client.
        """
        try:
            rule_manager = RuleManager()
            rules = rule_manager.get_rules_for_client(client_name)
            return {"status": 200, "data": rules}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve client rules: {e}")

    @app.post("/api/generate_report", tags=["Reporting"],
              summary="Generate a data cleaning operation report")
    async def generate_report(request: GenerateReportRequest):
        """
        Generates a detailed report of data cleaning operations based on provided filters.
        """
        try:
            report_generator = ReportGenerator()
            report_data = report_generator.generate_operation_report(
                batch_id=request.batch_id,
                operator_id=request.operator_id,
                start_date=request.start_date,
                end_date=request.end_date
            )
            return {"status": 200, "data": report_data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate report: {e}")

    @app.get("/api/conversation", tags=["Chat"], summary="Get all chat sessions")
    def get_conversation():
        from server.utils import SessionLocal
        from db.base_model import ThreadModel, SecretModel
        db_session = SessionLocal()
        try:
            user_id = "dataherd_user"
            agent = db_session.query(SecretModel).filter(SecretModel.user_id == user_id).first()
            if agent:
                assis_id = agent.assis_id
                results = db_session.query(ThreadModel.id, ThreadModel.conversation_name) \
                    .filter(ThreadModel.agent_id == assis_id, ThreadModel.conversation_name != "new_chat") \
                    .order_by(ThreadModel.updated_at.desc()).all()
                data = [{"id": result.id, "conversation_name": result.conversation_name} for result in results]
                return {"status": 200, "data": {"message": data}}
        except Exception:
            raise HTTPException(status_code=500, detail="Internal server error.")
        finally:
            db_session.close()

    from db_interface import DBConfig, insert_db_config, update_db_config, get_all_databases, \
        delete_db_config

    @app.post("/api/create_db_connection", tags=["Database"],
              summary="Create database connection for cattle data")
    def db_create(db_config: DBConfig = Body(...)):
        try:
            database_id = insert_db_config(db_config)
            return {"status": 200, "data": {"message": "Database connection established",
                                            "db_info_id": database_id}}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to create database connection.")

    @app.get("/api/show_all_databases", tags=["Database"], summary="Get all database connections")
    def list_databases():
        try:
            databases = get_all_databases()
            return {"status": 200, "data": databases}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to retrieve databases.")

    @app.delete("/api/delete_db_connection/{db_info_id}", tags=["Database"], summary="Delete database connection")
    def delete_db_connection(db_info_id: str):
        try:
            success = delete_db_config(db_info_id)
            if not success:
                raise HTTPException(status_code=404, detail="Database configuration not found")
            return {"status": 200, "data": {"message": "Database configuration deleted successfully"}}
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error.")


def run_api(host, port):
    # 初始化数据库
    initialize_database()

    # 启动服务
    uvicorn.run(app,
                host=host,
                port=port,
                )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9000)

    args = parser.parse_args()

    app = create_app()

    run_api(host=args.host,
            port=args.port,
            )
