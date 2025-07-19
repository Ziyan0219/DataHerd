# DataHerd Dependencies Map

## Overview

This document provides a comprehensive map of all dependencies within the DataHerd project, showing how different components interact with each other and external services.

## Component Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                DataHerd System                                  │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐  │
│  │   Frontend      │    │   API Server    │    │    Core Processing          │  │
│  │   (React)       │◄──►│   (FastAPI)     │◄──►│                             │  │
│  │                 │    │                 │    │  ┌─────────────────────────┐ │  │
│  │ • Dashboard     │    │ • Data Routes   │    │  │   NLP Processor         │ │  │
│  │ • Data Cleaning │    │ • Rule Routes   │    │  │                         │ │  │
│  │ • Rule Mgmt     │    │ • Report Routes │    │  │ • OpenAI API            │ │  │
│  │ • Reports       │    │ • Health Routes │    │  │ • Pattern Matching      │ │  │
│  │ • Settings      │    │                 │    │  │ • Rule Generation       │ │  │
│  └─────────────────┘    └─────────────────┘    │  └─────────────────────────┘ │  │
│           │                       │             │                             │  │
│           │                       │             │  ┌─────────────────────────┐ │  │
│           │                       │             │  │   Data Processor        │ │  │
│           │                       │             │  │                         │ │  │
│           │                       │             │  │ • Preview Generation    │ │  │
│           │                       │             │  │ • Change Application    │ │  │
│           │                       │             │  │ • Rollback System       │ │  │
│           │                       │             │  │ • Quality Metrics       │ │  │
│           │                       │             │  └─────────────────────────┘ │  │
│           │                       │             │                             │  │
│           │                       │             │  ┌─────────────────────────┐ │  │
│           │                       │             │  │   Rule Manager          │ │  │
│           │                       │             │  │                         │ │  │
│           │                       │             │  │ • Rule Persistence      │ │  │
│           │                       │             │  │ • Template Management   │ │  │
│           │                       │             │  │ • Usage Analytics       │ │  │
│           │                       │             │  │ • Client Context        │ │  │
│           │                       │             │  └─────────────────────────┘ │  │
│           │                       │             │                             │  │
│           │                       │             │  ┌─────────────────────────┐ │  │
│           │                       │             │  │   Report Generator      │ │  │
│           │                       │             │  │                         │ │  │
│           │                       │             │  │ • Report Compilation    │ │  │
│           │                       │             │  │ • Visualization Gen     │ │  │
│           │                       │             │  │ • Export Functions      │ │  │
│           │                       │             │  │ • Template Rendering    │ │  │
│           │                       │             │  └─────────────────────────┘ │  │
│           │                       │             └─────────────────────────────┘  │
│           │                       │                           │                   │
│           │                       │                           │                   │
│           │                       └───────────────────────────┼───────────────────┤
│           │                                                   │                   │
│           │                                                   ▼                   │
│           │                               ┌─────────────────────────────────────┐ │
│           │                               │         Database Layer              │ │
│           │                               │                                     │ │
│           │                               │ • SQLite/MySQL Database            │ │
│           │                               │ • SQLAlchemy ORM                   │ │
│           │                               │ • Connection Pooling               │ │
│           │                               │ • Migration Scripts                │ │
│           │                               └─────────────────────────────────────┘ │
│           │                                                   │                   │
│           └───────────────────────────────────────────────────┼───────────────────┤
│                                                               │                   │
│                                                               ▼                   │
│                               ┌─────────────────────────────────────────────────┐ │
│                               │              External Services                  │ │
│                               │                                                 │ │
│                               │ • OpenAI API (GPT-4)                           │ │
│                               │ • File Storage System                          │ │
│                               │ • Email Services (planned)                     │ │
│                               │ • Cloud Storage (planned)                      │ │
│                               └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Detailed Component Dependencies

### 1. Frontend Dependencies (React Application)

#### Internal Dependencies
```
Frontend Components:
├── App.jsx
│   ├── Layout.jsx
│   ├── Dashboard.jsx
│   ├── DataCleaning.jsx
│   ├── RuleManagement.jsx
│   ├── Reports.jsx
│   └── Settings.jsx
│
├── UI Components (shadcn/ui)
│   ├── Button, Input, Card, Table
│   ├── Dialog, Alert, Badge
│   ├── DateRangePicker
│   └── Charts (Recharts)
│
└── Utilities
    ├── API Client
    ├── Theme Provider
    └── Utils Functions
```

#### External Dependencies
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.8.1",
  "tailwindcss": "^3.2.0",
  "@radix-ui/react-*": "^1.0.0",
  "recharts": "^2.5.0",
  "lucide-react": "^0.263.1",
  "clsx": "^1.2.1",
  "tailwind-merge": "^1.10.0"
}
```

#### API Dependencies
- **Backend API**: All frontend components depend on backend API endpoints
- **WebSocket**: Real-time updates (planned)
- **File Upload**: Direct file upload to backend

### 2. API Server Dependencies (FastAPI)

#### Internal Dependencies
```
API Server Structure:
├── api_router.py (Main router)
│   ├── Data Routes (/api/data/*)
│   ├── Rule Routes (/api/rules/*)
│   ├── Report Routes (/api/reports/*)
│   └── Health Routes (/api/health, /api/status)
│
├── Dependencies on Core Processing:
│   ├── dataherd.data_processor
│   ├── dataherd.nlp_processor
│   ├── dataherd.rule_manager
│   └── dataherd.report_generator
│
└── Database Dependencies:
    ├── db.models
    ├── db.base
    └── db.init_db
```

#### External Dependencies
```python
# requirements.txt (API Server)
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

#### Service Dependencies
- **Database**: SQLite/MySQL for data persistence
- **File System**: Local file storage for uploads
- **Core Processing Modules**: All dataherd.* modules

### 3. Core Processing Dependencies

#### 3.1 NLP Processor Dependencies

```python
# dataherd/nlp_processor.py
Dependencies:
├── External APIs:
│   └── OpenAI API (GPT-4)
│       ├── openai>=1.0.0
│       ├── OPENAI_API_KEY (environment)
│       └── OPENAI_API_BASE (environment)
│
├── Internal Dependencies:
│   ├── rule_manager.RuleManager
│   └── config.config (API keys, settings)
│
└── Python Libraries:
    ├── re (regex patterns)
    ├── json (data serialization)
    ├── logging (error tracking)
    └── typing (type hints)
```

**Dependency Flow**:
```
Natural Language Input → OpenAI API → Parsed Rule → Rule Manager → Database
                     ↓
              Fallback Pattern Matching (if API unavailable)
```

#### 3.2 Data Processor Dependencies

```python
# dataherd/data_processor.py
Dependencies:
├── Internal Dependencies:
│   ├── nlp_processor.NLPProcessor
│   ├── rule_manager.RuleManager
│   ├── db.models (CattleRecord)
│   └── db.base (database session)
│
├── External Libraries:
│   ├── pandas>=2.0.0 (data manipulation)
│   ├── numpy>=1.24.0 (numerical operations)
│   └── sqlalchemy>=2.0.0 (database ORM)
│
└── Python Standard Library:
    ├── uuid (unique identifiers)
    ├── datetime (timestamps)
    ├── json (data serialization)
    └── logging (operation tracking)
```

**Dependency Flow**:
```
Raw Data → Pandas DataFrame → Rule Application → Database Updates → Change Tracking
    ↓
Preview Generation → User Approval → Change Application → Rollback Capability
```

#### 3.3 Rule Manager Dependencies

```python
# dataherd/rule_manager.py
Dependencies:
├── Database Dependencies:
│   ├── db.models (Rules, RuleApplications, ClientTemplates)
│   ├── db.base (database session)
│   └── sqlalchemy (ORM operations)
│
├── Internal Dependencies:
│   └── config.config (database settings)
│
└── Python Libraries:
    ├── json (rule serialization)
    ├── datetime (timestamps)
    ├── uuid (unique identifiers)
    └── typing (type definitions)
```

**Dependency Flow**:
```
Rule Definition → Database Storage → Template Creation → Client Association
    ↓
Usage Tracking → Effectiveness Metrics → Rule Optimization
```

#### 3.4 Report Generator Dependencies

```python
# dataherd/report_generator.py
Dependencies:
├── Visualization Libraries:
│   ├── matplotlib>=3.7.0 (chart generation)
│   ├── seaborn>=0.12.0 (statistical plots)
│   └── pandas>=2.0.0 (data analysis)
│
├── Template Engine:
│   ├── jinja2>=3.1.0 (HTML templating)
│   └── base64 (image encoding)
│
├── Internal Dependencies:
│   ├── Database models (for data aggregation)
│   └── Processing results (from other modules)
│
└── Python Libraries:
    ├── json (data serialization)
    ├── datetime (timestamps)
    ├── pathlib (file operations)
    └── io.BytesIO (image handling)
```

**Dependency Flow**:
```
Processing Results → Data Aggregation → Visualization Generation → Template Rendering
    ↓
Report Compilation → Export Functions → User Delivery
```

### 4. Database Layer Dependencies

#### Database Models Dependencies
```python
# db/models.py
Dependencies:
├── SQLAlchemy Core:
│   ├── sqlalchemy.Column
│   ├── sqlalchemy.Integer, String, DateTime, Text, Boolean
│   ├── sqlalchemy.ForeignKey
│   └── sqlalchemy.relationship
│
├── Database Base:
│   └── db.base.Base (declarative base)
│
└── Python Libraries:
    ├── datetime (timestamp fields)
    └── uuid (unique identifiers)
```

#### Database Configuration Dependencies
```python
# db/base.py
Dependencies:
├── SQLAlchemy Engine:
│   ├── sqlalchemy.create_engine
│   ├── sqlalchemy.sessionmaker
│   └── sqlalchemy.declarative_base
│
├── Configuration:
│   ├── config.config (database URL)
│   └── Environment variables
│
└── Database Drivers:
    ├── sqlite3 (built-in, for SQLite)
    └── pymysql (for MySQL, optional)
```

### 5. Configuration Dependencies

#### Configuration System
```python
# config/config.py
Dependencies:
├── Environment Variables:
│   ├── DATABASE_URL
│   ├── OPENAI_API_KEY
│   ├── OPENAI_API_BASE
│   ├── LOG_LEVEL
│   └── CLIENT_CONTEXT
│
├── Python Libraries:
│   ├── os (environment access)
│   ├── pathlib (file paths)
│   └── logging (log configuration)
│
└── Default Values:
    ├── SQLite database path
    ├── Log file locations
    └── API endpoints
```

## External Service Dependencies

### 1. OpenAI API Integration

**Purpose**: Natural language processing for rule understanding
**Dependency Type**: Critical (with fallback)
**Configuration**:
```python
OPENAI_API_KEY = "your-api-key"
OPENAI_API_BASE = "https://api.openai.com/v1"
```

**Fallback Strategy**: Pattern-based parsing when API unavailable

### 2. Database Systems

**SQLite** (Development):
- **Purpose**: Local development and small deployments
- **Dependency Type**: Built-in (no external service)
- **Configuration**: Local file path

**MySQL** (Production):
- **Purpose**: Production deployments
- **Dependency Type**: External service
- **Configuration**: Connection string with host, port, credentials

### 3. File Storage

**Local File System**:
- **Purpose**: File uploads and temporary storage
- **Dependency Type**: Local resource
- **Configuration**: Upload directory path

**Cloud Storage** (Planned):
- **Purpose**: Scalable file storage
- **Dependency Type**: External service
- **Configuration**: Cloud provider credentials

## Dependency Installation Order

### 1. System Dependencies
```bash
# Python 3.11+
python3.11 -m pip install --upgrade pip

# Database drivers (if using MySQL)
pip install pymysql
```

### 2. Core Python Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt
```

### 3. Frontend Dependencies
```bash
# Navigate to frontend directory
cd dataherd-frontend

# Install Node.js dependencies
npm install --legacy-peer-deps
```

### 4. Database Setup
```bash
# Initialize database
python -m db.init_db

# Verify database connection
python -c "from db.base import engine; print('Database connected:', engine.url)"
```

### 5. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
# Set OPENAI_API_KEY, DATABASE_URL, etc.
```

## Runtime Dependencies

### Startup Sequence
1. **Configuration Loading**: Load environment variables and config
2. **Database Connection**: Establish database connection and verify schema
3. **Core Module Initialization**: Initialize processing modules
4. **API Server Startup**: Start FastAPI server
5. **Frontend Serving**: Serve React application (if integrated)

### Service Health Dependencies
```python
Health Check Dependencies:
├── Database Connection
├── OpenAI API Availability (optional)
├── File System Access
├── Memory Usage
└── CPU Usage
```

## Development vs Production Dependencies

### Development Environment
```
Dependencies:
├── SQLite (local database)
├── Local file storage
├── Development server (uvicorn)
├── Hot reload enabled
├── Debug logging
└── Test data fixtures
```

### Production Environment
```
Dependencies:
├── MySQL (production database)
├── Cloud storage integration
├── Production WSGI server
├── Load balancer
├── Monitoring services
├── Log aggregation
└── Backup systems
```

## Dependency Management Best Practices

### 1. Version Pinning
- Pin major versions for stability
- Allow minor version updates for security patches
- Test dependency updates in staging environment

### 2. Fallback Strategies
- **OpenAI API**: Pattern-based parsing fallback
- **Database**: Connection retry with exponential backoff
- **File Storage**: Local fallback for cloud storage failures

### 3. Health Monitoring
- Monitor external service availability
- Implement circuit breakers for failing services
- Provide graceful degradation when services unavailable

### 4. Security Considerations
- Secure API key storage
- Database connection encryption
- Input validation and sanitization
- Regular dependency security updates

This dependency map provides a complete understanding of how all components in the DataHerd system interact with each other and external services, enabling effective development, deployment, and maintenance of the system.

