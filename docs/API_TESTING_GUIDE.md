# API Testing Scripts - Usage Guide

This directory contains three specialized API testing scripts to help you monitor and debug your investment recommendation system's API integrations.

## 🔍 Available Scripts

### 1. `api_status_checker.py` - Comprehensive API Testing
**Purpose**: Full detailed testing of all APIs with complete status reports

**Features**:
- Tests all 8 APIs individually (News, Alpha Vantage, FRED, MarketAux, Reddit, Twitter, Grok, Yahoo Finance)
- Provides detailed error messages and diagnostic information
- Generates JSON reports with timestamps
- Gives specific recommendations for fixing issues
- Shows API usage details and limitations

**Usage**:
```bash
python api_status_checker.py
```

**Output**: Detailed report + saved JSON file with results

### 2. `quick_api_check.py` - Daily Health Check
**Purpose**: Fast daily monitoring of core APIs

**Features**:
- Quick 5-second check of essential APIs
- Simple pass/fail status for each API
- Overall system health percentage
- Minimal output for regular monitoring

**Usage**:
```bash
python quick_api_check.py
```

**Output**: Simple status overview with overall health score

### 3. `test_investment_system.py` - Functional Testing
**Purpose**: Test actual investment system functionality end-to-end

**Features**:
- Tests stock data retrieval
- Tests market analysis engine
- Tests sentiment analysis
- Tests CSV generation
- Tests investment dashboard
- Verifies the system is ready for real use

**Usage**:
```bash
PYTHONPATH=. python test_investment_system.py
```

**Output**: Comprehensive system readiness report

## 📊 When to Use Each Script

### Daily Monitoring
Use `quick_api_check.py` for:
- Quick daily health checks
- Monitoring in production
- Automated health checks via cron jobs

### Debugging Issues
Use `api_status_checker.py` for:
- Investigating API problems
- Setting up new API keys
- Detailed troubleshooting
- Generating reports for stakeholders

### System Validation
Use `test_investment_system.py` for:
- Before important demos or presentations
- After code changes or updates
- Verifying end-to-end functionality
- Confirming system readiness

## 🎯 API Status Meanings

| Status | Meaning | Action Required |
|--------|---------|----------------|
| ✅ Working | API fully functional | None |
| ⚠️ Limited | API has restrictions (rate limits, etc.) | Consider upgrading plan |
| ❌ Failed | API not working | Check keys, connectivity, service status |

## 🔧 Common Issues & Solutions

### Rate Limits
- **Problem**: "Rate limit exceeded" 
- **Solution**: Wait for reset or upgrade API plan

### Invalid API Keys
- **Problem**: "Unauthorized" or "Invalid API key"
- **Solution**: Check `.env` file and verify keys on provider websites

### Network Issues
- **Problem**: Timeout or connection errors
- **Solution**: Check internet connection and firewall settings

### Missing Dependencies
- **Problem**: Import errors
- **Solution**: Run `pip install -r requirements.txt`

## 📈 System Health Levels

### 🟢 Excellent (80-100%)
- All core APIs working
- Full functionality available
- Ready for production use

### 🟡 Good (60-79%)
- Most APIs working
- Some features may be limited
- System operational with minor issues

### 🟠 Limited (40-59%)
- Basic functionality available
- Several APIs down
- Degraded performance expected

### 🔴 Critical (0-39%)
- Major functionality issues
- Most APIs down
- System needs immediate attention

## 🚀 Quick Start

1. **First-time setup**: Run comprehensive test
   ```bash
   python api_status_checker.py
   ```

2. **Daily monitoring**: Use quick check
   ```bash
   python quick_api_check.py
   ```

3. **Before using system**: Validate functionality
   ```bash
   PYTHONPATH=. python test_investment_system.py
   ```

## 📝 Notes

- All scripts automatically handle rate limits and API errors gracefully
- Results are saved with timestamps for tracking
- Scripts can be integrated into CI/CD pipelines
- Exit codes indicate system status (0=good, 1=degraded, 2=critical)

## 🔗 Integration Tips

### Cron Job Example (Daily Check)
```bash
# Add to crontab for daily 9 AM check
0 9 * * * cd /path/to/project && python quick_api_check.py >> api_health.log 2>&1
```

### Pre-deployment Check
```bash
# Add to deployment script
PYTHONPATH=. python test_investment_system.py || exit 1
```