#!/usr/bin/env python3
"""
Production monitoring script for Article-to-Audio service
Monitors health, performance, and alerts on issues
"""

import requests
import time
import json
import smtplib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@dataclass
class HealthCheck:
    timestamp: datetime
    status_code: int
    response_time: float
    success: bool
    error: Optional[str] = None

class ProductionMonitor:
    def __init__(self, base_url: str = "https://article-to-audio-server.onrender.com"):
        self.base_url = base_url
        self.health_history: List[HealthCheck] = []
        self.alert_threshold = 3  # Number of consecutive failures before alert
        self.check_interval = 60  # Check every minute
        
    def check_health(self) -> HealthCheck:
        """Perform health check"""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            return HealthCheck(
                timestamp=datetime.now(),
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                timestamp=datetime.now(),
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    def check_api_endpoints(self) -> Dict[str, bool]:
        """Test critical API endpoints"""
        endpoints = {
            '/health': 'GET',
            '/library/test@example.com': 'GET'
        }
        
        results = {}
        
        for endpoint, method in endpoints.items():
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                elif method == 'POST':
                    response = requests.post(f"{self.base_url}{endpoint}", json={}, timeout=10)
                
                results[endpoint] = response.status_code < 500
                
            except Exception:
                results[endpoint] = False
        
        return results
    
    def check_database_connection(self) -> bool:
        """Test database connectivity through API"""
        try:
            # Test a simple database operation
            response = requests.get(f"{self.base_url}/library/monitor@test.com", timeout=10)
            # Even if user doesn't exist, database connection should work (return empty array)
            return response.status_code in [200, 404]
        except Exception:
            return False
    
    def get_recent_failures(self) -> List[HealthCheck]:
        """Get recent failed health checks"""
        recent_failures = []
        for check in reversed(self.health_history[-10:]):  # Last 10 checks
            if not check.success:
                recent_failures.append(check)
            else:
                break  # Stop at first success
        return recent_failures
    
    def should_alert(self) -> bool:
        """Determine if alert should be sent"""
        recent_failures = self.get_recent_failures()
        return len(recent_failures) >= self.alert_threshold
    
    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        if not self.health_history:
            return "No health check data available"
        
        recent_checks = self.health_history[-20:]  # Last 20 checks
        successful_checks = [c for c in recent_checks if c.success]
        failed_checks = [c for c in recent_checks if not c.success]
        
        success_rate = len(successful_checks) / len(recent_checks) * 100
        avg_response_time = sum(c.response_time for c in successful_checks) / len(successful_checks) if successful_checks else 0
        
        # API endpoint status
        api_status = self.check_api_endpoints()
        db_status = self.check_database_connection()
        
        report = f"""
📊 Article-to-Audio Service Status Report
{'='*60}
🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔗 Service URL: {self.base_url}

📈 Performance Metrics (Last 20 checks):
   Success Rate: {success_rate:.1f}%
   Avg Response Time: {avg_response_time:.2f}s
   Failed Checks: {len(failed_checks)}
   Recent Failures: {len(self.get_recent_failures())}

🔍 Component Status:
   Main Service: {'✅ UP' if self.health_history[-1].success else '❌ DOWN'}
   Database: {'✅ Connected' if db_status else '❌ Disconnected'}
   
📡 API Endpoints:
"""
        
        for endpoint, status in api_status.items():
            status_icon = '✅' if status else '❌'
            report += f"   {status_icon} {endpoint}\n"
        
        if failed_checks:
            report += f"\n⚠️ Recent Errors:\n"
            for check in failed_checks[-5:]:  # Last 5 failures
                report += f"   {check.timestamp.strftime('%H:%M:%S')} - {check.error or f'HTTP {check.status_code}'}\n"
        
        return report
    
    def send_alert(self, message: str):
        """Send alert notification (placeholder - implement email/Slack/etc.)"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alert_message = f"""
🚨 ALERT: Article-to-Audio Service Issue
Time: {timestamp}

{message}

🔗 Service URL: {self.base_url}
📊 Status: Check monitoring dashboard for details
        """
        
        print("🚨 ALERT TRIGGERED:")
        print(alert_message)
        
        # TODO: Implement actual alerting (email, Slack, etc.)
        # Example email implementation:
        # self.send_email_alert(alert_message)
    
    def send_email_alert(self, message: str):
        """Send email alert (requires SMTP configuration)"""
        # Placeholder for email alerting
        # Configure SMTP settings in environment variables
        pass
    
    def log_status(self, check: HealthCheck):
        """Log status to console with color coding"""
        timestamp = check.timestamp.strftime('%H:%M:%S')
        
        if check.success:
            print(f"✅ {timestamp} - Service UP - {check.response_time:.2f}s")
        else:
            error_msg = check.error or f"HTTP {check.status_code}"
            print(f"❌ {timestamp} - Service DOWN - {error_msg}")
    
    def run_monitoring(self, duration_minutes: Optional[int] = None):
        """Run continuous monitoring"""
        start_time = time.time()
        print(f"🚀 Starting monitoring for {self.base_url}")
        print(f"⏱️ Check interval: {self.check_interval}s")
        
        if duration_minutes:
            print(f"⏰ Duration: {duration_minutes} minutes")
        else:
            print("⏰ Duration: Indefinite (Ctrl+C to stop)")
        
        try:
            while True:
                # Perform health check
                check = self.check_health()
                self.health_history.append(check)
                self.log_status(check)
                
                # Check for alerting
                if self.should_alert():
                    report = self.generate_status_report()
                    self.send_alert(f"Service has failed {len(self.get_recent_failures())} consecutive checks\n\n{report}")
                
                # Print periodic status report
                if len(self.health_history) % 10 == 0:  # Every 10 checks
                    print("\n" + self.generate_status_report())
                
                # Check duration limit
                if duration_minutes:
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes >= duration_minutes:
                        break
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        
        finally:
            print(f"\n📊 Final Status Report:")
            print(self.generate_status_report())

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Article-to-Audio service')
    parser.add_argument('--url', default='https://article-to-audio-server.onrender.com', 
                       help='Service URL to monitor')
    parser.add_argument('--interval', type=int, default=60, 
                       help='Check interval in seconds')
    parser.add_argument('--duration', type=int, 
                       help='Duration in minutes (default: indefinite)')
    parser.add_argument('--test', action='store_true', 
                       help='Run single test and exit')
    
    args = parser.parse_args()
    
    monitor = ProductionMonitor(args.url)
    monitor.check_interval = args.interval
    
    if args.test:
        print("🧪 Running single test...")
        check = monitor.check_health()
        monitor.log_status(check)
        
        api_status = monitor.check_api_endpoints()
        db_status = monitor.check_database_connection()
        
        print(f"\n📊 Test Results:")
        print(f"   Service: {'✅ UP' if check.success else '❌ DOWN'}")
        print(f"   Database: {'✅ Connected' if db_status else '❌ Disconnected'}")
        print(f"   Response Time: {check.response_time:.2f}s")
        
        for endpoint, status in api_status.items():
            status_icon = '✅' if status else '❌'
            print(f"   {status_icon} {endpoint}")
            
    else:
        monitor.run_monitoring(args.duration)

if __name__ == "__main__":
    main()