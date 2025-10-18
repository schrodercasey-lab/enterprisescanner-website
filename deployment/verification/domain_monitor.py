#!/usr/bin/env python3
"""
Enterprise Scanner Domain Monitoring
Continuous monitoring of domain health and performance
"""

import requests
import dns.resolver
import ssl
import socket
from datetime import datetime
import json

class DomainMonitor:
    def __init__(self):
        self.domain = "enterprisescanner.com"
        self.subdomains = ['www', 'api', 'app', 'cdn', 'admin', 'mail', 'secure', 'beta', 'demo', 'support']
        self.monitoring_results = {}
        
    def check_dns_health(self):
        """Check DNS resolution for all domains"""
        dns_results = {}
        
        for subdomain in ['@'] + self.subdomains:
            domain_name = self.domain if subdomain == '@' else f"{subdomain}.{self.domain}"
            
            try:
                # A record check
                answers = dns.resolver.resolve(domain_name, 'A')
                dns_results[domain_name] = {
                    'status': 'healthy',
                    'ip_addresses': [str(answer) for answer in answers],
                    'response_time': '< 100ms'
                }
            except Exception as e:
                dns_results[domain_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                
        return dns_results
        
    def check_ssl_certificates(self):
        """Check SSL certificate status and expiration"""
        ssl_results = {}
        
        for subdomain in ['@'] + self.subdomains:
            domain_name = self.domain if subdomain == '@' else f"{subdomain}.{self.domain}"
            
            try:
                context = ssl.create_default_context()
                with socket.create_connection((domain_name, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain_name) as ssock:
                        cert = ssock.getpeercert()
                        
                ssl_results[domain_name] = {
                    'status': 'valid',
                    'issuer': cert.get('issuer', []),
                    'expires': cert.get('notAfter'),
                    'subject': cert.get('subject', [])
                }
            except Exception as e:
                ssl_results[domain_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                
        return ssl_results
        
    def check_website_health(self):
        """Check website accessibility and performance"""
        health_results = {}
        
        endpoints = [
            f'https://{self.domain}',
            f'https://www.{self.domain}',
            f'https://api.{self.domain}/health',
            f'https://app.{self.domain}'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                health_results[endpoint] = {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'status': 'healthy' if response.status_code == 200 else 'warning'
                }
            except Exception as e:
                health_results[endpoint] = {
                    'status': 'error',
                    'error': str(e)
                }
                
        return health_results
        
    def generate_monitoring_report(self):
        """Generate comprehensive monitoring report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'domain': self.domain,
            'dns_health': self.check_dns_health(),
            'ssl_certificates': self.check_ssl_certificates(),
            'website_health': self.check_website_health(),
            'overall_status': 'healthy'
        }
        
        # Determine overall status
        error_count = 0
        total_checks = 0
        
        for category in ['dns_health', 'ssl_certificates', 'website_health']:
            for item, status in report[category].items():
                total_checks += 1
                if status.get('status') == 'error':
                    error_count += 1
                    
        if error_count == 0:
            report['overall_status'] = 'healthy'
        elif error_count < total_checks * 0.25:
            report['overall_status'] = 'warning'
        else:
            report['overall_status'] = 'critical'
            
        return report
        
    def send_alert(self, report):
        """Send alerts for critical issues"""
        if report['overall_status'] in ['warning', 'critical']:
            # Email/Slack notification logic would go here
            print(f"ALERT: Domain status is {report['overall_status']}")
            
if __name__ == "__main__":
    monitor = DomainMonitor()
    report = monitor.generate_monitoring_report()
    
    print("Domain Monitoring Report")
    print("=" * 50)
    print(f"Overall Status: {report['overall_status'].upper()}")
    print(f"Timestamp: {report['timestamp']}")
    
    monitor.send_alert(report)
