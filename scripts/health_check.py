#!/usr/bin/env python3
"""
System Health Check Script
==========================

Monitors API usage, system health, and performance metrics.
"""

import sys
import os
import time
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.api_clients.alpha_vantage_api import alpha_vantage
from src.api_clients.fred_api import fred_api
from src.api_clients.marketaux_api import marketaux_api

def check_api_health():
    """Check health of all APIs."""
    print("🏥 API Health Check")
    print("-" * 30)
    
    results = {}
    
    # Alpha Vantage
    try:
        start = time.time()
        response = alpha_vantage.get_stock_quote('AAPL')
        latency = time.time() - start
        
        if response and 'price' in response:
            results['alpha_vantage'] = {
                'status': '✅ Healthy',
                'latency': f'{latency:.2f}s',
                'sample_data': f"AAPL: ${response['price']}"
            }
        else:
            results['alpha_vantage'] = {
                'status': '⚠️ Issues detected',
                'latency': f'{latency:.2f}s',
                'sample_data': 'No data received'
            }
    except Exception as e:
        results['alpha_vantage'] = {
            'status': '❌ Error',
            'error': str(e)
        }
    
    # FRED API
    try:
        start = time.time()
        response = fred_api.get_vix_index()
        latency = time.time() - start
        
        if response and 'latest_value' in response:
            results['fred'] = {
                'status': '✅ Healthy',
                'latency': f'{latency:.2f}s',
                'sample_data': f"VIX: {response['latest_value']}"
            }
        else:
            results['fred'] = {
                'status': '⚠️ Issues detected',
                'latency': f'{latency:.2f}s',
                'sample_data': 'No data received'
            }
    except Exception as e:
        results['fred'] = {
            'status': '❌ Error',
            'error': str(e)
        }
    
    # MarketAux
    try:
        start = time.time()
        response = marketaux_api.get_trending_news(limit=1)
        latency = time.time() - start
        
        if response and response.get('total_articles', 0) > 0:
            results['marketaux'] = {
                'status': '✅ Healthy',
                'latency': f'{latency:.2f}s',
                'sample_data': f"{response['total_articles']} articles"
            }
        else:
            results['marketaux'] = {
                'status': '⚠️ Issues detected',
                'latency': f'{latency:.2f}s',
                'sample_data': 'No articles received'
            }
    except Exception as e:
        results['marketaux'] = {
            'status': '❌ Error',
            'error': str(e)
        }
    
    # Print results
    for api, data in results.items():
        print(f"{api.upper():15} {data['status']}")
        if 'latency' in data:
            print(f"{'':15} Latency: {data['latency']}")
        if 'sample_data' in data:
            print(f"{'':15} Data: {data['sample_data']}")
        if 'error' in data:
            print(f"{'':15} Error: {data['error']}")
        print()
    
    return results

def system_info():
    """Display system information."""
    print("💻 System Information")
    print("-" * 30)
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {os.getcwd()}")
    print()

def generate_report():
    """Generate health report."""
    print("🚀 Investment System Health Report")
    print("=" * 50)
    
    system_info()
    api_results = check_api_health()
    
    # Summary
    healthy_apis = sum(1 for result in api_results.values() if '✅' in result['status'])
    total_apis = len(api_results)
    
    print(f"📊 Summary: {healthy_apis}/{total_apis} APIs healthy")
    
    if healthy_apis == total_apis:
        print("✅ System is fully operational!")
        return True
    elif healthy_apis > 0:
        print("⚠️ System is partially operational")
        return False
    else:
        print("❌ System has critical issues")
        return False

def main():
    """Main health check function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        # JSON output for monitoring systems
        results = {
            'timestamp': datetime.now().isoformat(),
            'apis': {}
        }
        
        # Quick health checks for JSON output
        try:
            alpha_vantage.get_stock_quote('AAPL')
            results['apis']['alpha_vantage'] = 'healthy'
        except:
            results['apis']['alpha_vantage'] = 'error'
        
        try:
            fred_api.get_vix_index()
            results['apis']['fred'] = 'healthy'
        except:
            results['apis']['fred'] = 'error'
        
        try:
            marketaux_api.get_trending_news(limit=1)
            results['apis']['marketaux'] = 'healthy'
        except:
            results['apis']['marketaux'] = 'error'
        
        print(json.dumps(results, indent=2))
    else:
        # Human-readable output
        success = generate_report()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
