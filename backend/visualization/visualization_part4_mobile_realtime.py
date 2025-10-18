"""
Military-Grade Advanced Visualization & Analytics - Part 4 of 4
===============================================================

Mobile-Responsive & Real-Time Dashboard System

Features:
- Mobile-first responsive design
- WebSocket real-time updates
- Progressive Web App (PWA) support
- Touch-optimized controls
- Offline capability

TECHNOLOGY:
- Responsive CSS Grid/Flexbox
- WebSocket for real-time data
- Service Workers for PWA
- Mobile gesture support
- Adaptive layouts
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json


class DeviceType(Enum):
    """Device types for responsive design"""
    MOBILE = "Mobile"
    TABLET = "Tablet"
    DESKTOP = "Desktop"
    LARGE_DISPLAY = "Large Display"


class UpdateFrequency(Enum):
    """Real-time update frequencies"""
    INSTANT = "Instant (WebSocket)"
    ONE_SECOND = "1 second"
    FIVE_SECONDS = "5 seconds"
    TEN_SECONDS = "10 seconds"
    THIRTY_SECONDS = "30 seconds"


class LayoutMode(Enum):
    """Dashboard layout modes"""
    COMPACT = "Compact (Mobile)"
    STANDARD = "Standard (Tablet)"
    EXPANDED = "Expanded (Desktop)"
    FULL_SCREEN = "Full Screen"


@dataclass
class ResponsiveBreakpoint:
    """Responsive design breakpoint"""
    name: str
    min_width: int
    max_width: Optional[int]
    columns: int
    widget_height: int


@dataclass
class WebSocketMessage:
    """WebSocket message"""
    message_id: str
    message_type: str
    timestamp: datetime
    data: Dict[str, Any]


@dataclass
class RealtimeWidget:
    """Real-time dashboard widget"""
    widget_id: str
    title: str
    update_frequency: UpdateFrequency
    data_stream: str
    last_update: datetime
    current_value: Any


@dataclass
class MobileDashboard:
    """Mobile-optimized dashboard"""
    dashboard_id: str
    name: str
    layout_mode: LayoutMode
    widgets: List[RealtimeWidget]
    supports_offline: bool
    pwa_enabled: bool


class MobileRealtimeEngine:
    """Mobile-Responsive Real-Time Dashboard Engine - Part 4"""
    
    def __init__(self):
        self.dashboards: Dict[str, MobileDashboard] = {}
        self.websocket_clients: List[Any] = []
        self.realtime_widgets: List[RealtimeWidget] = []
        self.breakpoints = self._define_breakpoints()
    
    def create_mobile_dashboard(self, name: str, 
                               device_type: DeviceType) -> MobileDashboard:
        """Create mobile-optimized dashboard"""
        print(f"📱 Creating mobile dashboard for {device_type.value}: {name}")
        
        # Select layout mode based on device
        layout_mode = self._select_layout_mode(device_type)
        
        dashboard = MobileDashboard(
            dashboard_id=f"MOBILE-DASH-{len(self.dashboards) + 1:04d}",
            name=name,
            layout_mode=layout_mode,
            widgets=[],
            supports_offline=True,
            pwa_enabled=True
        )
        
        # Add optimized widgets for device
        self._add_mobile_widgets(dashboard, device_type)
        
        self.dashboards[dashboard.dashboard_id] = dashboard
        
        print(f"✅ Mobile dashboard created: {dashboard.dashboard_id}")
        return dashboard
    
    def add_realtime_widget(self, dashboard_id: str, title: str,
                           data_stream: str,
                           update_frequency: UpdateFrequency) -> RealtimeWidget:
        """Add real-time widget to dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        widget = RealtimeWidget(
            widget_id=f"RT-WIDGET-{len(self.realtime_widgets) + 1:06d}",
            title=title,
            update_frequency=update_frequency,
            data_stream=data_stream,
            last_update=datetime.now(),
            current_value=None
        )
        
        dashboard.widgets.append(widget)
        self.realtime_widgets.append(widget)
        
        print(f"✅ Real-time widget added: {title}")
        return widget
    
    def broadcast_update(self, data_stream: str, value: Any):
        """Broadcast real-time update via WebSocket"""
        print(f"📡 Broadcasting update: {data_stream}")
        
        message = WebSocketMessage(
            message_id=f"MSG-{datetime.now().timestamp()}",
            message_type="data_update",
            timestamp=datetime.now(),
            data={
                "stream": data_stream,
                "value": value
            }
        )
        
        # Update affected widgets
        for widget in self.realtime_widgets:
            if widget.data_stream == data_stream:
                widget.current_value = value
                widget.last_update = datetime.now()
        
        # Simulate WebSocket broadcast
        self._simulate_websocket_broadcast(message)
        
        return message
    
    def generate_pwa_manifest(self, dashboard_id: str) -> Dict[str, Any]:
        """Generate PWA manifest for mobile installation"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return {"error": "Dashboard not found"}
        
        manifest = {
            "name": f"Enterprise Scanner - {dashboard.name}",
            "short_name": "EntScanner",
            "description": "Military-grade security dashboard",
            "start_url": f"/dashboard/{dashboard_id}",
            "display": "standalone",
            "background_color": "#1a1a2e",
            "theme_color": "#0f3460",
            "orientation": "portrait-primary",
            "icons": [
                {
                    "src": "/assets/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/assets/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ],
            "scope": "/",
            "categories": ["security", "monitoring"],
            "screenshots": [
                {
                    "src": "/assets/screenshot-mobile.png",
                    "sizes": "540x720",
                    "type": "image/png",
                    "form_factor": "narrow"
                }
            ]
        }
        
        print(f"✅ PWA manifest generated for: {dashboard.name}")
        return manifest
    
    def generate_service_worker(self) -> str:
        """Generate Service Worker for offline support"""
        service_worker = """
// Enterprise Scanner Service Worker
const CACHE_NAME = 'enterprise-scanner-v1';
const urlsToCache = [
  '/',
  '/css/mobile-dashboard.css',
  '/js/dashboard-core.js',
  '/assets/icon-192.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
});
"""
        print("✅ Service Worker generated")
        return service_worker
    
    def optimize_for_device(self, dashboard_id: str, 
                           device_type: DeviceType) -> Dict[str, Any]:
        """Optimize dashboard layout for device"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return {"error": "Dashboard not found"}
        
        # Select appropriate breakpoint
        breakpoint = self._get_breakpoint_for_device(device_type)
        
        # Optimize layout
        optimized_layout = {
            "columns": breakpoint.columns,
            "widget_height": breakpoint.widget_height,
            "widgets": []
        }
        
        # Arrange widgets in grid
        for i, widget in enumerate(dashboard.widgets):
            row = i // breakpoint.columns
            col = i % breakpoint.columns
            
            optimized_layout["widgets"].append({
                "widget_id": widget.widget_id,
                "position": {"row": row, "col": col},
                "size": {"width": 1, "height": 1}
            })
        
        print(f"✅ Layout optimized for {device_type.value}")
        return optimized_layout
    
    def enable_touch_gestures(self, dashboard_id: str) -> Dict[str, Any]:
        """Enable touch gesture support"""
        gestures = {
            "swipe_left": "Navigate to next dashboard",
            "swipe_right": "Navigate to previous dashboard",
            "pinch_zoom": "Zoom widget",
            "long_press": "Show widget options",
            "double_tap": "Full-screen widget"
        }
        
        print(f"✅ Touch gestures enabled for {dashboard_id}")
        return gestures
    
    def _define_breakpoints(self) -> List[ResponsiveBreakpoint]:
        """Define responsive design breakpoints"""
        return [
            ResponsiveBreakpoint(
                name="Mobile (Portrait)",
                min_width=0,
                max_width=480,
                columns=1,
                widget_height=200
            ),
            ResponsiveBreakpoint(
                name="Mobile (Landscape)",
                min_width=481,
                max_width=768,
                columns=2,
                widget_height=180
            ),
            ResponsiveBreakpoint(
                name="Tablet",
                min_width=769,
                max_width=1024,
                columns=3,
                widget_height=220
            ),
            ResponsiveBreakpoint(
                name="Desktop",
                min_width=1025,
                max_width=1920,
                columns=4,
                widget_height=250
            ),
            ResponsiveBreakpoint(
                name="Large Display",
                min_width=1921,
                max_width=None,
                columns=6,
                widget_height=300
            )
        ]
    
    def _select_layout_mode(self, device_type: DeviceType) -> LayoutMode:
        """Select layout mode for device"""
        layout_map = {
            DeviceType.MOBILE: LayoutMode.COMPACT,
            DeviceType.TABLET: LayoutMode.STANDARD,
            DeviceType.DESKTOP: LayoutMode.EXPANDED,
            DeviceType.LARGE_DISPLAY: LayoutMode.FULL_SCREEN
        }
        return layout_map.get(device_type, LayoutMode.STANDARD)
    
    def _add_mobile_widgets(self, dashboard: MobileDashboard, 
                           device_type: DeviceType):
        """Add optimized widgets for mobile device"""
        # Mobile gets fewer, more critical widgets
        if device_type == DeviceType.MOBILE:
            critical_widgets = [
                ("Security Alerts", "/stream/alerts", UpdateFrequency.INSTANT),
                ("Active Incidents", "/stream/incidents", UpdateFrequency.FIVE_SECONDS),
                ("System Status", "/stream/status", UpdateFrequency.TEN_SECONDS)
            ]
        else:
            critical_widgets = [
                ("Security Alerts", "/stream/alerts", UpdateFrequency.INSTANT),
                ("Active Incidents", "/stream/incidents", UpdateFrequency.FIVE_SECONDS),
                ("Vulnerability Scan", "/stream/vulns", UpdateFrequency.THIRTY_SECONDS),
                ("Threat Feed", "/stream/threats", UpdateFrequency.TEN_SECONDS),
                ("System Status", "/stream/status", UpdateFrequency.TEN_SECONDS),
                ("Compliance Score", "/stream/compliance", UpdateFrequency.THIRTY_SECONDS)
            ]
        
        for title, stream, frequency in critical_widgets:
            self.add_realtime_widget(dashboard.dashboard_id, title, stream, frequency)
    
    def _get_breakpoint_for_device(self, device_type: DeviceType) -> ResponsiveBreakpoint:
        """Get breakpoint configuration for device"""
        device_width_map = {
            DeviceType.MOBILE: 375,
            DeviceType.TABLET: 768,
            DeviceType.DESKTOP: 1440,
            DeviceType.LARGE_DISPLAY: 2560
        }
        
        width = device_width_map[device_type]
        
        for breakpoint in self.breakpoints:
            if breakpoint.min_width <= width:
                if breakpoint.max_width is None or width <= breakpoint.max_width:
                    return breakpoint
        
        return self.breakpoints[0]
    
    def _simulate_websocket_broadcast(self, message: WebSocketMessage):
        """Simulate WebSocket broadcast (in production, use actual WebSocket)"""
        # In production:
        # for client in self.websocket_clients:
        #     await client.send(json.dumps(message.__dict__))
        pass


def main():
    """Test mobile real-time dashboard engine"""
    engine = MobileRealtimeEngine()
    
    # Create mobile dashboard
    mobile_dash = engine.create_mobile_dashboard("SOC Mobile", DeviceType.MOBILE)
    print(f"Mobile Dashboard: {mobile_dash.dashboard_id}")
    print(f"Layout Mode: {mobile_dash.layout_mode.value}")
    print(f"Widgets: {len(mobile_dash.widgets)}")
    
    # Broadcast real-time update
    engine.broadcast_update("/stream/alerts", {"severity": "HIGH", "count": 3})
    
    # Generate PWA manifest
    manifest = engine.generate_pwa_manifest(mobile_dash.dashboard_id)
    print(f"PWA Manifest: {manifest['name']}")
    
    # Generate Service Worker
    sw = engine.generate_service_worker()
    print(f"Service Worker: {len(sw)} chars")
    
    # Optimize for tablet
    layout = engine.optimize_for_device(mobile_dash.dashboard_id, DeviceType.TABLET)
    print(f"Optimized Layout: {layout['columns']} columns")
    
    # Enable touch gestures
    gestures = engine.enable_touch_gestures(mobile_dash.dashboard_id)
    print(f"Touch Gestures: {len(gestures)} enabled")


if __name__ == "__main__":
    main()
