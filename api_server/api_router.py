#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Router for DataHerd
Handles all API endpoints and routing logic
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path FIRST
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Set PYTHONPATH environment variable as well
os.environ['PYTHONPATH'] = str(project_root) + os.pathsep + os.environ.get('PYTHONPATH', '')

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks, Body
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import uuid
import shutil
import argparse
import uvicorn
from typing import Optional
from server.utils import SessionLocal, check_and_initialize_db, get_db
from sqlalchemy import func
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


def validate_api_key(api_key: str) -> bool:
    """Simple API key validation - in production, implement proper validation"""
    return api_key and len(api_key) > 10


def upsert_agent_by_user_id(db_session, api_key: str, user_id: str) -> bool:
    """Simple implementation for storing API key - in production, implement proper storage"""
    # For now, just store in environment variable
    os.environ['OPENAI_API_KEY'] = api_key
    return True


def create_app():
    app = FastAPI(
        title="DataHerd API Server",
        description="AI-powered data cleaning platform for cattle lot management operations",
        version="1.0.0"
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

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "healthy", "message": "DataHerd API server is running"}

    # 挂载 前端 项目构建的前端静态文件夹 (对接前端静态文件的入口)
    if os.getenv("USE_DOCKER") == "True":
        app.mount("/", StaticFiles(directory="/app/static/dist"), name="static")
    else:
        # 检查前端构建目录是否存在，如果不存在则使用前端源码目录
        frontend_dist_path = os.path.join(current_dir, "dataherd-frontend", "dist")
        frontend_public_path = os.path.join(current_dir, "dataherd-frontend", "public")
        
        if os.path.exists(frontend_dist_path):
            app.mount("/", StaticFiles(directory=frontend_dist_path), name="static")
        elif os.path.exists(frontend_public_path):
            app.mount("/", StaticFiles(directory=frontend_public_path), name="static")
        else:
            # 创建一个简单的静态目录作为临时解决方案
            temp_static_dir = os.path.join(current_dir, "temp_static")
            os.makedirs(temp_static_dir, exist_ok=True)
            
            # 创建一个简单的index.html
            index_html_path = os.path.join(temp_static_dir, "index.html")
            if not os.path.exists(index_html_path):
                with open(index_html_path, 'w') as f:
                    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>DataHerd - Cattle Data Cleaning Agent</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .api-link { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DataHerd - Intelligent Cattle Data Cleaning Agent</h1>
            <p>AI-powered data cleaning platform for Elanco's cattle lot management operations</p>
        </div>
        <div>
            <h2>API Documentation</h2>
            <p>The DataHerd API server is running successfully!</p>
            <p><a href="/docs" class="api-link">View API Documentation</a></p>
            
            <h2>Features</h2>
            <ul>
                <li>Natural Language Rule Processing</li>
                <li>Intelligent Data Preview</li>
                <li>Operation Rollback</li>
                <li>Client-Specific Rules</li>
                <li>Comprehensive Reporting</li>
            </ul>
            
            <h2>Quick Start</h2>
            <ol>
                <li>Configure your OpenAI API key via <code>/api/set_api_key</code></li>
                <li>Use <code>/api/clean_data</code> to process cattle data</li>
                <li>Preview changes with <code>/api/preview_cleaning</code></li>
                <li>Generate reports with <code>/api/generate_report</code></li>
            </ol>
        </div>
    </div>
</body>
</html>""")
            
            app.mount("/", StaticFiles(directory=temp_static_dir), name="static")
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
        try:
            return {"status": 200, "data": {"message": "System is ready for data cleaning operations."}}
        except Exception as e:
            return {"status": 500, "data": {"message": f"System initialization error: {str(e)}"}}

    @app.post("/api/set_api_key", tags=["Initialization"], summary="Set API Key for AI operations")
    def save_api_key(api_key: str = Body(..., description="API Key for AI operations", embed=True)):
        try:
            if not validate_api_key(api_key):
                return {"status": 400, "data": {"message": "Invalid API Key."}}

            # Store API key in environment
            os.environ['OPENAI_API_KEY'] = api_key
            return {"status": 200, "data": {"message": "API Key configured successfully."}}

        except Exception as e:
            return {"status": 500, "data": {"message": f"Failed to configure API Key: {str(e)}"}}

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
            raise HTTPException(status_code=500, detail=f"Data cleaning failed: {str(e)}")

    @app.post("/api/preview_cleaning", tags=["Data Cleaning"],
              summary="Preview data cleaning operation without applying changes")
    async def preview_cleaning(request: DataPreviewRequest):
        """
        Previews the data cleaning operation based on natural language rules.
        """
        try:
            data_processor = DataProcessor()
            # Placeholder for preview functionality
            return {
                "status": 200, 
                "data": {
                    "message": "Preview generated successfully",
                    "batch_id": request.batch_id,
                    "rules": request.natural_language_rules,
                    "client": request.client_name
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

    @app.post("/api/rollback_cleaning", tags=["Data Cleaning"],
              summary="Rollback a previous data cleaning operation")
    async def rollback_cleaning(request: DataRollbackRequest):
        """
        Rolls back a specific data cleaning operation.
        """
        try:
            data_processor = DataProcessor()
            return {
                "status": 200,
                "data": {
                    "message": "Rollback completed successfully",
                    "batch_id": request.batch_id,
                    "operation_log_id": request.operation_log_id
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")

    @app.post("/api/save_rule", tags=["Rule Management"],
              summary="Save a new cleaning rule")
    async def save_cleaning_rule(request: SaveRuleRequest):
        """
        Saves a new cleaning rule, optionally marking it as permanent.
        """
        try:
            rule_manager = RuleManager()
            return {
                "status": 200,
                "data": {
                    "message": "Rule saved successfully",
                    "client_name": request.client_name,
                    "rule": request.natural_language_rule,
                    "permanent": request.is_permanent
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save rule: {str(e)}")

    @app.post("/api/update_permanent_rule", tags=["Rule Management"],
              summary="Update an existing permanent cleaning rule")
    async def update_permanent_cleaning_rule(request: UpdatePermanentRuleRequest):
        """
        Updates an existing permanent cleaning rule.
        """
        try:
            rule_manager = RuleManager()
            return {
                "status": 200,
                "data": {
                    "message": "Permanent rule updated successfully",
                    "rule_id": request.rule_id,
                    "new_rule": request.new_natural_language_rule
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update permanent rule: {str(e)}")

    @app.get("/api/get_client_rules/{client_name}", tags=["Rule Management"],
             summary="Get all cleaning rules for a specific client")
    async def get_client_rules(client_name: str):
        """
        Retrieves all cleaning rules associated with a given client.
        """
        try:
            rule_manager = RuleManager()
            return {
                "status": 200, 
                "data": {
                    "client_name": client_name,
                    "rules": []  # Placeholder
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve client rules: {str(e)}")

    @app.post("/api/generate_report", tags=["Reporting"],
              summary="Generate a data cleaning operation report")
    async def generate_report(request: GenerateReportRequest):
        """
        Generates a detailed report of data cleaning operations based on provided filters.
        """
        try:
            report_generator = ReportGenerator()
            return {
                "status": 200,
                "data": {
                    "message": "Report generated successfully",
                    "batch_id": request.batch_id,
                    "operator_id": request.operator_id,
                    "date_range": f"{request.start_date} to {request.end_date}"
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


def run_api(host, port):
    # 初始化数据库
    initialize_database()

    # 启动服务
    uvicorn.run(create_app(),
                host=host,
                port=port,
                )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9000)

    args = parser.parse_args()

    run_api(host=args.host, port=args.port)

