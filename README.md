# 💼 AI-Powered Investment Recommendation Agent v2.0

**A comprehensive, production-ready investment analysis platform** that combines real-time market data, economic indicators, and multi-source sentiment analysis to provide AI-powered investment recommendations.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)]()

---

## 🚀 Key Features

### 📊 **Real-Time Market Analysis**
- **Live Stock Data**: Alpha Vantage API integration with yfinance fallback
- **Technical Indicators**: SMA, EMA, RSI, MACD analysis
- **Company Fundamentals**: P/E ratios, EPS, market cap, financial metrics

### 🏛️ **Economic Intelligence**
- **Federal Reserve Data**: Real-time inflation, unemployment, GDP indicators
- **Market Volatility**: VIX index monitoring and risk assessment  
- **Interest Rates**: Fed funds rate and treasury yield tracking

### 🧠 **AI-Powered Sentiment Analysis**
- **Multi-Source Intelligence**: News, Reddit, Twitter sentiment fusion
- **Fine-Tuned Models**: FinBERT for financial text analysis
- **Professional News**: MarketAux integration with built-in sentiment scoring
- **Weighted Analysis**: 40% news, 30% AI analysis, 30% social sentiment

### 🎯 **Investment Recommendations**
- **Multi-Factor Analysis**: Technical + Fundamental + Sentiment + Economic
- **Risk Assessment**: Dynamic risk scoring based on market conditions
- **Actionable Insights**: Clear BUY/HOLD/SELL recommendations with rationale

---

## 🏗️ **Organized Project Structure**

```
investment-recommendation-system/
├── 📁 src/                          # Source code
│   ├── 🔌 api_clients/             # External API integrations
│   │   ├── alpha_vantage_api.py    # Stock data & technical indicators
│   │   ├── fred_api.py             # Economic indicators (FRED)
│   │   └── marketaux_api.py        # Financial news & sentiment
│   ├── 📊 data_processing/         # Data fetching & processing
│   │   └── data_fetch.py           # Enhanced data aggregation
│   ├── 🧠 analysis_engine/         # Core analysis logic
│   │   ├── market_analysis.py      # Market condition assessment
│   │   ├── recommendations.py     # Investment recommendation logic
│   │   └── risk_profile.py         # Risk assessment algorithms
│   ├── � sentiment_analysis/      # Multi-source sentiment analysis
│   │   ├── sentiment_model.py      # FinBERT model integration
│   │   ├── enhanced_fusion.py      # Advanced sentiment fusion
│   │   └── fusion.py               # Legacy sentiment combining
│   ├── 🗄️ database/               # Data persistence
│   │   ├── db_sqlite.py           # SQLite operations
│   │   └── db_questdb.py          # QuestDB time-series data
│   └── 🖥️ ui/                      # User interfaces
│       └── dashboard.py            # Streamlit web interface
├── 🧪 tests/                       # Test suites
│   ├── api_test.py                 # API integration tests
│   └── full_test.py                # End-to-end system tests
├── ⚙️ config/                      # Configuration files
│   └── config.py                   # Environment variables & settings
├── 📜 scripts/                     # Utility scripts
│   ├── setup.py                    # System setup automation
│   └── health_check.py             # API health monitoring
├── 📚 docs/                        # Documentation
│   ├── API_INTEGRATION_GUIDE.md   # API setup guide
│   └── IMPLEMENTATION_SUMMARY.md  # Technical implementation details
├── 🎯 main.py                      # Command-line interface
├── 📋 requirements.txt             # Python dependencies
├── 🔐 .env                         # API keys & secrets (not in repo)
└── 📖 README.md                    # This file
```

---

## 🚀 **Quick Start**

### 1. **Clone & Setup**
```bash
git clone https://github.com/KumarSatyam24/AI-Powered-Investment-Recommendation-Agent-with-Sentiment-and-Market-Analytics.git
cd AI-Powered-Investment-Recommendation-Agent-with-Sentiment-and-Market-Analytics
python scripts/setup.py
```

### 2. **Configure API Keys**
Update `.env` file with your API keys:
```env
# Get free keys from:
ALPHA_VANTAGE_KEY=your_key_here          # https://www.alphavantage.co/support/#api-key
FRED_API_KEY=your_key_here               # https://fred.stlouisfed.org/docs/api/api_key.html  
MARKETAUX_API_KEY=your_key_here          # https://www.marketaux.com/
NEWS_API_KEY=your_key_here               # https://newsapi.org/
```

### 3. **Run Analysis**
```bash
# Command-line analysis
python main.py AAPL

# Web dashboard
streamlit run src/ui/dashboard.py
```

### 4. **Health Check**
```bash
python scripts/health_check.py
```

---

## 💡 **Usage Examples**

### **Command Line Analysis**
```bash
$ python main.py TSLA

🔍 Analyzing TSLA...
==================================================
📊 INVESTMENT ANALYSIS REPORT FOR TSLA
==================================================

💰 Stock Information:
  Price: $241.05
  P/E Ratio: 45.23
  Volume: 52,341,200

📈 Market Conditions:
  Overall: Low Risk - Selective Opportunities
  VIX: 16.6

🧠 Sentiment Analysis:
  Overall Sentiment: bullish
  Confidence: 0.67
  Sources: 4

🎯 AI Recommendation:
  Buy
```

### **Web Dashboard**
```bash
streamlit run src/ui/dashboard.py
# Opens at http://localhost:8501
```

### **Python API**
```python
from main import InvestmentRecommendationSystem

system = InvestmentRecommendationSystem()
analysis = system.analyze_stock('AAPL')

print(f"Recommendation: {analysis['recommendation']}")
print(f"Sentiment: {analysis['sentiment_analysis']['overall_sentiment']}")
```

---

## 🔧 **API Integration Details**

| API Service | Purpose | Rate Limit | Cost |
|-------------|---------|------------|------|
| **Alpha Vantage** | Stock data, technicals | 25/day | Free tier |
| **FRED** | Economic indicators | Unlimited | Free |
| **MarketAux** | Financial news + sentiment | 200/month | Free tier |
| **NewsAPI** | General financial news | 1000/day | Free tier |
| **Reddit** | Social sentiment | High | Free |
| **Twitter** | Market buzz sentiment | Varies | Free tier |

---

## 🎯 **System Architecture**

### **Data Flow**
```
� Raw Data Sources → 🔄 API Clients → 📊 Data Processing → 🧠 Analysis Engine → 🎯 Recommendations
     ↓                    ↓               ↓                    ↓                    ↓
• Stock prices      • Alpha Vantage   • Data cleaning     • Technical analysis  • Buy/Hold/Sell
• Economic data     • FRED API        • Normalization     • Sentiment fusion    • Risk assessment  
• News articles     • MarketAux       • Aggregation       • Market conditions   • Confidence scores
• Social posts      • NewsAPI         • Validation        • Multi-factor model  • Detailed rationale
```

### **Analysis Components**
- **40% Technical Analysis**: Price trends, indicators, volume
- **30% Fundamental Analysis**: P/E ratios, financial health  
- **20% Sentiment Analysis**: News + social media sentiment
- **10% Market Conditions**: Economic indicators, VIX, rates

---

## 🧪 **Testing & Monitoring**

### **Run Tests**
```bash
# API integration tests
python tests/api_test.py

# Full system test
python tests/full_test.py

# Health monitoring
python scripts/health_check.py
```

### **System Health**
```bash
# JSON output for monitoring
python scripts/health_check.py --json
```

---

## 📈 **Performance & Reliability**

- **Intelligent Fallbacks**: Multiple data sources with automatic failover
- **Caching**: Reduces API calls and improves response times
- **Rate Limiting**: Respects API limits with request queuing
- **Error Handling**: Graceful degradation when services are unavailable
- **Mock Data**: Development/testing without consuming API quotas

---

## 🎓 **For Developers**

### **Adding New APIs**
1. Create client in `src/api_clients/`
2. Add to `src/api_clients/__init__.py`
3. Update data processing in `src/data_processing/`
4. Add tests in `tests/`

### **Custom Analysis**
1. Extend `src/analysis_engine/`
2. Update recommendation logic
3. Add UI components if needed

### **Development Setup**
```bash
# Install development dependencies
pip install -e .

# Run in development mode
python -m src.ui.dashboard
```

---

## 🏆 **Production Deployment**

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "src/ui/dashboard.py"]
```

### **Environment Variables**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export STREAMLIT_SERVER_PORT=8501
```

---

## 📊 **System Capabilities**

✅ **Real-time stock analysis** with 15+ technical indicators  
✅ **Economic intelligence** from Federal Reserve data  
✅ **Multi-source sentiment** with professional news integration  
✅ **AI-powered recommendations** using ensemble methods  
✅ **Risk assessment** with dynamic market condition analysis  
✅ **Web dashboard** with interactive visualizations  
✅ **Command-line interface** for scripting and automation  
✅ **Comprehensive testing** with health monitoring  
✅ **Production-ready** architecture with error handling  

---

## 👤 **Author & Support**

**Satyam Kumar**  
- GitHub: [@KumarSatyam24](https://github.com/KumarSatyam24)
- LinkedIn: [Connect](https://linkedin.com/in/your-profile)

### **Contributing**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### **Support**
- 📖 Check [docs/](docs/) for detailed guides
- 🐛 Report issues on GitHub
- 💡 Feature requests welcome

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏷️ **Version History**

- **v2.0.0** (Current) - Complete reorganization, enhanced APIs, production-ready
- **v1.0.0** - Initial release with basic functionality

---

<div align="center">

**⭐ Star this repo if it helped you make better investment decisions!**

*Built with ❤️ for the investment community*

</div>

