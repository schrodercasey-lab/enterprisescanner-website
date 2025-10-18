#!/usr/bin/env python3
"""
Test Report Generator - Professional Reports for Jupiter Integration

Generates comprehensive test reports in multiple formats (JSON, Markdown, HTML)
to provide clear, actionable feedback on Jupiter integration results.

Features:
- Multiple output formats (JSON, Markdown, HTML, Plain Text)
- Performance metrics and statistics
- Clear pass/fail indicators
- Actionable recommendations
- Professional formatting

Author: Enterprise Scanner Platform
Date: October 18, 2025
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

from modules.jupiter_integration_hub import IntegrationResult, ProcessingStatus


class ReportFormat(Enum):
    """Supported report formats"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"


class TestReportGenerator:
    """
    Generates professional test reports for Jupiter integration results.
    
    Example:
        from modules.test_report_generator import TestReportGenerator
        from modules.jupiter_integration_hub import process_jupiter_scan
        
        result = process_jupiter_scan("scan.json")
        
        generator = TestReportGenerator()
        generator.generate_report(result, "report.html", ReportFormat.HTML)
    """
    
    def __init__(self):
        """Initialize test report generator"""
        pass
    
    def generate_report(
        self,
        result: IntegrationResult,
        output_file: str,
        format: ReportFormat = ReportFormat.HTML
    ) -> str:
        """
        Generate a test report in the specified format.
        
        Args:
            result: Integration result to report on
            output_file: Path to output file
            format: Report format
        
        Returns:
            Path to generated report file
        """
        if format == ReportFormat.JSON:
            content = self._generate_json_report(result)
        elif format == ReportFormat.MARKDOWN:
            content = self._generate_markdown_report(result)
        elif format == ReportFormat.HTML:
            content = self._generate_html_report(result)
        else:  # TEXT
            content = self._generate_text_report(result)
        
        # Write to file
        Path(output_file).write_text(content, encoding='utf-8')
        return output_file
    
    def _generate_json_report(self, result: IntegrationResult) -> str:
        """Generate JSON format report"""
        report = {
            'test_report': {
                'generated_at': datetime.now().isoformat(),
                'status': result.status.value,
                'summary': {
                    'target': result.scan_data.get('target'),
                    'total_vulnerabilities': result.metrics.total_vulnerabilities,
                    'processing_time': result.metrics.processing_time,
                    'success_rate': result.metrics.calculate_success_rate()
                },
                'modules': {
                    'script_generator': {
                        'scripts_generated': result.metrics.scripts_generated,
                        'scripts_failed': result.metrics.scripts_failed,
                        'success_rate': self._calculate_module_success_rate(
                            result.metrics.scripts_generated,
                            result.metrics.scripts_failed
                        )
                    },
                    'config_generator': {
                        'configs_generated': result.metrics.configs_generated,
                        'configs_failed': result.metrics.configs_failed,
                        'success_rate': self._calculate_module_success_rate(
                            result.metrics.configs_generated,
                            result.metrics.configs_failed
                        )
                    },
                    'proactive_monitor': {
                        'monitoring_active': result.metrics.monitoring_active,
                        'alerts_generated': result.metrics.alerts_generated
                    }
                },
                'performance': {
                    'processing_time_seconds': result.metrics.processing_time,
                    'vulnerabilities_per_second': result.metrics.vulnerabilities_per_second
                },
                'issues': {
                    'errors': result.errors,
                    'warnings': result.warnings
                },
                'outputs': {
                    'scripts_directory': f"{result.output_directory}/scripts" if result.remediation_scripts else None,
                    'configs_directory': f"{result.output_directory}/configs" if result.security_configs else None,
                    'monitoring_session': result.monitoring_session.session_id if result.monitoring_session else None
                }
            }
        }
        return json.dumps(report, indent=2)
    
    def _generate_markdown_report(self, result: IntegrationResult) -> str:
        """Generate Markdown format report"""
        lines = []
        
        # Header
        lines.append("# Jupiter Integration Test Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Status:** {self._get_status_badge_md(result.status)}")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Target System:** {result.scan_data.get('target', 'Unknown')}")
        lines.append(f"- **Vulnerabilities Processed:** {result.metrics.total_vulnerabilities}")
        lines.append(f"- **Processing Time:** {result.metrics.processing_time:.2f} seconds")
        lines.append(f"- **Throughput:** {result.metrics.vulnerabilities_per_second:.2f} vulnerabilities/second")
        lines.append(f"- **Success Rate:** {result.metrics.calculate_success_rate():.1f}%")
        lines.append("")
        
        # Module Results
        lines.append("## Module Performance")
        lines.append("")
        
        # Script Generator
        lines.append("### 🔧 Script Generator")
        lines.append("")
        lines.append(f"- **Scripts Generated:** {result.metrics.scripts_generated}")
        lines.append(f"- **Scripts Failed:** {result.metrics.scripts_failed}")
        script_success = self._calculate_module_success_rate(
            result.metrics.scripts_generated,
            result.metrics.scripts_failed
        )
        lines.append(f"- **Success Rate:** {script_success:.1f}%")
        if result.remediation_scripts:
            lines.append(f"- **Output Directory:** `{result.output_directory}/scripts/`")
        lines.append("")
        
        # Config Generator
        lines.append("### 🔒 Config Generator")
        lines.append("")
        lines.append(f"- **Configs Generated:** {result.metrics.configs_generated}")
        lines.append(f"- **Configs Failed:** {result.metrics.configs_failed}")
        config_success = self._calculate_module_success_rate(
            result.metrics.configs_generated,
            result.metrics.configs_failed
        )
        lines.append(f"- **Success Rate:** {config_success:.1f}%")
        if result.security_configs:
            lines.append(f"- **Output Directory:** `{result.output_directory}/configs/`")
        lines.append("")
        
        # Proactive Monitor
        lines.append("### 📡 Proactive Monitor")
        lines.append("")
        if result.monitoring_session:
            lines.append(f"- **Status:** ✅ Active")
            lines.append(f"- **Session ID:** `{result.monitoring_session.session_id}`")
            lines.append(f"- **Alert Rules:** {len(result.monitoring_session.active_rules)}")
            lines.append(f"- **Alerts Generated:** {result.metrics.alerts_generated}")
        else:
            lines.append(f"- **Status:** ⚠️ Not Active")
        lines.append("")
        
        # Issues
        if result.errors or result.warnings:
            lines.append("## Issues")
            lines.append("")
            
            if result.errors:
                lines.append(f"### ❌ Errors ({len(result.errors)})")
                lines.append("")
                for error in result.errors:
                    lines.append(f"- {error}")
                lines.append("")
            
            if result.warnings:
                lines.append(f"### ⚠️ Warnings ({len(result.warnings)})")
                lines.append("")
                for warning in result.warnings[:10]:  # Limit to 10
                    lines.append(f"- {warning}")
                if len(result.warnings) > 10:
                    lines.append(f"- ... and {len(result.warnings) - 10} more warnings")
                lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        recommendations = self._generate_recommendations(result)
        for rec in recommendations:
            lines.append(f"- {rec}")
        lines.append("")
        
        # Next Steps
        lines.append("## Next Steps")
        lines.append("")
        lines.append("1. Review generated scripts and configurations")
        lines.append(f"2. Test remediation scripts in development environment")
        lines.append(f"3. Apply configurations during maintenance window")
        lines.append(f"4. Monitor alerts and system behavior")
        lines.append(f"5. Run follow-up vulnerability scan to verify fixes")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, result: IntegrationResult) -> str:
        """Generate HTML format report"""
        status_color = {
            ProcessingStatus.SUCCESS: '#28a745',
            ProcessingStatus.PARTIAL: '#ffc107',
            ProcessingStatus.FAILED: '#dc3545',
            ProcessingStatus.WARNING: '#ffc107'
        }
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jupiter Integration Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            background-color: {status_color.get(result.status, '#6c757d')};
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .metric-label {{
            font-weight: 600;
            color: #555;
        }}
        .metric-value {{
            color: #2c3e50;
            font-weight: bold;
        }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .info {{ color: #17a2b8; }}
        .module-section {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .alert {{
            padding: 12px 20px;
            margin: 10px 0;
            border-radius: 4px;
            border-left: 4px solid;
        }}
        .alert-error {{
            background: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }}
        .alert-warning {{
            background: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }}
        .recommendation {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 4px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Jupiter Integration Test Report</h1>
        
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Status:</strong> <span class="status-badge">{result.status.value.upper()}</span></p>
        
        <h2>📊 Executive Summary</h2>
        <div class="metric">
            <span class="metric-label">Target System</span>
            <span class="metric-value">{result.scan_data.get('target', 'Unknown')}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Vulnerabilities Processed</span>
            <span class="metric-value">{result.metrics.total_vulnerabilities}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Processing Time</span>
            <span class="metric-value">{result.metrics.processing_time:.2f} seconds</span>
        </div>
        <div class="metric">
            <span class="metric-label">Throughput</span>
            <span class="metric-value">{result.metrics.vulnerabilities_per_second:.2f} vulnerabilities/second</span>
        </div>
        <div class="metric">
            <span class="metric-label">Success Rate</span>
            <span class="metric-value {'success' if result.metrics.calculate_success_rate() >= 90 else 'warning'}">{result.metrics.calculate_success_rate():.1f}%</span>
        </div>
        
        <h2>🔧 Module Performance</h2>
        
        <div class="module-section">
            <h3>🔧 Script Generator</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Scripts Generated</td>
                    <td class="success">{result.metrics.scripts_generated}</td>
                </tr>
                <tr>
                    <td>Scripts Failed</td>
                    <td class="{'error' if result.metrics.scripts_failed > 0 else ''}">{result.metrics.scripts_failed}</td>
                </tr>
                <tr>
                    <td>Success Rate</td>
                    <td>{self._calculate_module_success_rate(result.metrics.scripts_generated, result.metrics.scripts_failed):.1f}%</td>
                </tr>
            </table>
            {f'<p><strong>Output:</strong> <code>{result.output_directory}/scripts/</code></p>' if result.remediation_scripts else ''}
        </div>
        
        <div class="module-section">
            <h3>🔒 Config Generator</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Configs Generated</td>
                    <td class="success">{result.metrics.configs_generated}</td>
                </tr>
                <tr>
                    <td>Configs Failed</td>
                    <td class="{'error' if result.metrics.configs_failed > 0 else ''}">{result.metrics.configs_failed}</td>
                </tr>
                <tr>
                    <td>Success Rate</td>
                    <td>{self._calculate_module_success_rate(result.metrics.configs_generated, result.metrics.configs_failed):.1f}%</td>
                </tr>
            </table>
            {f'<p><strong>Output:</strong> <code>{result.output_directory}/configs/</code></p>' if result.security_configs else ''}
        </div>
        
        <div class="module-section">
            <h3>📡 Proactive Monitor</h3>
            {self._generate_monitoring_html(result)}
        </div>
"""
        
        # Add issues section
        if result.errors or result.warnings:
            html += """
        <h2>⚠️ Issues</h2>
"""
            
            if result.errors:
                html += f"""
        <h3>❌ Errors ({len(result.errors)})</h3>
"""
                for error in result.errors:
                    html += f"""
        <div class="alert alert-error">{error}</div>
"""
            
            if result.warnings:
                html += f"""
        <h3>⚠️ Warnings ({len(result.warnings[:10])})</h3>
"""
                for warning in result.warnings[:10]:
                    html += f"""
        <div class="alert alert-warning">{warning}</div>
"""
                if len(result.warnings) > 10:
                    html += f"""
        <div class="alert alert-warning">... and {len(result.warnings) - 10} more warnings</div>
"""
        
        # Add recommendations
        recommendations = self._generate_recommendations(result)
        html += """
        <h2>💡 Recommendations</h2>
"""
        for rec in recommendations:
            html += f"""
        <div class="recommendation">{rec}</div>
"""
        
        # Add next steps
        html += """
        <h2>📋 Next Steps</h2>
        <ol>
            <li>Review generated scripts and configurations</li>
            <li>Test remediation scripts in development environment</li>
            <li>Apply configurations during maintenance window</li>
            <li>Monitor alerts and system behavior</li>
            <li>Run follow-up vulnerability scan to verify fixes</li>
        </ol>
        
        <div class="footer">
            <p>Enterprise Scanner Platform - Phase 3 Jupiter Integration</p>
            <p>Report generated by Test Report Generator v1.0.0</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_text_report(self, result: IntegrationResult) -> str:
        """Generate plain text format report"""
        return result.get_summary()
    
    def _generate_monitoring_html(self, result: IntegrationResult) -> str:
        """Generate monitoring section HTML"""
        if result.monitoring_session:
            return f"""
            <p><strong>Status:</strong> <span class="success">✅ Active</span></p>
            <p><strong>Session ID:</strong> <code>{result.monitoring_session.session_id}</code></p>
            <p><strong>Alert Rules:</strong> {len(result.monitoring_session.active_rules)}</p>
            <p><strong>Alerts Generated:</strong> {result.metrics.alerts_generated}</p>
"""
        else:
            return """
            <p><strong>Status:</strong> <span class="warning">⚠️ Not Active</span></p>
"""
    
    def _get_status_badge_md(self, status: ProcessingStatus) -> str:
        """Get markdown status badge"""
        badges = {
            ProcessingStatus.SUCCESS: "![SUCCESS](https://img.shields.io/badge/STATUS-SUCCESS-brightgreen)",
            ProcessingStatus.PARTIAL: "![PARTIAL](https://img.shields.io/badge/STATUS-PARTIAL-yellow)",
            ProcessingStatus.FAILED: "![FAILED](https://img.shields.io/badge/STATUS-FAILED-red)",
            ProcessingStatus.WARNING: "![WARNING](https://img.shields.io/badge/STATUS-WARNING-yellow)"
        }
        return badges.get(status, status.value.upper())
    
    def _calculate_module_success_rate(self, succeeded: int, failed: int) -> float:
        """Calculate success rate for a module"""
        total = succeeded + failed
        if total == 0:
            return 100.0
        return (succeeded / total) * 100.0
    
    def _generate_recommendations(self, result: IntegrationResult) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on errors
        if result.metrics.scripts_failed > 0:
            recommendations.append(
                f"Review {result.metrics.scripts_failed} failed script generation(s) - check vulnerability mapping"
            )
        
        if result.metrics.configs_failed > 0:
            recommendations.append(
                f"Review {result.metrics.configs_failed} failed config generation(s) - verify vulnerability IDs"
            )
        
        # Based on warnings
        if len(result.warnings) > 10:
            recommendations.append(
                f"High number of warnings ({len(result.warnings)}) - review safety checks"
            )
        
        # Based on success rate
        success_rate = result.metrics.calculate_success_rate()
        if success_rate < 80:
            recommendations.append(
                f"Success rate below 80% ({success_rate:.1f}%) - investigate common failure patterns"
            )
        
        # Based on monitoring
        if not result.metrics.monitoring_active:
            recommendations.append(
                "Enable proactive monitoring for real-time vulnerability tracking"
            )
        
        # Based on performance
        if result.metrics.vulnerabilities_per_second < 1.0:
            recommendations.append(
                f"Performance below 1 vuln/sec ({result.metrics.vulnerabilities_per_second:.2f}) - consider optimization"
            )
        
        # Default recommendations
        if not recommendations:
            recommendations.extend([
                "All systems functioning optimally",
                "Continue with deployment procedures",
                "Schedule follow-up vulnerability scan in 30 days"
            ])
        
        return recommendations


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST REPORT GENERATOR - Example Usage")
    print("="*70 + "\n")
    
    print("from modules.test_report_generator import TestReportGenerator, ReportFormat")
    print("from modules.jupiter_integration_hub import process_jupiter_scan")
    print("")
    print('result = process_jupiter_scan("jupiter_scan.json")')
    print("")
    print("generator = TestReportGenerator()")
    print('generator.generate_report(result, "report.html", ReportFormat.HTML)')
    print('generator.generate_report(result, "report.md", ReportFormat.MARKDOWN)')
    print('generator.generate_report(result, "report.json", ReportFormat.JSON)')
    
    print("\n" + "="*70)
    print("Ready to generate professional test reports! 📊")
    print("="*70 + "\n")
