# DataHerd Component Guide

This document provides a comprehensive overview of each functional component in DataHerd and how they contribute to the system's core capabilities.

## 🏗️ System Architecture

DataHerd follows a modular architecture with clear separation of concerns:

```
DataHerd/
├── api_server/          # FastAPI backend server
├── dataherd/           # Core business logic modules
├── db/                 # Database models and utilities
├── config/             # Configuration management
├── dataherd-frontend/  # React frontend application
└── static/             # Built frontend assets
```

## 🔧 Core Components

### 1. API Server (`api_server/api_router.py`)

**Purpose**: Central HTTP API server that handles all client requests and coordinates between frontend and backend services.

**Key Capabilities**:
- RESTful API endpoints for all DataHerd operations
- Request validation and error handling
- CORS configuration for frontend integration
- Static file serving for the web interface

**Core Endpoints**:
- `/api/clean_data` - Main data cleaning operations
- `/api/preview_cleaning` - Data change previews
- `/api/rollback_cleaning` - Operation rollbacks
- `/api/save_rule` - Rule management
- `/api/generate_report` - Report generation

**Contribution to DataHerd's Capabilities**:
- Provides the primary interface for all system interactions
- Ensures secure and validated data processing
- Enables real-time communication between frontend and backend

### 2. Rule Engine (`dataherd/rule_engine.py`)

**Purpose**: Converts natural language cleaning rules into executable data processing logic.

**Key Capabilities**:
- Natural language processing for rule interpretation
- Dynamic rule compilation and execution
- Context-aware rule application based on client preferences
- Rule validation and error handling

**Core Functions**:
- `parse_natural_language_rule()` - Converts text to structured rules
- `apply_rules_to_data()` - Executes rules on dataset
- `validate_rule_syntax()` - Ensures rule correctness

**Contribution to DataHerd's Capabilities**:
- Enables flexible, human-readable rule definition
- Provides the core intelligence for data cleaning operations
- Allows non-technical users to define complex cleaning logic

### 3. LLM Integration (`dataherd/llm_integration.py`)

**Purpose**: Manages communication with OpenAI's language models for intelligent rule processing.

**Key Capabilities**:
- Secure API key management
- Optimized prompt engineering for rule interpretation
- Response parsing and validation
- Error handling for API failures

**Core Functions**:
- `process_natural_language()` - Main LLM interaction
- `generate_rule_suggestions()` - AI-powered rule recommendations
- `validate_api_connection()` - Connection testing

**Contribution to DataHerd's Capabilities**:
- Provides the AI intelligence behind natural language processing
- Enables sophisticated rule interpretation and suggestion
- Allows the system to understand complex, context-dependent instructions

### 4. Data Processor (`dataherd/data_processor.py`)

**Purpose**: Handles all data manipulation operations including cleaning, preview, and rollback functionality.

**Key Capabilities**:
- Data loading and validation
- Preview generation without data modification
- Safe data cleaning with backup creation
- Operation rollback with state restoration

**Core Functions**:
- `preview_cleaning_operation()` - Generate change previews
- `apply_cleaning_rules()` - Execute data cleaning
- `rollback_operation()` - Restore previous state
- `backup_data_state()` - Create operation snapshots

**Contribution to DataHerd's Capabilities**:
- Provides safe, reversible data operations
- Enables users to preview changes before applying them
- Maintains data integrity through comprehensive backup systems

### 5. Rule Manager (`dataherd/rule_manager.py`)

**Purpose**: Manages the lifecycle of cleaning rules including storage, retrieval, and client-specific customization.

**Key Capabilities**:
- Rule persistence and retrieval
- Client-specific rule management
- Permanent rule updates
- Rule versioning and history

**Core Functions**:
- `save_rule()` - Store new cleaning rules
- `get_rules_for_client()` - Retrieve client-specific rules
- `update_permanent_rule()` - Modify base system rules
- `get_rule_history()` - Track rule changes over time

**Contribution to DataHerd's Capabilities**:
- Enables automatic rule memory for repeat clients
- Allows permanent system improvements based on user feedback
- Provides rule traceability and audit capabilities

### 6. Report Generator (`dataherd/report_generator.py`)

**Purpose**: Creates comprehensive reports of all data cleaning operations for audit and analysis purposes.

**Key Capabilities**:
- Detailed operation logging
- Flexible report filtering and generation
- Multiple output formats
- Statistical analysis of cleaning operations

**Core Functions**:
- `generate_operation_report()` - Create detailed reports
- `filter_operations()` - Apply report filters
- `calculate_statistics()` - Generate operation metrics

**Contribution to DataHerd's Capabilities**:
- Provides transparency and accountability for all operations
- Enables performance analysis and optimization
- Supports compliance and audit requirements

## 🗄️ Database Components

### 1. Database Schemas (`db/schemas.py`)

**Purpose**: Defines the data models for all system entities.

**Key Models**:
- `BatchInfo` - Cattle batch information
- `CleaningRule` - Stored cleaning rules
- `OperationLog` - Operation history and audit trail
- `ClientPreference` - Client-specific settings

**Contribution to DataHerd's Capabilities**:
- Provides structured data storage for all system entities
- Ensures data consistency and integrity
- Enables complex queries and reporting

### 2. Base Model (`db/base_model.py`)

**Purpose**: Provides common database functionality and utilities.

**Key Features**:
- Database connection management
- Common model behaviors
- Transaction handling
- Migration support

**Contribution to DataHerd's Capabilities**:
- Ensures reliable database operations
- Provides consistent data access patterns
- Supports system scalability and maintenance

## 🎨 Frontend Components

### 1. Main Application (`dataherd-frontend/src/App.jsx`)

**Purpose**: Primary user interface for all DataHerd operations.

**Key Features**:
- Tabbed interface for different operations
- Real-time operation feedback
- Responsive design for multiple devices
- Integrated help and guidance

**Core Sections**:
- **Clean Data Tab**: Rule input and execution
- **Preview Tab**: Change visualization
- **History Tab**: Operation history and rollback
- **Reports Tab**: Report generation and viewing

**Contribution to DataHerd's Capabilities**:
- Provides intuitive access to all system features
- Enables real-time interaction with data cleaning operations
- Offers comprehensive visibility into system state and history

## 🔄 Component Interactions

### Data Cleaning Workflow

1. **User Input** → Frontend captures rule description and batch information
2. **API Request** → Frontend sends request to API server
3. **Rule Processing** → Rule engine processes natural language via LLM integration
4. **Data Processing** → Data processor applies rules or generates preview
5. **Result Display** → Frontend displays results to user
6. **Logging** → Operation log records all activities
7. **Rule Storage** → Rule manager stores successful rules for future use

### Preview and Rollback Workflow

1. **Preview Request** → User requests change preview
2. **Safe Processing** → Data processor generates preview without modifying data
3. **Result Display** → Frontend shows proposed changes
4. **User Decision** → User chooses to apply or modify rules
5. **Rollback Option** → If needed, data processor restores previous state

### Reporting Workflow

1. **Report Request** → User specifies report parameters
2. **Data Aggregation** → Report generator queries operation logs
3. **Analysis** → Statistical analysis and formatting
4. **Delivery** → Report delivered via frontend interface

## 🎯 Capability Mapping

Each component contributes to DataHerd's core capabilities:

| Capability | Primary Components | Supporting Components |
|------------|-------------------|----------------------|
| Natural Language Processing | Rule Engine, LLM Integration | API Server |
| Data Preview | Data Processor | Frontend, API Server |
| Operation Rollback | Data Processor, Database | Rule Manager |
| Rule Memory | Rule Manager, Database | LLM Integration |
| Permanent Rule Updates | Rule Manager, Database | Rule Engine |
| Operation Reporting | Report Generator, Database | Frontend |
| Client-Specific Rules | Rule Manager, Database | Rule Engine |

## 🔧 Maintenance Considerations

### Component Dependencies

- **Rule Engine** depends on LLM Integration for natural language processing
- **Data Processor** depends on Rule Engine for rule execution
- **Frontend** depends on API Server for all backend communication
- **All components** depend on Database for persistence

### Scalability Points

- **LLM Integration**: Can be optimized with caching and batch processing
- **Data Processor**: Can be scaled horizontally for large datasets
- **Database**: Can be partitioned by client or time period
- **Frontend**: Can be deployed to CDN for global access

### Monitoring Points

- **API Server**: Request/response times and error rates
- **Rule Engine**: Rule processing success rates
- **Data Processor**: Data processing volumes and performance
- **Database**: Query performance and storage usage

This component guide provides the foundation for understanding, maintaining, and extending DataHerd's capabilities. Each component is designed to be modular and replaceable while maintaining clear interfaces with other system parts.

