# DataHerd - Intelligent Cattle Data Cleaning Agent

DataHerd is an AI-powered data cleaning platform specifically designed for Elanco's cattle lot management operations. It provides intelligent, flexible data cleaning capabilities through natural language rule processing, automated data validation, and comprehensive operation tracking.

## 🚀 Key Features

- **Natural Language Rule Processing**: Define data cleaning rules in plain English
- **Intelligent Data Preview**: Review changes before applying them to your data
- **Operation Rollback**: Safely revert previous cleaning operations
- **Client-Specific Rules**: Automatically remember and apply client-specific cleaning preferences
- **Permanent Rule Management**: Update underlying cleaning rules based on operational feedback
- **Comprehensive Reporting**: Generate detailed reports of all cleaning operations
- **Real-time Processing**: Fast, efficient data processing with immediate feedback

## 🏗️ Architecture Overview

DataHerd is built on a modern, scalable architecture:

- **Backend**: FastAPI-based REST API server
- **Frontend**: React-based web interface with Tailwind CSS
- **Database**: SQLAlchemy ORM with support for multiple database backends
- **AI Integration**: OpenAI API integration for natural language processing
- **Data Processing**: Custom rule engine for flexible data validation

## 📋 Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL or SQLite database
- OpenAI API key

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ziyan0219/DataHerd.git
cd DataHerd
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your configuration
```

### 3. Frontend Setup

```bash
cd dataherd-frontend
pnpm install
pnpm run build
```

### 4. Database Initialization

```bash
# Initialize the database
python -m db.init_db
```

## 🚀 Quick Start

### 1. Start the Backend Server

```bash
python api_server/api_router.py --host 0.0.0.0 --port 9000
```

### 2. Access the Web Interface

Open your browser and navigate to `http://localhost:9000`

### 3. Configure API Key

1. Click on "Settings" in the top navigation
2. Enter your OpenAI API key
3. Click "Save Configuration"

### 4. Start Cleaning Data

1. Navigate to the "Clean Data" tab
2. Enter your batch ID and client name
3. Describe your cleaning rules in natural language
4. Preview changes or apply rules directly

## 📖 Usage Guide

### Defining Cleaning Rules

DataHerd accepts natural language descriptions of cleaning rules. Examples:

```
Flag lots where entry weight is below 500 pounds, and delete lots where entry weight is above 1500 pounds.

For Elanco clients, use stricter thresholds of 450 and 1400 pounds respectively.

Remove any lots with missing breed information or invalid birth dates.
```

### Client-Specific Rules

DataHerd automatically remembers rules for specific clients. When processing a batch for a known client, previously used rules are automatically suggested and can be reapplied.

### Permanent Rule Updates

When you identify a rule that should be applied globally, you can mark it as "permanent" to update the underlying cleaning logic for all future operations.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=sqlite:///./dataherd.db
# For PostgreSQL: postgresql://user:password@localhost/dataherd

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Server Configuration
USE_DOCKER=False
DEBUG=True
```

### Database Configuration

DataHerd supports multiple database backends through SQLAlchemy. Configure your database URL in the `.env` file.

## 📊 API Documentation

Once the server is running, visit `http://localhost:9000/docs` for interactive API documentation.

### Key Endpoints

- `POST /api/clean_data` - Apply cleaning rules to a batch
- `POST /api/preview_cleaning` - Preview cleaning changes
- `POST /api/rollback_cleaning` - Rollback a previous operation
- `POST /api/save_rule` - Save a new cleaning rule
- `GET /api/get_client_rules/{client_name}` - Get rules for a client
- `POST /api/generate_report` - Generate operation reports

## 🧪 Testing

```bash
# Run backend tests
python -m pytest tests/

# Run frontend tests
cd dataherd-frontend
pnpm test
```

## 📈 Monitoring and Logging

DataHerd provides comprehensive logging and monitoring:

- All operations are logged to the database
- Detailed operation reports can be generated
- Real-time status monitoring through the web interface

## 🔒 Security

- API key validation for AI operations
- Input sanitization for all user inputs
- Secure database connections
- CORS protection for web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions, please contact:

**Ziyan Xin**  
Email: ziyanxinbci@gmail.com  
GitHub: [@Ziyan0219](https://github.com/Ziyan0219)

## 🙏 Acknowledgments

- Built on the foundation of MateGenPro framework
- Designed specifically for Elanco's cattle data management needs
- Powered by OpenAI's language models for intelligent rule processing

---

**DataHerd** - Making cattle data cleaning intelligent, efficient, and reliable.

