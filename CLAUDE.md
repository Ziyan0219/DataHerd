# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataHerd is an AI-powered cattle data cleaning platform with natural language rule processing. It consists of a FastAPI backend and a React frontend, designed for cattle lot management operations with intelligent data validation and comprehensive reporting.

## Development Commands

### Backend Development
```bash
# Start the full application (backend + frontend)
python start.py

# Development mode with auto-reload
python start.py --reload --log-level DEBUG

# Custom host/port configuration
python start.py --host 127.0.0.1 --port 8000

# Skip frontend build (backend only)
python start.py --skip-frontend

# Skip database initialization
python start.py --skip-db-init
```

### Frontend Development
```bash
cd dataherd-frontend

# Install dependencies
pnpm install

# Development server
pnpm run dev

# Build for production
pnpm run build

# Lint code
pnpm run lint

# Preview built application
pnpm run preview
```

### Testing
```bash
# Run backend tests
python -m pytest tests/

# Run core functionality tests
python test_core_functionality.py

# Simple test script
python simple_test.py

# Frontend tests (if available)
cd dataherd-frontend && pnpm test
```

### Database Operations
```bash
# Initialize database
python -m db.init_db

# Reset database (from scratch)
rm dataherd.db && python -m db.init_db
```

### Installation
```bash
# Automated installation
./install.sh

# Quick start (creates venv and starts server)
./start.sh

# Manual installation
python3 -m venv dataherd_env
source dataherd_env/bin/activate  # Windows: dataherd_env\Scripts\activate
pip install -r requirements.txt
```

## Architecture Overview

### Backend Structure (`/`)
- **`start.py`** - Main application entry point with environment setup
- **`api_server/`** - FastAPI application and routing
  - `api_router.py` - Main API routes and endpoint definitions
  - `db_interface.py` - Database interface layer
  - `python_interface.py` - Python integration utilities
  - `utils.py` - API utility functions
- **`dataherd/`** - Core business logic modules
  - `data_processor.py` - Data cleaning and processing engine
  - `nlp_processor.py` - Natural language rule parsing with OpenAI integration
  - `rule_manager.py` - Rule persistence and management
  - `report_generator.py` - Comprehensive reporting system
- **`db/`** - Database layer
  - `models.py` - SQLAlchemy ORM models
  - `init_db.py` - Database initialization
  - `base.py` - Database session management
  - `schemas.py` - Pydantic schemas for data validation
- **`config/`** - Configuration management
  - `config.py` - Application configuration

### Frontend Structure (`/dataherd-frontend/`)
- **`src/`** - React application source
  - `pages/` - Main application pages
    - `Dashboard.jsx` - System overview and metrics
    - `DataCleaning.jsx` - Data upload and cleaning interface
    - `Reports.jsx` - Report generation and viewing
    - `RuleManagement.jsx` - Rule creation and management
    - `Settings.jsx` - Application settings
  - `components/` - Reusable components
    - `Layout.jsx` - Main application layout
    - `ui/` - Shadcn/ui component library
  - `hooks/` - Custom React hooks
  - `lib/` - Utility functions
- **Technology Stack**: React 19, Tailwind CSS, Shadcn/ui, Recharts, React Router

### Key Integrations
- **OpenAI API** - Natural language rule processing
- **SQLAlchemy** - Database ORM with SQLite/MySQL support
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server for production deployment

## Environment Configuration

Required environment variables (create `.env` file):
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
DATABASE_URL=sqlite:///./dataherd.db
OPENAI_API_BASE=https://api.openai.com/v1
USE_DOCKER=False
DEBUG=True
```

## Core Features Implementation

### Natural Language Rule Processing
- Uses OpenAI GPT-4 for advanced rule understanding
- Fallback pattern-based parsing for offline operation
- Context-aware processing for client-specific requirements
- Located in `dataherd/nlp_processor.py`

### Data Processing Pipeline
1. **Data Loading** - CSV/Excel file upload and parsing
2. **Rule Application** - Natural language rules converted to executable operations
3. **Preview System** - Non-destructive change preview with confidence scoring
4. **Change Application** - User-approved changes with rollback capability
5. **Report Generation** - Comprehensive analysis and audit trails

### Database Schema
- **CattleRecord** - Main cattle data (lot_id, weight, breed, birth_date, health_status)
- **BatchInfo** - Processing batch metadata
- **OperationLog** - Complete audit trail of all operations
- **Rules** - Stored rule definitions with metadata and analytics

## Development Workflow

1. **Environment Setup**: Use `./install.sh` or manual setup with virtual environment
2. **Database**: Initialize with `python -m db.init_db`
3. **Development**: Run `python start.py --reload` for backend + frontend
4. **Testing**: Use `python test_core_functionality.py` for integration tests
5. **Frontend Only**: Use `cd dataherd-frontend && pnpm run dev` for frontend development

## Key Architectural Patterns

- **Separation of Concerns** - Clear separation between data processing, API, and UI layers
- **Preview-Apply Pattern** - All data changes use preview-before-apply workflow
- **Rule Engine** - Flexible rule system with natural language input
- **Client Context** - Client-specific rule templates and processing contexts
- **Comprehensive Logging** - Full audit trail for compliance and debugging

## Production Deployment

- **Server**: Uvicorn ASGI server with configurable host/port
- **Database**: Supports SQLite (development) and MySQL (production)  
- **Frontend**: Vite-built static assets served by FastAPI
- **API Docs**: Available at `/docs` endpoint (Swagger UI)
- **Health Check**: Available at `/health` endpoint

## Common Development Tasks

- **Add new API endpoint**: Edit `api_server/api_router.py`
- **Modify data processing**: Edit `dataherd/data_processor.py`
- **Add frontend page**: Create in `dataherd-frontend/src/pages/`
- **Database changes**: Modify `db/models.py` and reinitialize database
- **Add new rule type**: Extend `dataherd/nlp_processor.py` and `dataherd/rule_manager.py`