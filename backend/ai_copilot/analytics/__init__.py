"""
Jupiter Analytics Module

Business intelligence and ROI tracking for demonstrating value.

Components:
- UsageTracker: Query and feature usage analytics
- ROICalculator: Return on investment calculations
- DashboardAPI: REST endpoints for analytics dashboard

Author: Enterprise Scanner Team
Version: 2.0.0
Date: October 17, 2025
"""

from .usage_tracker import JupiterUsageTracker
from .roi_calculator import JupiterROICalculator

__all__ = [
    'JupiterUsageTracker',
    'JupiterROICalculator',
]
