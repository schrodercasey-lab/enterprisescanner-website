"""
Military-Grade Advanced Visualization & Analytics - Part 1 of 4
===============================================================

Interactive Security Dashboards

Features:
- Real-time security dashboards
- Customizable widgets
- Drill-down analytics
- KPI tracking
- Responsive design

TECHNOLOGY:
- React/Vue.js framework support
- D3.js for advanced visualizations
- WebSocket for real-time updates
- REST API integration
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json


class DashboardType(Enum):
    """Dashboard types"""
    EXECUTIVE = "Executive Overview"
    SOC_OPERATIONS = "SOC Operations"
    THREAT_INTELLIGENCE = "Threat Intelligence"
    COMPLIANCE = "Compliance Monitoring"
    INCIDENT_RESPONSE = "Incident Response"
    VULNERABILITY_MANAGEMENT = "Vulnerability Management"


class WidgetType(Enum):
    """Dashboard widget types"""
    LINE_CHART = "Line Chart"
    BAR_CHART = "Bar Chart"
    PIE_CHART = "Pie Chart"
    HEATMAP = "Heatmap"
    GAUGE = "Gauge"
    TABLE = "Data Table"
    METRIC = "Single Metric"
    TIMELINE = "Timeline"


class RefreshInterval(Enum):
    """Data refresh intervals"""
    REAL_TIME = "Real-time (WebSocket)"
    FIVE_SECONDS = "5 seconds"
    THIRTY_SECONDS = "30 seconds"
    ONE_MINUTE = "1 minute"
    FIVE_MINUTES = "5 minutes"


@dataclass
class Widget:
    """Dashboard widget"""
    widget_id: str
    widget_type: WidgetType
    title: str
    data_source: str
    refresh_interval: RefreshInterval
    position: Dict[str, int]  # x, y, width, height
    config: Dict[str, Any]


@dataclass
class Dashboard:
    """Security dashboard"""
    dashboard_id: str
    dashboard_type: DashboardType
    name: str
    widgets: List[Widget]
    created_by: str
    is_public: bool
    last_updated: datetime


@dataclass
class KPI:
    """Key Performance Indicator"""
    kpi_id: str
    name: str
    current_value: float
    target_value: float
    unit: str
    trend: str  # "up", "down", "stable"


class InteractiveDashboardEngine:
    """Interactive Dashboard Engine - Part 1"""
    
    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
        self.kpis: List[KPI] = []
        self._initialize_default_kpis()
    
    def create_dashboard(self, dashboard_type: DashboardType, name: str,
                        created_by: str) -> Dashboard:
        """Create new interactive dashboard"""
        print(f"📊 Creating dashboard: {name}")
        
        dashboard = Dashboard(
            dashboard_id=f"DASH-{len(self.dashboards) + 1:04d}",
            dashboard_type=dashboard_type,
            name=name,
            widgets=[],
            created_by=created_by,
            is_public=False,
            last_updated=datetime.now()
        )
        
        # Add default widgets based on type
        self._add_default_widgets(dashboard)
        
        self.dashboards[dashboard.dashboard_id] = dashboard
        
        print(f"✅ Dashboard created: {dashboard.dashboard_id} ({len(dashboard.widgets)} widgets)")
        return dashboard
    
    def add_widget(self, dashboard_id: str, widget_type: WidgetType,
                   title: str, data_source: str) -> Widget:
        """Add widget to dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        widget = Widget(
            widget_id=f"WIDGET-{len(dashboard.widgets) + 1:04d}",
            widget_type=widget_type,
            title=title,
            data_source=data_source,
            refresh_interval=RefreshInterval.ONE_MINUTE,
            position=self._calculate_next_position(dashboard),
            config=self._get_default_widget_config(widget_type)
        )
        
        dashboard.widgets.append(widget)
        dashboard.last_updated = datetime.now()
        
        print(f"✅ Widget added: {widget.title}")
        return widget
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return {"error": "Dashboard not found"}
        
        widget_data = {}
        for widget in dashboard.widgets:
            widget_data[widget.widget_id] = self._fetch_widget_data(widget)
        
        return {
            "dashboard_id": dashboard.dashboard_id,
            "name": dashboard.name,
            "type": dashboard.dashboard_type.value,
            "last_updated": dashboard.last_updated.isoformat(),
            "widgets": widget_data
        }
    
    def generate_executive_dashboard(self) -> Dashboard:
        """Generate executive overview dashboard"""
        print("📊 Generating Executive Dashboard...")
        
        dashboard = self.create_dashboard(
            dashboard_type=DashboardType.EXECUTIVE,
            name="Executive Security Overview",
            created_by="System"
        )
        
        # Add executive KPI widgets
        self.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.GAUGE,
            title="Security Posture Score",
            data_source="/api/security/posture"
        )
        
        self.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.LINE_CHART,
            title="Incident Trend (30 Days)",
            data_source="/api/incidents/trend"
        )
        
        self.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.METRIC,
            title="Critical Vulnerabilities",
            data_source="/api/vulnerabilities/critical/count"
        )
        
        print(f"✅ Executive Dashboard created with {len(dashboard.widgets)} widgets")
        return dashboard
    
    def generate_soc_dashboard(self) -> Dashboard:
        """Generate SOC operations dashboard"""
        print("📊 Generating SOC Operations Dashboard...")
        
        dashboard = self.create_dashboard(
            dashboard_type=DashboardType.SOC_OPERATIONS,
            name="SOC Real-time Operations",
            created_by="System"
        )
        
        # Add SOC-specific widgets
        self.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.HEATMAP,
            title="Alert Heatmap (24h)",
            data_source="/api/alerts/heatmap"
        )
        
        self.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.TABLE,
            title="Top Security Events",
            data_source="/api/events/top"
        )
        
        self.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.PIE_CHART,
            title="Alert Distribution by Severity",
            data_source="/api/alerts/by-severity"
        )
        
        print(f"✅ SOC Dashboard created with {len(dashboard.widgets)} widgets")
        return dashboard
    
    def track_kpis(self) -> List[KPI]:
        """Track security KPIs"""
        print("📈 Tracking Security KPIs...")
        
        # Update KPI values (simulated)
        for kpi in self.kpis:
            kpi.current_value = self._simulate_kpi_value(kpi)
            kpi.trend = self._calculate_trend(kpi)
        
        return self.kpis
    
    def _initialize_default_kpis(self):
        """Initialize default security KPIs"""
        self.kpis = [
            KPI(
                kpi_id="KPI-001",
                name="Mean Time to Detect (MTTD)",
                current_value=4.2,
                target_value=2.0,
                unit="hours",
                trend="down"
            ),
            KPI(
                kpi_id="KPI-002",
                name="Mean Time to Respond (MTTR)",
                current_value=8.5,
                target_value=6.0,
                unit="hours",
                trend="down"
            ),
            KPI(
                kpi_id="KPI-003",
                name="Security Posture Score",
                current_value=87.0,
                target_value=95.0,
                unit="percentage",
                trend="up"
            ),
            KPI(
                kpi_id="KPI-004",
                name="Patch Compliance Rate",
                current_value=92.0,
                target_value=98.0,
                unit="percentage",
                trend="stable"
            )
        ]
    
    def _add_default_widgets(self, dashboard: Dashboard):
        """Add default widgets based on dashboard type"""
        if dashboard.dashboard_type == DashboardType.EXECUTIVE:
            # Executive dashboards get high-level metrics
            pass  # Will be added via generate_executive_dashboard
        elif dashboard.dashboard_type == DashboardType.SOC_OPERATIONS:
            # SOC dashboards get real-time operational data
            pass  # Will be added via generate_soc_dashboard
    
    def _calculate_next_position(self, dashboard: Dashboard) -> Dict[str, int]:
        """Calculate next widget position"""
        # Simple grid layout: 4 columns, auto-increment rows
        widget_count = len(dashboard.widgets)
        col = widget_count % 4
        row = widget_count // 4
        
        return {
            "x": col * 25,
            "y": row * 25,
            "width": 25,
            "height": 25
        }
    
    def _get_default_widget_config(self, widget_type: WidgetType) -> Dict[str, Any]:
        """Get default configuration for widget type"""
        configs = {
            WidgetType.LINE_CHART: {
                "x_axis": "timestamp",
                "y_axis": "value",
                "color": "#3498db"
            },
            WidgetType.GAUGE: {
                "min": 0,
                "max": 100,
                "thresholds": [50, 75, 90]
            },
            WidgetType.HEATMAP: {
                "color_scheme": "RdYlGn",
                "cell_size": 10
            }
        }
        return configs.get(widget_type, {})
    
    def _fetch_widget_data(self, widget: Widget) -> Dict[str, Any]:
        """Fetch real-time data for widget (simulated)"""
        # In production, this would call actual data sources
        if widget.widget_type == WidgetType.GAUGE:
            return {
                "value": 87.0,
                "min": 0,
                "max": 100,
                "status": "good"
            }
        elif widget.widget_type == WidgetType.METRIC:
            return {
                "value": 5,
                "change": -2,
                "change_percentage": -28.5
            }
        elif widget.widget_type == WidgetType.LINE_CHART:
            return {
                "data": [
                    {"timestamp": "2024-01-01", "value": 45},
                    {"timestamp": "2024-01-02", "value": 52},
                    {"timestamp": "2024-01-03", "value": 38}
                ]
            }
        else:
            return {"data": []}
    
    def _simulate_kpi_value(self, kpi: KPI) -> float:
        """Simulate KPI value (in production, fetch from data source)"""
        import random
        # Simulate slight variation
        variance = kpi.current_value * 0.05
        return kpi.current_value + random.uniform(-variance, variance)
    
    def _calculate_trend(self, kpi: KPI) -> str:
        """Calculate KPI trend"""
        if kpi.current_value > kpi.target_value * 1.05:
            return "up"
        elif kpi.current_value < kpi.target_value * 0.95:
            return "down"
        else:
            return "stable"


def main():
    """Test interactive dashboard engine"""
    engine = InteractiveDashboardEngine()
    
    # Generate executive dashboard
    exec_dash = engine.generate_executive_dashboard()
    print(f"Executive Dashboard: {exec_dash.dashboard_id}")
    
    # Generate SOC dashboard
    soc_dash = engine.generate_soc_dashboard()
    print(f"SOC Dashboard: {soc_dash.dashboard_id}")
    
    # Get dashboard data
    data = engine.get_dashboard_data(exec_dash.dashboard_id)
    print(f"Widgets in Executive Dashboard: {len(data['widgets'])}")
    
    # Track KPIs
    kpis = engine.track_kpis()
    print(f"Security KPIs tracked: {len(kpis)}")
    for kpi in kpis:
        print(f"  {kpi.name}: {kpi.current_value:.1f} {kpi.unit} (Target: {kpi.target_value:.1f})")


if __name__ == "__main__":
    main()
