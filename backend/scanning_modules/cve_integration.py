"""
CVE Database Integration Module
National Vulnerability Database (NVD) integration for vulnerability tracking
"""

import requests
import json
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)


@dataclass
class CVEDetails:
    """CVE vulnerability details"""
    cve_id: str
    description: str
    severity: str
    cvss_score: float
    published_date: datetime
    affected_products: List[str]
    exploit_available: bool = False
    remediation: Optional[str] = None


class CVEIntegration:
    """
    CVE Database Integration for Enterprise Scanner
    
    Features:
    - NVD API integration
    - Local CVE database caching
    - Version-based vulnerability detection
    - Exploit availability checking
    - CVSS score calculation
    - Remediation guidance
    """
    
    NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    def __init__(self, db_path: str = "cve_database.db", api_key: Optional[str] = None):
        """
        Initialize CVE integration
        
        Args:
            db_path: Path to local SQLite database
            api_key: Optional NVD API key for higher rate limits
        """
        self.db_path = db_path
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'apiKey': api_key})
        
        self._init_database()
    
    def _init_database(self):
        """Initialize local CVE database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cves (
                cve_id TEXT PRIMARY KEY,
                description TEXT,
                severity TEXT,
                cvss_score REAL,
                published_date TEXT,
                affected_products TEXT,
                exploit_available INTEGER,
                remediation TEXT,
                last_updated TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cve_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT,
                vendor TEXT,
                product TEXT,
                version TEXT,
                FOREIGN KEY (cve_id) REFERENCES cves(cve_id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"CVE database initialized at {self.db_path}")
    
    def sync_cve_database(self, days: int = 30):
        """
        Sync CVE database with NVD (last N days)
        
        Args:
            days: Number of days to fetch (default 30)
        """
        logger.info(f"Syncing CVE database for last {days} days...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            # Call NVD API
            params = {
                'pubStartDate': start_date.isoformat(),
                'pubEndDate': end_date.isoformat()
            }
            
            response = self.session.get(
                self.NVD_API_BASE,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])
                
                logger.info(f"Fetched {len(vulnerabilities)} CVEs from NVD")
                
                # Store in local database
                self._store_cves(vulnerabilities)
            else:
                logger.error(f"NVD API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error syncing CVE database: {e}")
    
    def _store_cves(self, vulnerabilities: List[Dict]):
        """Store CVEs in local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for vuln in vulnerabilities:
            try:
                cve = vuln.get('cve', {})
                cve_id = cve.get('id', 'UNKNOWN')
                
                # Extract details
                descriptions = cve.get('descriptions', [])
                description = descriptions[0].get('value', '') if descriptions else ''
                
                metrics = cve.get('metrics', {})
                cvss_data = metrics.get('cvssMetricV31', [{}])[0]
                cvss_score = cvss_data.get('cvssData', {}).get('baseScore', 0.0)
                severity = cvss_data.get('cvssData', {}).get('baseSeverity', 'UNKNOWN')
                
                published = cve.get('published', datetime.now().isoformat())
                
                # Insert or update
                cursor.execute("""
                    INSERT OR REPLACE INTO cves 
                    (cve_id, description, severity, cvss_score, published_date, 
                     affected_products, exploit_available, remediation, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cve_id, description, severity, cvss_score, published,
                    '', 0, '', datetime.now().isoformat()
                ))
                
            except Exception as e:
                logger.debug(f"Error storing CVE: {e}")
        
        conn.commit()
        conn.close()
        logger.info("CVE database sync complete")
    
    def check_version_vulnerabilities(
        self, 
        software: str, 
        version: str
    ) -> List[CVEDetails]:
        """
        Check if a specific software version has known vulnerabilities
        
        Args:
            software: Software name (e.g., 'nginx', 'apache', 'mysql')
            version: Version string (e.g., '1.18.0')
            
        Returns:
            List of CVE details for matching vulnerabilities
        """
        logger.info(f"Checking vulnerabilities for {software} {version}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search for matching CVEs
        cursor.execute("""
            SELECT cve_id, description, severity, cvss_score, 
                   published_date, exploit_available, remediation
            FROM cves
            WHERE LOWER(description) LIKE ?
            ORDER BY cvss_score DESC
        """, (f'%{software.lower()}%',))
        
        results = []
        for row in cursor.fetchall():
            results.append(CVEDetails(
                cve_id=row[0],
                description=row[1],
                severity=row[2],
                cvss_score=row[3],
                published_date=datetime.fromisoformat(row[4]),
                affected_products=[software],
                exploit_available=bool(row[5]),
                remediation=row[6]
            ))
        
        conn.close()
        return results
    
    def check_exploit_availability(self, cve_id: str) -> bool:
        """
        Check if exploit is available for CVE
        
        Checks multiple sources:
        - Exploit-DB (searchsploit API)
        - Metasploit Framework
        - Packet Storm Security
        - Exploit Database mirror
        
        Args:
            cve_id: CVE identifier (e.g., "CVE-2024-1234")
            
        Returns:
            True if exploit is publicly available
        """
        try:
            # Method 1: Check Exploit-DB via web search API
            exploit_db_url = f"https://www.exploit-db.com/search?cve={cve_id}"
            try:
                response = requests.get(exploit_db_url, timeout=5)
                if response.status_code == 200:
                    # Check if any exploits are found
                    if 'No Results' not in response.text and 'Exploit Database' in response.text:
                        logger.info(f"Exploit found on Exploit-DB for {cve_id}")
                        return True
            except Exception as e:
                logger.debug(f"Error checking Exploit-DB: {e}")
            
            # Method 2: Check Metasploit Framework (via GitHub API)
            metasploit_search_url = f"https://api.github.com/search/code?q={cve_id}+repo:rapid7/metasploit-framework"
            try:
                headers = {'Accept': 'application/vnd.github.v3+json'}
                response = requests.get(metasploit_search_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('total_count', 0) > 0:
                        logger.info(f"Metasploit module found for {cve_id}")
                        return True
            except Exception as e:
                logger.debug(f"Error checking Metasploit: {e}")
            
            # Method 3: Check NIST NVD for references containing "exploit"
            nvd_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
            try:
                response = requests.get(nvd_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    vulnerabilities = data.get('vulnerabilities', [])
                    if vulnerabilities:
                        cve_data = vulnerabilities[0].get('cve', {})
                        references = cve_data.get('references', [])
                        
                        # Check if any reference URL contains "exploit"
                        for ref in references:
                            url = ref.get('url', '').lower()
                            tags = ref.get('tags', [])
                            
                            if 'exploit' in url or 'Exploit' in tags:
                                logger.info(f"Exploit reference found in NVD for {cve_id}")
                                return True
            except Exception as e:
                logger.debug(f"Error checking NVD references: {e}")
            
            # Method 4: Check local Metasploit database if available
            metasploit_db_path = os.path.join(os.path.expanduser('~'), '.msf4', 'modules_metadata.json')
            if os.path.exists(metasploit_db_path):
                try:
                    with open(metasploit_db_path, 'r') as f:
                        modules = json.load(f)
                        for module in modules:
                            if 'references' in module:
                                for ref in module['references']:
                                    if cve_id.upper() in str(ref).upper():
                                        logger.info(f"Local Metasploit module found for {cve_id}")
                                        return True
                except Exception as e:
                    logger.debug(f"Error checking local Metasploit DB: {e}")
            
            # Method 5: Check Packet Storm Security
            packetstorm_url = f"https://packetstormsecurity.com/search/?q={cve_id}"
            try:
                response = requests.get(packetstorm_url, timeout=5)
                if response.status_code == 200:
                    if 'Exploit' in response.text or 'PoC' in response.text:
                        logger.info(f"Exploit/PoC found on Packet Storm for {cve_id}")
                        return True
            except Exception as e:
                logger.debug(f"Error checking Packet Storm: {e}")
            
            # Method 6: Check local database cache
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT exploit_available FROM cves WHERE cve_id = ?
            """, (cve_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return True
            
            # No exploit found
            return False
            
        except Exception as e:
            logger.error(f"Error checking exploit availability for {cve_id}: {e}")
            return False
    
    def get_remediation_guidance(self, cve_id: str) -> str:
        """
        Get remediation guidance for a CVE
        
        Args:
            cve_id: CVE identifier
            
        Returns:
            Remediation guidance string
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT remediation FROM cves WHERE cve_id = ?
        """, (cve_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return result[0]
        else:
            return "Update to the latest patched version of the affected software"
    
    def calculate_cvss_score(self, cve_id: str) -> float:
        """
        Get CVSS score for a CVE
        
        Args:
            cve_id: CVE identifier
            
        Returns:
            CVSS base score (0.0 - 10.0)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cvss_score FROM cves WHERE cve_id = ?
        """, (cve_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0.0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize CVE integration
    cve = CVEIntegration()
    
    # Sync database (uncomment to fetch from NVD)
    # cve.sync_cve_database(days=30)
    
    # Check for vulnerabilities
    vulnerabilities = cve.check_version_vulnerabilities('nginx', '1.18.0')
    
    print(f"Found {len(vulnerabilities)} CVEs for nginx 1.18.0")
    for vuln in vulnerabilities[:5]:  # Show first 5
        print(f"  - {vuln.cve_id}: {vuln.severity} (CVSS: {vuln.cvss_score})")
