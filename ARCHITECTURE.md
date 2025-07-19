# DataHerd Architecture Documentation

## Overview

DataHerd is a comprehensive cattle data cleaning and management system that leverages natural language processing to understand and apply data cleaning rules. The system is designed to handle large-scale cattle lot management data with intelligent rule-based processing, preview capabilities, and comprehensive reporting.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DataHerd System                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React)                                               │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │   Dashboard     │  Data Cleaning  │    Rule Management      │ │
│  │                 │                 │                         │ │
│  │   Reports       │    Settings     │      History           │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                           │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │  Data Endpoints │ Rule Endpoints  │   Report Endpoints      │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Core Processing Layer                                          │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │ NLP Processor   │ Data Processor  │   Rule Manager          │ │
│  │                 │                 │                         │ │
│  │ Report Gen.     │ Database Layer  │   Configuration         │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Data Storage                                                   │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │   SQLite/MySQL  │   File Storage  │    Cache Layer          │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Layer (React Application)

**Location**: `dataherd-frontend/`

**Purpose**: Provides a modern, responsive web interface for users to interact with the DataHerd system.

**Key Components**:
- **Dashboard**: Overview of system status, recent activities, and key metrics
- **Data Cleaning**: Interface for uploading data, applying rules, and previewing changes
- **Rule Management**: Create, edit, and manage data cleaning rules
- **Reports**: Generate and view comprehensive reports
- **Settings**: System configuration and user preferences

**Technologies**:
- React 18
- Tailwind CSS
- Shadcn/ui components
- Recharts for visualizations
- React Router for navigation

**Key Features**:
- Responsive design for desktop and mobile
- Real-time updates via WebSocket connections
- Interactive data preview with change highlighting
- Drag-and-drop file upload
- Advanced filtering and search capabilities

### 2. API Layer (FastAPI)

**Location**: `api_server/`

**Purpose**: Provides RESTful API endpoints for frontend-backend communication and external integrations.

**Key Endpoints**:

```
POST   /api/data/upload              # Upload data files
GET    /api/data/preview/{batch_id}  # Preview data changes
POST   /api/data/apply               # Apply data changes
POST   /api/data/rollback            # Rollback changes

POST   /api/rules/parse              # Parse natural language rules
GET    /api/rules/                   # List all rules
POST   /api/rules/                   # Create new rule
PUT    /api/rules/{rule_id}          # Update rule
DELETE /api/rules/{rule_id}          # Delete rule

GET    /api/reports/                 # List reports
POST   /api/reports/generate         # Generate new report
GET    /api/reports/{report_id}      # Get specific report
POST   /api/reports/{report_id}/export # Export report

GET    /api/health                   # Health check
GET    /api/status                   # System status
```

**Technologies**:
- FastAPI framework
- Pydantic for data validation
- SQLAlchemy for database ORM
- Uvicorn ASGI server

### 3. Core Processing Layer

#### 3.1 NLP Processor (`dataherd/nlp_processor.py`)

**Purpose**: Converts natural language rules into executable data cleaning operations.

**Key Capabilities**:
1. **Natural Language Rule Understanding**: Interprets plain English descriptions of data cleaning rules
2. **Contextual Rule Application**: Adjusts rules based on client-specific contexts (e.g., Elanco)
3. **Rule Confidence Scoring**: Provides confidence scores for rule interpretations
4. **Executable Code Generation**: Converts parsed rules into Python code

**Core Classes**:
- `NLPProcessor`: Main processing class
- `ParsedRule`: Structured representation of parsed rules
- `RuleType`: Enumeration of rule types (validation, standardization, cleaning, estimation)

**Integration**:
- Uses OpenAI API for advanced natural language understanding
- Fallback to pattern-based parsing for offline operation
- Integrates with Rule Manager for persistence

#### 3.2 Data Processor (`dataherd/data_processor.py`)

**Purpose**: Handles core data cleaning operations with preview and rollback capabilities.

**Key Capabilities**:
1. **Data Preview and Rollback**: Preview changes before applying, with full rollback support
2. **Batch Processing**: Handle large datasets efficiently
3. **Change Tracking**: Detailed logging of all data modifications
4. **Quality Metrics**: Calculate data quality improvement scores

**Core Methods**:
- `preview_changes()`: Generate preview of potential changes
- `apply_changes()`: Apply approved changes to data
- `rollback_changes()`: Revert data to previous state
- `process_natural_language_rules()`: Integration with NLP processor

**Data Flow**:
```
Raw Data → Load → Parse Rules → Preview Changes → User Approval → Apply Changes → Generate Report
                                      ↓
                                 Cache for Rollback
```

#### 3.3 Rule Manager (`dataherd/rule_manager.py`)

**Purpose**: Manages rule persistence, versioning, and client-specific rule templates.

**Key Capabilities**:
1. **Rule Memory and Persistence**: Store and retrieve rules with full metadata
2. **Client-Specific Templates**: Create and apply rule templates for specific clients
3. **Usage Analytics**: Track rule effectiveness and usage patterns
4. **Rule Versioning**: Maintain history of rule changes

**Database Schema**:
```sql
rules (
    id, name, description, rule_type, field, condition, action,
    parameters, confidence, client_context, is_permanent, is_active,
    created_at, updated_at, usage_count, success_rate, last_used
)

rule_applications (
    id, rule_id, batch_id, applied_at, success, changes_made, confidence_achieved
)

client_templates (
    id, client_name, template_name, template_rules, created_at, is_active
)
```

#### 3.4 Report Generator (`dataherd/report_generator.py`)

**Purpose**: Generates comprehensive reports with analytics and visualizations.

**Key Capabilities**:
1. **Comprehensive Reporting**: Detailed analysis of data cleaning operations
2. **Multiple Report Types**: 
   - Comprehensive cleaning reports
   - Audit trail reports
   - Client summary reports
   - Operation reports
3. **Visualization Generation**: Charts and graphs using matplotlib/seaborn
4. **Multiple Export Formats**: HTML, JSON, PDF support

**Report Types**:
- **Comprehensive Report**: Complete analysis with executive summary, quality assessment, and recommendations
- **Audit Trail Report**: Detailed operation timeline for compliance
- **Client Summary Report**: Aggregated statistics across multiple batches for specific clients
- **Operation Report**: System-wide operation statistics and performance metrics

### 4. Database Layer

**Location**: `db/`

**Purpose**: Handles data persistence and database operations.

**Components**:
- `models.py`: SQLAlchemy models for cattle data
- `init_db.py`: Database initialization and migration scripts
- `base.py`: Database connection and session management

**Supported Databases**:
- SQLite (development and small deployments)
- MySQL (production deployments)

**Key Models**:
```python
CattleRecord:
    - lot_id: Unique identifier
    - weight: Animal weight in pounds
    - breed: Cattle breed
    - birth_date: Date of birth
    - health_status: Health information
    - feed_type: Feed information
    - created_at, updated_at: Timestamps
```

## Data Flow Architecture

### 1. Data Ingestion Flow

```
User Upload → File Validation → Data Parsing → Schema Validation → Database Storage
     ↓
Batch ID Generation → Preview Generation → User Interface Update
```

### 2. Rule Processing Flow

```
Natural Language Input → NLP Processor → Parsed Rules → Rule Validation
     ↓
Rule Storage → Template Creation → Client Association → Usage Tracking
```

### 3. Data Cleaning Flow

```
Data Batch + Rules → Preview Generation → User Review → Change Application
     ↓
Change Logging → Quality Metrics → Report Generation → Result Storage
```

### 4. Reporting Flow

```
Processing Results → Data Aggregation → Visualization Generation → Report Compilation
     ↓
Format Export → User Delivery → Archive Storage
```

## Key Features Implementation

### 1. Natural Language Rule Understanding

**Implementation**: 
- Primary: OpenAI GPT-4 API for advanced understanding
- Fallback: Pattern-based parsing for common cattle data patterns
- Context awareness for client-specific requirements

**Example Rule Processing**:
```
Input: "Flag any cattle with weight below 400 pounds or above 1500 pounds"
Output: ParsedRule(
    rule_type=RuleType.VALIDATION,
    field="weight",
    condition="weight < 400 or weight > 1500",
    action="flag_as_error",
    parameters={"min_weight": 400, "max_weight": 1500},
    confidence=0.95
)
```

### 2. Contextual Rule Application

**Client Context Integration**:
- Rules can be tailored for specific clients (e.g., Elanco)
- Client-specific data patterns and requirements
- Historical rule effectiveness tracking per client

**Implementation**:
```python
def process_natural_language_rules(self, rule_text: str, client_context: str = ""):
    # Incorporate client context into rule processing
    # Adjust parameters based on client history
    # Apply client-specific validation thresholds
```

### 3. Data Preview and Rollback

**Preview System**:
- Non-destructive change preview
- Detailed change breakdown by category
- Confidence scoring for each proposed change
- User approval workflow

**Rollback Mechanism**:
- Complete data state preservation
- Operation-level rollback capability
- Audit trail maintenance
- Data integrity verification

### 4. Rule Memory and Persistence

**Storage Strategy**:
- SQLite database for rule metadata
- JSON serialization for complex rule parameters
- Version control for rule changes
- Usage analytics and effectiveness tracking

**Template System**:
- Client-specific rule templates
- Template versioning and inheritance
- Bulk rule application from templates
- Template sharing across similar clients

### 5. Comprehensive Reporting

**Report Generation Pipeline**:
1. Data aggregation from multiple sources
2. Statistical analysis and trend calculation
3. Visualization generation (charts, graphs)
4. Template-based report compilation
5. Multi-format export (HTML, JSON, PDF)

**Report Components**:
- Executive summaries with key metrics
- Detailed change breakdowns
- Performance analytics
- Quality improvement measurements
- Actionable recommendations

## Security and Compliance

### Data Security
- Input validation and sanitization
- SQL injection prevention
- Secure file upload handling
- Data encryption at rest (configurable)

### Audit Trail
- Complete operation logging
- User action tracking
- Change history preservation
- Compliance reporting capabilities

### Access Control
- Role-based access control (planned)
- Client data isolation
- API key authentication
- Session management

## Performance Considerations

### Scalability
- Asynchronous processing for large datasets
- Database connection pooling
- Caching layer for frequently accessed data
- Batch processing optimization

### Optimization
- Lazy loading for large datasets
- Efficient database queries with proper indexing
- Memory management for large file processing
- Background task processing

## Deployment Architecture

### Development Environment
```
Local Development:
- SQLite database
- File-based storage
- Development server (uvicorn)
- Hot reload enabled
```

### Production Environment
```
Production Deployment:
- MySQL database with replication
- Cloud storage integration
- Load balancer + multiple app instances
- Redis cache layer
- Monitoring and logging
```

### Container Deployment
```
Docker Containers:
- Frontend: Nginx + React build
- Backend: Python + FastAPI
- Database: MySQL container
- Cache: Redis container
```

## Integration Points

### External APIs
- OpenAI API for natural language processing
- Email services for notifications
- Cloud storage for file management
- Monitoring services for system health

### Data Sources
- CSV file uploads
- Excel file imports
- Database connections (planned)
- API integrations (planned)

### Export Targets
- Local file downloads
- Email delivery
- Cloud storage upload
- API webhooks (planned)

## Monitoring and Maintenance

### Health Monitoring
- System health endpoints
- Database connection monitoring
- API response time tracking
- Error rate monitoring

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Performance metrics logging

### Maintenance Tasks
- Database cleanup and optimization
- Log rotation and archival
- Cache invalidation
- Rule effectiveness analysis

## Future Enhancements

### Planned Features
1. **Real-time Processing**: WebSocket-based real-time updates
2. **Advanced Analytics**: Machine learning for pattern detection
3. **Multi-tenant Architecture**: Full client isolation and customization
4. **API Integrations**: Direct integration with cattle management systems
5. **Mobile Application**: Native mobile app for field data collection
6. **Advanced Visualizations**: Interactive dashboards and charts

### Technical Improvements
1. **Microservices Architecture**: Split into specialized services
2. **Event-Driven Architecture**: Implement event sourcing
3. **Advanced Caching**: Redis-based distributed caching
4. **Container Orchestration**: Kubernetes deployment
5. **CI/CD Pipeline**: Automated testing and deployment

This architecture provides a solid foundation for the DataHerd system while maintaining flexibility for future enhancements and scalability requirements.

