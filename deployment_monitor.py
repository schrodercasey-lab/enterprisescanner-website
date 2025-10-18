#!/usr/bin/env python3
"""
Deployment Progress Monitor
Monitor deployment progress in real-time
"""

import time
import requests
import threading
from datetime import datetime

class DeploymentMonitor:
    def __init__(self):
        self.domain = "enterprisescanner.com"
        self.server_ip = "134.199.147.45"
        self.monitoring = False
        self.start_time = None
        
    def start_monitoring(self):
        """Start monitoring deployment progress"""
        self.monitoring = True
        self.start_time = datetime.now()
        
        print("🔍 Deployment Monitor Started")
        print("=" * 50)
        print(f"📅 Start time: {self.start_time.strftime('%H:%M:%S')}")
        print(f"🎯 Target: {self.domain}")
        print(f"🖥️  Server: {self.server_ip}")
        print("")
        
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            while self.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        check_count = 0
        last_status = None
        
        while self.monitoring:
            check_count += 1
            elapsed = datetime.now() - self.start_time
            
            # Check website status
            try:
                response = requests.get(f"http://{self.domain}", timeout=5)
                content_size = len(response.content)
                
                if content_size > 30000:
                    status = f"✅ DEPLOYED ({content_size:,} bytes)"
                    if status != last_status:
                        print(f"\r[{elapsed.total_seconds():.0f}s] {status}")
                        self.stop_monitoring()
                        return
                else:
                    status = f"⏳ PENDING ({content_size} bytes)"
                    
            except Exception as e:
                status = f"🔄 CHECKING... ({str(e)[:30]})"
                
            # Update display
            if check_count % 5 == 0 or status != last_status:
                timer_display = f"{int(elapsed.total_seconds()//60):02d}:{int(elapsed.total_seconds()%60):02d}"
                print(f"\r[{timer_display}] Check #{check_count}: {status}", end="", flush=True)
                
            last_status = status
            time.sleep(2)
            
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            print(f"\n🏁 Monitoring stopped after {elapsed.total_seconds():.1f} seconds")

if __name__ == "__main__":
    monitor = DeploymentMonitor()
    print("🔍 Starting deployment monitoring...")
    print("📋 This will check your website every 2 seconds")
    print("⏹️  Press Ctrl+C to stop monitoring")
    print("")
    monitor.start_monitoring()
