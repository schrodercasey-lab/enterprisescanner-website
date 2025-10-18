"""
Advanced Port Scanner Module
Enterprise-grade port scanning with service detection, OS fingerprinting, and banner grabbing
"""

import socket
import asyncio
import concurrent.futures
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class PortScanResult:
    """Result from scanning a single port"""
    port: int
    status: str  # 'open', 'closed', 'filtered'
    service: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None
    protocol: str = 'tcp'


@dataclass
class HostScanResult:
    """Complete scan results for a host"""
    hostname: str
    ip_address: str
    scan_start: datetime
    scan_end: datetime
    open_ports: List[PortScanResult]
    os_guess: Optional[str] = None
    total_ports_scanned: int = 0
    scan_duration_seconds: float = 0.0


class AdvancedPortScanner:
    """
    Advanced port scanning with async capabilities for Fortune 500 enterprises
    
    Features:
    - Full port range scanning (1-65535)
    - Async scanning for speed
    - Service version detection
    - Banner grabbing
    - OS fingerprinting
    - Configurable scan profiles
    """
    
    # Common ports and their typical services
    COMMON_PORTS = {
        20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
        25: 'SMTP', 53: 'DNS', 67: 'DHCP', 68: 'DHCP',
        80: 'HTTP', 110: 'POP3', 123: 'NTP', 137: 'NetBIOS',
        138: 'NetBIOS', 139: 'NetBIOS', 143: 'IMAP', 161: 'SNMP',
        162: 'SNMP', 389: 'LDAP', 443: 'HTTPS', 445: 'SMB',
        465: 'SMTPS', 514: 'Syslog', 587: 'SMTP', 636: 'LDAPS',
        993: 'IMAPS', 995: 'POP3S', 1433: 'MS-SQL', 1521: 'Oracle',
        3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC',
        6379: 'Redis', 8080: 'HTTP-Proxy', 8443: 'HTTPS-Alt',
        9090: 'Prometheus', 27017: 'MongoDB', 50000: 'DB2'
    }
    
    # Scan profiles for different use cases
    SCAN_PROFILES = {
        'quick': {
            'ports': [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080],
            'timeout': 0.5,
            'max_workers': 50
        },
        'standard': {
            'ports': list(COMMON_PORTS.keys()),
            'timeout': 1.0,
            'max_workers': 100
        },
        'deep': {
            'ports': range(1, 65536),  # All ports
            'timeout': 2.0,
            'max_workers': 200
        },
        'custom': {
            'ports': [],  # Will be set dynamically
            'timeout': 1.0,
            'max_workers': 100
        }
    }
    
    def __init__(self, timeout: float = 1.0, max_workers: int = 100):
        """
        Initialize the advanced port scanner
        
        Args:
            timeout: Socket connection timeout in seconds
            max_workers: Maximum concurrent scanning threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.scan_results = {}
        
    async def scan_host_async(
        self, 
        hostname: str, 
        profile: str = 'standard',
        custom_ports: Optional[List[int]] = None
    ) -> HostScanResult:
        """
        Asynchronously scan a host using the specified profile
        
        Args:
            hostname: Target hostname or IP address
            profile: Scan profile ('quick', 'standard', 'deep', 'custom')
            custom_ports: List of ports for 'custom' profile
            
        Returns:
            HostScanResult with all scan findings
        """
        scan_start = datetime.now()
        
        # Resolve hostname to IP
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            logger.error(f"Failed to resolve hostname: {hostname}")
            return HostScanResult(
                hostname=hostname,
                ip_address='unknown',
                scan_start=scan_start,
                scan_end=datetime.now(),
                open_ports=[],
                total_ports_scanned=0,
                scan_duration_seconds=0.0
            )
        
        # Get port list based on profile
        if profile == 'custom' and custom_ports:
            ports_to_scan = custom_ports
        else:
            scan_config = self.SCAN_PROFILES.get(profile, self.SCAN_PROFILES['standard'])
            ports_to_scan = list(scan_config['ports'])
            self.timeout = scan_config['timeout']
            self.max_workers = scan_config['max_workers']
        
        logger.info(f"Starting {profile} scan of {hostname} ({ip_address}) - {len(ports_to_scan)} ports")
        
        # Scan all ports concurrently
        open_ports = await self._scan_ports_concurrent(ip_address, ports_to_scan)
        
        # Perform banner grabbing on open ports
        for port_result in open_ports:
            banner = await self._grab_banner_async(ip_address, port_result.port)
            if banner:
                port_result.banner = banner
                port_result.service, port_result.version = self._parse_banner(banner)
        
        # Try OS fingerprinting (basic implementation)
        os_guess = await self._guess_os_async(ip_address, open_ports)
        
        scan_end = datetime.now()
        scan_duration = (scan_end - scan_start).total_seconds()
        
        result = HostScanResult(
            hostname=hostname,
            ip_address=ip_address,
            scan_start=scan_start,
            scan_end=scan_end,
            open_ports=open_ports,
            os_guess=os_guess,
            total_ports_scanned=len(ports_to_scan),
            scan_duration_seconds=scan_duration
        )
        
        logger.info(f"Scan complete: {len(open_ports)} open ports found in {scan_duration:.2f}s")
        return result
    
    async def _scan_ports_concurrent(self, ip_address: str, ports: List[int]) -> List[PortScanResult]:
        """
        Scan multiple ports concurrently using thread pool
        
        Args:
            ip_address: Target IP address
            ports: List of ports to scan
            
        Returns:
            List of PortScanResult for open ports
        """
        open_ports = []
        
        # Use ThreadPoolExecutor for concurrent scanning
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all port scans
            future_to_port = {
                executor.submit(self._scan_single_port, ip_address, port): port 
                for port in ports
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    if result and result.status == 'open':
                        open_ports.append(result)
                except Exception as e:
                    logger.debug(f"Error scanning port {port}: {e}")
        
        # Sort by port number
        open_ports.sort(key=lambda x: x.port)
        return open_ports
    
    def _scan_single_port(self, ip_address: str, port: int) -> Optional[PortScanResult]:
        """
        Scan a single port using socket connection
        
        Args:
            ip_address: Target IP address
            port: Port number to scan
            
        Returns:
            PortScanResult if port is open, None otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip_address, port))
            sock.close()
            
            if result == 0:
                # Port is open
                service = self.COMMON_PORTS.get(port, 'unknown')
                return PortScanResult(
                    port=port,
                    status='open',
                    service=service,
                    protocol='tcp'
                )
            else:
                # Port is closed or filtered
                return None
                
        except socket.timeout:
            # Timeout indicates filtered port
            return None
        except Exception as e:
            logger.debug(f"Error scanning {ip_address}:{port} - {e}")
            return None
    
    async def _grab_banner_async(self, ip_address: str, port: int) -> Optional[str]:
        """
        Attempt to grab service banner from an open port
        
        Args:
            ip_address: Target IP address
            port: Open port number
            
        Returns:
            Banner string if available
        """
        try:
            # Create socket with short timeout for banner grabbing
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((ip_address, port))
            
            # Try to receive banner (some services send immediately)
            sock.send(b'HEAD / HTTP/1.1\r\n\r\n')  # HTTP request
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            if banner:
                return banner[:500]  # Limit banner length
            return None
            
        except Exception as e:
            logger.debug(f"Banner grab failed for {ip_address}:{port} - {e}")
            return None
    
    def _parse_banner(self, banner: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse service name and version from banner
        
        Args:
            banner: Banner string
            
        Returns:
            Tuple of (service_name, version)
        """
        try:
            # HTTP server detection
            if 'HTTP/' in banner:
                if 'nginx' in banner.lower():
                    parts = banner.split('nginx/')
                    if len(parts) > 1:
                        version = parts[1].split()[0]
                        return ('nginx', version)
                    return ('nginx', 'unknown')
                    
                elif 'apache' in banner.lower():
                    parts = banner.split('Apache/')
                    if len(parts) > 1:
                        version = parts[1].split()[0]
                        return ('apache', version)
                    return ('apache', 'unknown')
                    
                elif 'microsoft-iis' in banner.lower():
                    parts = banner.split('IIS/')
                    if len(parts) > 1:
                        version = parts[1].split()[0]
                        return ('iis', version)
                    return ('iis', 'unknown')
                
                return ('http', 'unknown')
            
            # SSH detection
            elif 'SSH' in banner:
                parts = banner.split('SSH-')
                if len(parts) > 1:
                    version = parts[1].split()[0]
                    return ('ssh', version)
                return ('ssh', 'unknown')
            
            # FTP detection
            elif 'FTP' in banner.upper():
                return ('ftp', 'detected')
            
            # SMTP detection
            elif 'SMTP' in banner.upper() or '220' in banner:
                return ('smtp', 'detected')
            
            return (None, None)
            
        except Exception as e:
            logger.debug(f"Error parsing banner: {e}")
            return (None, None)
    
    async def _guess_os_async(self, ip_address: str, open_ports: List[PortScanResult]) -> Optional[str]:
        """
        Attempt to guess operating system based on open ports and services
        
        Args:
            ip_address: Target IP address
            open_ports: List of open ports with service info
            
        Returns:
            OS guess string
        """
        try:
            port_numbers = [p.port for p in open_ports]
            
            # Windows indicators
            windows_ports = {135, 139, 445, 3389}  # RPC, NetBIOS, SMB, RDP
            if windows_ports.intersection(port_numbers):
                return "Windows (SMB/RDP detected)"
            
            # Linux indicators
            linux_ports = {22}  # SSH
            if 22 in port_numbers:
                # Check SSH banner for OS hints
                ssh_port = next((p for p in open_ports if p.port == 22), None)
                if ssh_port and ssh_port.banner:
                    if 'ubuntu' in ssh_port.banner.lower():
                        return "Linux (Ubuntu)"
                    elif 'debian' in ssh_port.banner.lower():
                        return "Linux (Debian)"
                    elif 'centos' in ssh_port.banner.lower():
                        return "Linux (CentOS)"
                    elif 'redhat' in ssh_port.banner.lower():
                        return "Linux (RedHat)"
                return "Linux/Unix"
            
            # macOS indicators
            if 548 in port_numbers or 5900 in port_numbers:  # AFP, VNC
                return "macOS"
            
            return "Unknown OS"
            
        except Exception as e:
            logger.debug(f"Error guessing OS: {e}")
            return "Unknown OS"
    
    def scan_host(self, hostname: str, profile: str = 'standard', custom_ports: Optional[List[int]] = None) -> HostScanResult:
        """
        Synchronous wrapper for async scan_host_async
        
        Args:
            hostname: Target hostname or IP
            profile: Scan profile
            custom_ports: Custom port list
            
        Returns:
            HostScanResult
        """
        return asyncio.run(self.scan_host_async(hostname, profile, custom_ports))
    
    def get_scan_summary(self, result: HostScanResult) -> Dict[str, Any]:
        """
        Generate a summary dict from scan results for reporting
        
        Args:
            result: HostScanResult to summarize
            
        Returns:
            Dictionary with scan summary
        """
        return {
            'target': {
                'hostname': result.hostname,
                'ip_address': result.ip_address,
                'os_guess': result.os_guess
            },
            'scan_info': {
                'start_time': result.scan_start.isoformat(),
                'end_time': result.scan_end.isoformat(),
                'duration_seconds': result.scan_duration_seconds,
                'ports_scanned': result.total_ports_scanned
            },
            'findings': {
                'open_ports_count': len(result.open_ports),
                'open_ports': [
                    {
                        'port': p.port,
                        'service': p.service,
                        'version': p.version,
                        'banner': p.banner[:100] if p.banner else None  # Truncate banner
                    }
                    for p in result.open_ports
                ]
            },
            'risk_assessment': self._assess_risk(result)
        }
    
    def _assess_risk(self, result: HostScanResult) -> Dict[str, Any]:
        """
        Assess security risk based on scan results
        
        Args:
            result: HostScanResult
            
        Returns:
            Risk assessment dictionary
        """
        risk_score = 0
        findings = []
        
        port_numbers = [p.port for p in result.open_ports]
        
        # High-risk ports
        high_risk_ports = {
            23: 'Telnet (unencrypted)',
            21: 'FTP (unencrypted)',
            3389: 'RDP (potential brute-force target)',
            1433: 'MS-SQL (database exposure)',
            3306: 'MySQL (database exposure)',
            5432: 'PostgreSQL (database exposure)',
            6379: 'Redis (often unsecured)',
            27017: 'MongoDB (often unsecured)'
        }
        
        for port, risk_desc in high_risk_ports.items():
            if port in port_numbers:
                risk_score += 15
                findings.append({
                    'severity': 'high',
                    'port': port,
                    'description': f'High-risk service detected: {risk_desc}',
                    'recommendation': f'Review necessity of port {port} and implement access controls'
                })
        
        # Too many open ports
        if len(result.open_ports) > 20:
            risk_score += 10
            findings.append({
                'severity': 'medium',
                'description': f'High number of open ports: {len(result.open_ports)}',
                'recommendation': 'Minimize attack surface by closing unnecessary ports'
            })
        
        # Outdated services (based on version strings)
        for port_result in result.open_ports:
            if port_result.version and 'old' in port_result.version.lower():
                risk_score += 5
                findings.append({
                    'severity': 'medium',
                    'port': port_result.port,
                    'description': f'Potentially outdated {port_result.service} version detected',
                    'recommendation': 'Update to latest stable version'
                })
        
        # Determine overall risk level
        if risk_score >= 40:
            risk_level = 'critical'
        elif risk_score >= 25:
            risk_level = 'high'
        elif risk_score >= 10:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': min(100, risk_score),
            'findings': findings
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create scanner instance
    scanner = AdvancedPortScanner(timeout=1.0, max_workers=100)
    
    # Scan a host
    target = "scanme.nmap.org"  # Safe test target
    print(f"Scanning {target}...")
    
    result = scanner.scan_host(target, profile='quick')
    summary = scanner.get_scan_summary(result)
    
    print(f"\n=== Scan Results ===")
    print(f"Target: {summary['target']['hostname']} ({summary['target']['ip_address']})")
    print(f"OS Guess: {summary['target']['os_guess']}")
    print(f"Duration: {summary['scan_info']['duration_seconds']:.2f}s")
    print(f"Open Ports: {summary['findings']['open_ports_count']}")
    print(f"\nRisk Level: {summary['risk_assessment']['risk_level'].upper()}")
    print(f"Risk Score: {summary['risk_assessment']['risk_score']}/100")
    
    if summary['findings']['open_ports']:
        print(f"\nOpen Ports:")
        for port in summary['findings']['open_ports']:
            print(f"  - Port {port['port']}: {port['service']} {port['version'] or ''}")
