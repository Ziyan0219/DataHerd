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

### Backend Stack
- **Framework**: FastAPI + Uvicorn ASGI server
- **Database**: SQLAlchemy ORM with SQLite (default), PostgreSQL/MySQL support
- **AI Integration**: OpenAI GPT-4 for natural language rule processing
- **Data Processing**: Pandas + custom rule engine
- **Authentication**: API key-based authentication

### Frontend Stack
- **Framework**: React 19 + React Router
- **Styling**: Tailwind CSS + Shadcn/ui components
- **Build Tool**: Vite with TypeScript support
- **Charts**: Recharts for data visualization
- **State Management**: React hooks + local state

### Key Features Architecture
- **SPA Routing**: Single Page Application with client-side routing
- **Real-time Feedback**: Toast notifications and progress indicators
- **Responsive Design**: Mobile-first responsive interface
- **Component Library**: Reusable UI components with consistent design

## ⚡ Quick Start (TL;DR)

```bash
# 1. Clone and setup
git clone https://github.com/Ziyan0219/DataHerd.git
cd DataHerd
python -m venv dataherd_env
source dataherd_env/bin/activate  # Windows: dataherd_env\Scripts\activate

# 2. Install dependencies
pip install fastapi uvicorn openai pandas sqlalchemy python-dotenv python-multipart

# 3. Setup environment
echo "OPENAI_API_KEY=your_key_here" > .env
echo "DATABASE_URL=sqlite:///./dataherd.db" >> .env

# 4. Build and run
cd dataherd-frontend && npm install && npm run build && cd ..
python start.py
```

**Then visit**: http://localhost:9000

## 📋 Prerequisites

- Python 3.8+ (tested with Python 3.12)
- Node.js 18+ and pnpm/npm
- SQLite (default) or PostgreSQL/MySQL (optional)
- OpenAI API key for AI-powered rule processing

### System Requirements

- Windows 10+, macOS, or Linux
- 4GB RAM minimum (8GB recommended)
- 1GB disk space for dependencies

## 🛠️ Installation

### Option 1: Automated Installation (Recommended)

```bash
git clone https://github.com/Ziyan0219/DataHerd.git
cd DataHerd
./install.sh
```

The installation script will automatically:
- Check Python version requirements
- Create a virtual environment
- Install all dependencies
- Set up environment configuration
- Initialize the database
- Build the frontend (if Node.js/pnpm available)

### Option 2: Quick Start Script

```bash
# Clone the repository
git clone https://github.com/Ziyan0219/DataHerd.git
cd DataHerd

# Run the quick start script
./start.sh
```

### Option 3: Manual Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Ziyan0219/DataHerd.git
cd DataHerd
```

#### 2. Create Virtual Environment

```bash
python3 -m venv dataherd_env
source dataherd_env/bin/activate  # On Windows: dataherd_env\Scripts\activate
```

#### 3. Install Python Dependencies

```bash
# Core backend dependencies
pip install fastapi uvicorn python-multipart
pip install pandas sqlalchemy python-dotenv
pip install openai

# Or install all from requirements.txt if available
pip install -r requirements.txt
```

**Required Python Packages:**
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server  
- `sqlalchemy` - Database ORM
- `pandas` - Data processing
- `openai` - AI integration
- `python-dotenv` - Environment configuration
- `python-multipart` - File upload support

#### 4. Environment Configuration

Create a `.env` file in the project root with the following content:

```env
# OpenAI Configuration (required for AI features)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Database Configuration
DATABASE_URL=sqlite:///./dataherd.db

# Application Configuration
USE_DOCKER=False
DEBUG=True
HOST=0.0.0.0
PORT=9000
```

**⚠️ Important**: You must provide a valid OpenAI API key for the AI-powered rule processing to work.

#### 5. Initialize Database

```bash
# Initialize the database
python -m db.init_db
```

#### 6. Build Frontend

```bash
cd dataherd-frontend
# Install frontend dependencies
pnpm install
# or if pnpm is not available
npm install

# Build the frontend
pnpm run build
# or
npm run build

cd ..
```

#### 7. Start the Application

```bash
# Basic startup
python start.py

# Development mode with auto-reload
python start.py --reload --log-level DEBUG

# Custom host and port
python start.py --host 127.0.0.1 --port 9000

# Skip database initialization (if already initialized)
python start.py --skip-db-init

# Skip frontend build (backend only)
python start.py --skip-frontend
```

### Option 4: Development Mode

For frontend development with hot reload:

```bash
# Terminal 1: Start backend
python start.py --skip-frontend

# Terminal 2: Start frontend dev server
cd dataherd-frontend
pnpm run dev
# Access at http://localhost:5173
```

### Option 5: Production Deployment

```bash
# Build everything first
cd dataherd-frontend && pnpm run build && cd ..

# Start in production mode
python start.py --host 0.0.0.0 --port 9000
```

## 🌐 Accessing the Application

Once started, the application will be available at:
- **Web Interface**: http://localhost:9000
- **API Documentation**: http://localhost:9000/docs
- **Health Check**: http://localhost:9000/health

## 📖 Usage Guide

### Getting Started

1. **Welcome Screen**: Visit http://localhost:9000 to see the welcome screen
2. **Dashboard**: Navigate to the dashboard for system overview and quick actions
3. **Data Cleaning**: Upload cattle data and define cleaning rules
4. **Rule Management**: Create, edit, and manage cleaning rules
5. **Reports**: Generate comprehensive cleaning reports

### Key Features

#### 🤖 AI-Powered Rule Processing
Define cleaning rules in natural language:

```
Flag cattle with weight below 400 pounds or above 1500 pounds
Standardize breed names to proper capitalization
Remove records with missing birth dates
Estimate missing weights based on breed and age patterns
```

#### 📊 Enhanced Preview System
- **Selective Acceptance**: Accept, reject, or edit individual changes
- **Keyboard Editing**: Click "Edit" to modify suggested values directly
- **Confidence Scoring**: See AI confidence levels for each suggestion
- **Batch Operations**: Accept all or reject all changes at once

#### 🎯 Rule Management
- **Template-Based Creation**: Base new rules on existing ones
- **Edit Functionality**: Modify existing rules with full details
- **Success Rate Tracking**: N/A for new rules, percentage for used rules
- **Client-Specific Rules**: Organize rules by client context

#### 📈 Smart Reporting
- **Real-time Generation**: Generate reports with progress indicators
- **Multiple Report Types**: Operations, client-specific, quality analysis
- **Data Cleaning Reports**: Automatic report generation after cleaning operations

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
# Run core functionality tests
python test_core_functionality.py

# Run simple integration test
python simple_test.py

# Run pytest (if test files exist)
python -m pytest tests/

# Run frontend tests (if configured)
cd dataherd-frontend
pnpm test
```

## 🚨 Troubleshooting

### Common Issues

#### White Screen on Startup
- Ensure frontend is built: `cd dataherd-frontend && pnpm run build`
- Check server logs for errors
- Verify all dependencies are installed

#### Database Errors
- Initialize database: `python -m db.init_db`
- Check SQLite file permissions
- Verify DATABASE_URL in .env file

#### OpenAI API Errors
- Verify OPENAI_API_KEY in .env file
- Check API key validity and usage limits
- Ensure internet connectivity for API calls

#### Port Already in Use
- Use different port: `python start.py --port 8000`
- Kill existing process: `lsof -ti:9000 | xargs kill -9` (Unix/Mac)

#### Windows Unicode Errors
- Ensure terminal supports UTF-8
- All emoji characters have been removed from startup messages

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

- Built with modern AI and data processing technologies
- Designed specifically for Elanco's cattle data management needs
- Powered by OpenAI's language models for intelligent rule processing

---

**DataHerd** - Making cattle data cleaning intelligent, efficient, and reliable.

