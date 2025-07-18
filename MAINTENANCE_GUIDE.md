# DataHerd Maintenance Guide

This guide provides comprehensive instructions for maintaining, updating, and troubleshooting the DataHerd system.

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Database Management](#database-management)
3. [Rule Management](#rule-management)
4. [Configuration Updates](#configuration-updates)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Backup and Recovery](#backup-and-recovery)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)
9. [Security Maintenance](#security-maintenance)
10. [Deployment Updates](#deployment-updates)

## 🖥️ System Requirements

### Minimum Requirements
- **CPU**: 2 cores, 2.4 GHz
- **RAM**: 4 GB
- **Storage**: 20 GB available space
- **Network**: Stable internet connection for AI API calls

### Recommended Requirements
- **CPU**: 4+ cores, 3.0+ GHz
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: High-speed internet (100+ Mbps)

### Software Dependencies
- Python 3.11+
- Node.js 20+
- PostgreSQL 13+ (recommended) or SQLite 3.35+
- Git 2.30+

## 🗄️ Database Management

### Database Connection Configuration

DataHerd supports multiple database backends. Configure your database in the `.env` file:

```env
# SQLite (Development)
DATABASE_URL=sqlite:///./dataherd.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://username:password@localhost:5432/dataherd

# MySQL (Alternative)
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/dataherd
```

### Database Initialization

```bash
# Initialize a new database
python -m db.init_db

# Reset database (WARNING: This will delete all data)
python -m db.init_db --reset
```

### Database Migrations

When updating the system, you may need to migrate the database schema:

```bash
# Check current schema version
python -c "from db.base_model import check_schema_version; check_schema_version()"

# Apply pending migrations
python -m db.migrate

# Create a new migration (for developers)
python -m db.create_migration "description_of_changes"
```

### Database Backup

#### SQLite Backup
```bash
# Create backup
cp dataherd.db dataherd_backup_$(date +%Y%m%d_%H%M%S).db

# Restore from backup
cp dataherd_backup_20250718_120000.db dataherd.db
```

#### PostgreSQL Backup
```bash
# Create backup
pg_dump -h localhost -U username dataherd > dataherd_backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -h localhost -U username dataherd < dataherd_backup_20250718_120000.sql
```

### Database Maintenance Tasks

#### Weekly Tasks
```bash
# Analyze database performance
python -m db.analyze_performance

# Clean up old operation logs (older than 90 days)
python -m db.cleanup_logs --days 90

# Vacuum database (SQLite only)
python -c "from db.utils import vacuum_database; vacuum_database()"
```

#### Monthly Tasks
```bash
# Generate database health report
python -m db.health_report

# Optimize database indexes
python -m db.optimize_indexes

# Archive old data
python -m db.archive_data --months 12
```

## 📏 Rule Management

### Viewing Current Rules

```bash
# List all permanent rules
python -m dataherd.rule_manager list_permanent_rules

# List rules for a specific client
python -m dataherd.rule_manager list_client_rules --client "Elanco"

# Export all rules to JSON
python -m dataherd.rule_manager export_rules --output rules_backup.json
```

### Adding New Base Rules

```bash
# Add a new permanent rule
python -m dataherd.rule_manager add_permanent_rule \
  --description "Flag lots with entry weight below 400 pounds" \
  --rule_type "weight_validation" \
  --priority 1
```

### Updating Existing Rules

```bash
# Update a permanent rule
python -m dataherd.rule_manager update_rule \
  --rule_id "rule_001" \
  --description "Updated weight threshold to 450 pounds"

# Disable a rule temporarily
python -m dataherd.rule_manager disable_rule --rule_id "rule_001"

# Re-enable a rule
python -m dataherd.rule_manager enable_rule --rule_id "rule_001"
```

### Rule Import/Export

```bash
# Import rules from JSON file
python -m dataherd.rule_manager import_rules --input rules_backup.json

# Export rules with specific criteria
python -m dataherd.rule_manager export_rules \
  --client "Elanco" \
  --date_from "2025-01-01" \
  --output elanco_rules.json
```

### Rule Validation

```bash
# Validate all rules
python -m dataherd.rule_manager validate_all_rules

# Test a specific rule
python -m dataherd.rule_manager test_rule \
  --rule_id "rule_001" \
  --test_data "test_batch.csv"
```

## ⚙️ Configuration Updates

### Environment Variables

Key configuration variables in `.env`:

```env
# Database
DATABASE_URL=your_database_url

# OpenAI API
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Server Settings
HOST=0.0.0.0
PORT=9000
DEBUG=False
USE_DOCKER=False

# Security
SECRET_KEY=your_secret_key
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=dataherd.log

# Performance
MAX_WORKERS=4
CACHE_TTL=3600
```

### Updating Configuration

1. **Stop the service**:
   ```bash
   # If running as a service
   sudo systemctl stop dataherd
   
   # If running manually
   pkill -f "python api_server/api_router.py"
   ```

2. **Update configuration**:
   ```bash
   # Edit the .env file
   nano .env
   ```

3. **Validate configuration**:
   ```bash
   python -m config.validate
   ```

4. **Restart the service**:
   ```bash
   # If running as a service
   sudo systemctl start dataherd
   
   # If running manually
   python api_server/api_router.py --host 0.0.0.0 --port 9000
   ```

## 📊 Monitoring and Logging

### Log Files

DataHerd generates several types of logs:

- **Application Log**: `dataherd.log` - General application events
- **API Log**: `api.log` - HTTP request/response logs
- **Database Log**: `database.log` - Database operation logs
- **Error Log**: `error.log` - Error and exception logs

### Log Rotation

Configure log rotation to prevent disk space issues:

```bash
# Install logrotate configuration
sudo cp config/logrotate.conf /etc/logrotate.d/dataherd

# Test log rotation
sudo logrotate -d /etc/logrotate.d/dataherd

# Force log rotation
sudo logrotate -f /etc/logrotate.d/dataherd
```

### Monitoring Scripts

```bash
# Check system health
python -m monitoring.health_check

# Monitor API performance
python -m monitoring.api_monitor --duration 3600

# Generate performance report
python -m monitoring.performance_report --output performance.html
```

### Setting Up Alerts

```bash
# Configure email alerts for errors
python -m monitoring.setup_alerts \
  --email admin@yourcompany.com \
  --threshold error \
  --frequency daily

# Configure Slack notifications
python -m monitoring.setup_slack \
  --webhook_url "your_slack_webhook" \
  --channel "#dataherd-alerts"
```

## 💾 Backup and Recovery

### Automated Backup Setup

Create a backup script (`backup.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/dataherd"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
python -m db.backup --output "$BACKUP_DIR/db_$DATE.sql"

# Backup configuration
cp .env "$BACKUP_DIR/config_$DATE.env"

# Backup rules
python -m dataherd.rule_manager export_rules --output "$BACKUP_DIR/rules_$DATE.json"

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" *.log

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.json" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Set up automated backups:

```bash
# Make script executable
chmod +x backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /path/to/dataherd/backup.sh" | crontab -
```

### Recovery Procedures

#### Complete System Recovery

1. **Stop the service**:
   ```bash
   sudo systemctl stop dataherd
   ```

2. **Restore database**:
   ```bash
   python -m db.restore --backup db_20250718_020000.sql
   ```

3. **Restore configuration**:
   ```bash
   cp config_20250718_020000.env .env
   ```

4. **Restore rules**:
   ```bash
   python -m dataherd.rule_manager import_rules --input rules_20250718_020000.json
   ```

5. **Restart service**:
   ```bash
   sudo systemctl start dataherd
   ```

#### Partial Recovery

```bash
# Restore only rules
python -m dataherd.rule_manager import_rules --input rules_backup.json --merge

# Restore specific client data
python -m db.restore_client --client "Elanco" --backup client_backup.sql

# Restore operation logs
python -m db.restore_logs --backup logs_backup.sql --date_from "2025-07-01"
```

## 🚀 Performance Optimization

### Database Optimization

```bash
# Analyze slow queries
python -m db.analyze_slow_queries --threshold 1000

# Optimize indexes
python -m db.optimize_indexes

# Update table statistics
python -m db.update_statistics
```

### Application Optimization

```bash
# Profile API performance
python -m profiling.api_profiler --duration 3600

# Optimize rule processing
python -m profiling.rule_profiler --sample_size 1000

# Memory usage analysis
python -m profiling.memory_profiler
```

### Caching Configuration

```bash
# Enable Redis caching
pip install redis
export CACHE_BACKEND=redis
export REDIS_URL=redis://localhost:6379/0

# Clear cache
python -m cache.clear_all

# Cache statistics
python -m cache.stats
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Symptoms**: "Database connection failed" errors

**Solutions**:
```bash
# Check database status
python -m db.check_connection

# Test database credentials
python -m db.test_credentials

# Reset database connection pool
python -m db.reset_pool
```

#### 2. OpenAI API Errors

**Symptoms**: "API key invalid" or "Rate limit exceeded"

**Solutions**:
```bash
# Validate API key
python -m dataherd.llm_integration test_api_key

# Check API usage
python -m dataherd.llm_integration check_usage

# Switch to backup API endpoint
export OPENAI_API_BASE=https://backup-api.openai.com/v1
```

#### 3. High Memory Usage

**Symptoms**: System becomes slow, out of memory errors

**Solutions**:
```bash
# Check memory usage
python -m monitoring.memory_check

# Clear application cache
python -m cache.clear_all

# Restart with memory profiling
python -m memory_profiler api_server/api_router.py
```

#### 4. Slow Rule Processing

**Symptoms**: Rules take a long time to process

**Solutions**:
```bash
# Profile rule processing
python -m profiling.rule_profiler

# Optimize rule cache
python -m dataherd.rule_engine optimize_cache

# Check LLM response times
python -m dataherd.llm_integration benchmark
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set debug environment
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with debug output
python api_server/api_router.py --debug
```

### Log Analysis

```bash
# Search for errors in logs
grep -i error dataherd.log | tail -20

# Analyze API response times
python -m monitoring.analyze_logs --metric response_time --period 24h

# Find slow database queries
python -m monitoring.analyze_logs --metric db_query --threshold 1000
```

## 🔒 Security Maintenance

### API Key Rotation

```bash
# Update OpenAI API key
python -m security.rotate_api_key --service openai --new_key "new_api_key"

# Update database credentials
python -m security.rotate_db_credentials --new_password "new_password"
```

### Security Audits

```bash
# Run security scan
python -m security.audit

# Check for vulnerable dependencies
pip audit

# Validate input sanitization
python -m security.test_input_validation
```

### Access Control

```bash
# List current API keys
python -m security.list_api_keys

# Revoke compromised key
python -m security.revoke_api_key --key_id "key_123"

# Generate new access token
python -m security.generate_token --user "admin" --expires "30d"
```

## 🚀 Deployment Updates

### Application Updates

1. **Backup current system**:
   ```bash
   ./backup.sh
   ```

2. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

3. **Update dependencies**:
   ```bash
   pip install -r requirements.txt
   cd dataherd-frontend && pnpm install
   ```

4. **Run database migrations**:
   ```bash
   python -m db.migrate
   ```

5. **Build frontend**:
   ```bash
   cd dataherd-frontend && pnpm run build
   cp -r dist/* ../static/
   ```

6. **Test the update**:
   ```bash
   python -m tests.integration_test
   ```

7. **Restart services**:
   ```bash
   sudo systemctl restart dataherd
   ```

### Rollback Procedure

If an update fails:

1. **Stop the service**:
   ```bash
   sudo systemctl stop dataherd
   ```

2. **Revert to previous version**:
   ```bash
   git checkout previous_stable_tag
   ```

3. **Restore database**:
   ```bash
   python -m db.restore --backup latest_backup.sql
   ```

4. **Restart service**:
   ```bash
   sudo systemctl start dataherd
   ```

### Health Checks

After any maintenance:

```bash
# Comprehensive health check
python -m monitoring.health_check --comprehensive

# API endpoint tests
python -m tests.api_test

# Database integrity check
python -m db.integrity_check

# Frontend functionality test
python -m tests.frontend_test
```

## 📞 Support and Escalation

### Internal Troubleshooting

1. Check logs for error messages
2. Verify configuration settings
3. Test database connectivity
4. Validate API credentials
5. Check system resources

### External Support

For issues requiring external support:

**Primary Contact**: Ziyan Xin (ziyanxinbci@gmail.com)

**Information to Include**:
- Error messages and logs
- System configuration
- Steps to reproduce the issue
- Impact on operations
- Attempted solutions

### Emergency Procedures

For critical system failures:

1. **Immediate Response**:
   - Stop the service to prevent data corruption
   - Switch to backup system if available
   - Notify stakeholders

2. **Assessment**:
   - Identify the root cause
   - Estimate recovery time
   - Determine data integrity status

3. **Recovery**:
   - Restore from latest backup
   - Apply emergency fixes
   - Validate system functionality

4. **Post-Incident**:
   - Document the incident
   - Update procedures
   - Implement preventive measures

This maintenance guide should be reviewed and updated regularly to reflect system changes and operational experience.

