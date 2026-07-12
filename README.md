🎯 Overview
BlackMamba APT is a professional-grade Cache Poisoning Framework designed for Red Team operations and security testing. Unlike traditional penetration testing tools, BlackMamba exploits Unkeyed Headers in CDN/Edge Cache infrastructure to deploy stealthy, zero-trace attacks.

Key Philosophy
"Minimal in behavior, maximum in damage, and completely asynchronous."

The tool sends only a single request to deploy the attack vector, then completely disengages. The actual compromise occurs when a privileged user (admin) legitimately accesses the poisoned cache, unknowingly triggering the exfiltration of sensitive data.

🎯 Tactical Objectives
-Zero Network Footprint: No scanning, no brute-force, no RCE payloads in network logs

-Edge Infrastructure Exploitation: Leverages CDN/Cloud Edge Caches

-Asynchronous Exfiltration: Attack and data collection are completely decoupled

-SOC Evasion: Bypasses traditional monitoring and detection systems

-Admin Privilege Harvesting: Captures session tokens, cookies, and credentials


⚙️ How It Works
The Attack Chain
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: CACHE POISONING                            │
│                                                                             │
│  Attacker → Single HTTP Request with Malicious Headers → CDN Edge Cache   │
│                                                                             │
│  Headers used:                                                              │
│  • X-Forwarded-Host: attacker.com                                          │
│  • X-Forwarded-Scheme: https                                               │
│  • Cache-Control: no-cache                                                 │
│                                                                             │
│  Result: CDN caches poisoned response (malicious JavaScript)              |
\
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: VICTIM TRIGGER                              │
│                                                                             │
│  Victim (Admin) → Legitimate Request → CDN (Poisoned Cache)                 │
│                                                                             │
│  Result: Victim receives malicious response without knowing                 │
│                                                                             │
│  SOC View: No unusual traffic, no alerts, normal user behavior              │ 
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 3: DATA EXFILTRATION                           │
│                                                                             │
│  Victim's Browser → Executes Malicious JavaScript → Exfil Server            │
│                                                                             │
│  Exfiltrated Data:                                                          │
│  • Session Cookies                                                          │
│  • Authentication Tokens                                                    │
│  • LocalStorage/SessionStorage                                              │
│  • Browser Fingerprint                                                      │
│  • User Agent & Platform                                                    │
│  • Referrer & URL                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
