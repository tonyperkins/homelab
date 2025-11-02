# ER707 WAN Monitor - System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ER707 WAN Monitor                           │
│                    (Python Application)                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Config     │  │  Monitoring  │  │   Logging    │         │
│  │   Manager    │→ │    Engine    │→ │   System     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                           ↓                                     │
│                    ┌──────────────┐                            │
│                    │  Omada API   │                            │
│                    │   Client     │                            │
│                    └──────────────┘                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS API Calls
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Omada Controller                             │
│                  (Hardware/Software)                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     API      │  │   Device     │  │   Network    │         │
│  │   Gateway    │→ │   Manager    │→ │   Control    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Management Commands
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                      TP-Link ER707                              │
│                    (Gateway/Firewall)                           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  WAN Port 1  │  │  LAN Ports   │  │   Routing    │         │
│  │   (WAN1)     │  │   (LAN1-8)   │  │   Engine     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Ethernet Connection
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AT&T BGW320-500                              │
│                   (Fiber Gateway)                               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Fiber ONT   │  │ IP Passthrough│  │   DHCP      │         │
│  │  Interface   │→ │   Config     │→ │   Server    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Fiber Connection
                          ↓
                    AT&T Fiber Network
                      (Public Internet)
```

## 🔄 Monitoring Flow

```
START
  │
  ├─→ Load Configuration (config.yaml)
  │
  ├─→ Initialize Logging System
  │
  ├─→ Connect to Omada Controller
  │     ├─→ Authenticate (username/password)
  │     ├─→ Get Controller ID
  │     └─→ Get Site ID
  │
  ├─→ Enter Monitoring Loop
  │     │
  │     ├─→ Query ER707 Device Status
  │     │     └─→ GET /api/v2/sites/{site}/gateways/{mac}
  │     │
  │     ├─→ Extract WAN IP Address
  │     │     └─→ Parse JSON response
  │     │
  │     ├─→ Validate IP Address
  │     │     ├─→ Check if valid IP format
  │     │     └─→ Check if RFC 1918 private range
  │     │
  │     ├─→ Decision: Is Private IP?
  │     │     │
  │     │     ├─→ NO (Public IP)
  │     │     │     ├─→ Log: "Public IP confirmed"
  │     │     │     └─→ Continue monitoring
  │     │     │
  │     │     └─→ YES (Private IP)
  │     │           ├─→ Log: "Private IP detected"
  │     │           ├─→ Trigger Remediation
  │     │           │     │
  │     │           │     ├─→ Disconnect WAN Port
  │     │           │     │     └─→ PATCH /ports/{id} {enable: false}
  │     │           │     │
  │     │           │     ├─→ Wait (5 seconds)
  │     │           │     │
  │     │           │     ├─→ Reconnect WAN Port
  │     │           │     │     └─→ PATCH /ports/{id} {enable: true}
  │     │           │     │
  │     │           │     ├─→ Wait (30 seconds for stabilization)
  │     │           │     │
  │     │           │     ├─→ Verify New IP
  │     │           │     │     ├─→ Query device status
  │     │           │     │     └─→ Check if public IP obtained
  │     │           │     │
  │     │           │     └─→ Decision: Success?
  │     │           │           ├─→ YES: Log success, continue
  │     │           │           └─→ NO: Retry (up to max attempts)
  │     │           │
  │     │           └─→ Continue monitoring
  │     │
  │     ├─→ Wait (check_interval_seconds)
  │     │
  │     └─→ Loop back to Query Device Status
  │
  └─→ Handle Errors
        ├─→ Re-authenticate if needed
        ├─→ Log errors
        └─→ Continue monitoring
```

## 📦 Component Architecture

### 1. Configuration Manager
```python
Responsibilities:
- Load config.yaml
- Validate configuration
- Provide configuration to other components

Files:
- config.yaml (user configuration)
- config.example.yaml (template)
```

### 2. Omada Controller Client
```python
Class: OmadaController

Methods:
- login() → Authenticate with controller
- get_wan_status() → Query device WAN status
- disconnect_wan_port() → Disable WAN port
- connect_wan_port() → Enable WAN port
- reconnect_wan_port() → Full reconnection sequence

API Endpoints Used:
- POST /api/v2/login
- GET /api/v2/controllers
- GET /api/v2/sites
- GET /api/v2/sites/{site}/gateways/{mac}
- PATCH /api/v2/sites/{site}/gateways/{mac}/ports/{id}
```

### 3. IP Validator
```python
Class: IPValidator

Methods:
- is_private_ip() → Check if IP is RFC 1918
- is_valid_ip() → Validate IP format

RFC 1918 Ranges:
- 10.0.0.0/8 (10.0.0.0 - 10.255.255.255)
- 172.16.0.0/12 (172.16.0.0 - 172.31.255.255)
- 192.168.0.0/16 (192.168.0.0 - 192.168.255.255)
```

### 4. Monitoring Engine
```python
Class: WANMonitor

Methods:
- monitor_loop() → Main monitoring loop
- check_wan_ip() → Check current WAN IP
- extract_wan_ip() → Parse IP from API response
- remediate_private_ip() → Execute remediation

State:
- last_known_ip → Track IP changes
- consecutive_failures → Error recovery
```

### 5. Logging System
```python
Configuration:
- Level: DEBUG, INFO, WARNING, ERROR
- Outputs: File + Console
- Format: Timestamp - Level - Message

Log Files:
- logs/wan_monitor.log (main log)
- logs/service_output.log (Windows service)
- logs/service_error.log (Windows service)
```

## 🔌 API Integration

### Omada Controller API v2

```
Authentication Flow:
1. POST /api/v2/login
   Request: {username, password}
   Response: {token, ...}

2. Use token in subsequent requests
   Header: Cookie: {token}

Device Management:
1. GET /api/v2/controllers
   → Get controller ID

2. GET /api/v2/sites
   → Get site ID for site name

3. GET /api/v2/sites/{site}/gateways/{mac}
   → Get device status and WAN IP

4. PATCH /api/v2/sites/{site}/gateways/{mac}/ports/{id}
   Request: {enable: true/false}
   → Enable/disable WAN port
```

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Security Layers                             │
│                                                                 │
│  1. Configuration Security                                      │
│     ├─→ config.yaml excluded from version control              │
│     ├─→ File permissions restricted (chmod 600)                │
│     └─→ Credentials stored locally only                        │
│                                                                 │
│  2. Network Security                                            │
│     ├─→ HTTPS for all API communication                        │
│     ├─→ SSL certificate verification (optional)                │
│     └─→ No external network access required                    │
│                                                                 │
│  3. Authentication Security                                     │
│     ├─→ Token-based authentication                             │
│     ├─→ Automatic re-authentication on failure                 │
│     └─→ Session management                                     │
│                                                                 │
│  4. Operational Security                                        │
│     ├─→ Read-only operations (except port control)             │
│     ├─→ Minimal privilege requirements                         │
│     └─→ Audit logging of all actions                           │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

### Normal Operation (Public IP)
```
Monitor → Query API → Extract IP → Validate IP → Public ✓ → Log → Wait → Loop
```

### Remediation Flow (Private IP)
```
Monitor → Query API → Extract IP → Validate IP → Private ✗
    ↓
Log Warning
    ↓
Disconnect WAN Port → Wait 5s → Reconnect WAN Port
    ↓
Wait 30s (stabilization)
    ↓
Query API → Extract IP → Validate IP
    ↓
Public ✓ → Log Success → Continue Monitoring
    │
    └→ Private ✗ → Retry (up to max attempts)
```

## 🎯 Decision Points

### 1. IP Classification
```
Input: IP Address String
    ↓
Valid Format? → NO → Log Error → Skip
    ↓ YES
In 10.0.0.0/8? → YES → Private
    ↓ NO
In 172.16.0.0/12? → YES → Private
    ↓ NO
In 192.168.0.0/16? → YES → Private
    ↓ NO
Public IP → Continue Monitoring
```

### 2. Remediation Decision
```
Private IP Detected
    ↓
Attempt < Max Attempts? → NO → Log Failure → Continue Monitoring
    ↓ YES
Execute Remediation
    ↓
Public IP Obtained? → YES → Log Success → Continue Monitoring
    ↓ NO
Increment Attempt → Retry
```

### 3. Error Recovery
```
API Call Failed
    ↓
Consecutive Failures < 3? → YES → Log Warning → Continue
    ↓ NO
Re-authenticate
    ↓
Success? → YES → Reset Counter → Continue
    ↓ NO
Log Error → Wait → Retry
```

## 🔧 Deployment Architectures

### Standalone Deployment
```
┌─────────────────────────┐
│   Monitoring Server     │
│                         │
│  ┌──────────────────┐   │
│  │  WAN Monitor     │   │
│  │  (Python App)    │   │
│  └────────┬─────────┘   │
│           │ HTTPS       │
└───────────┼─────────────┘
            ↓
    Omada Controller
```

### Service Deployment (Windows)
```
┌─────────────────────────┐
│   Windows Server        │
│                         │
│  ┌──────────────────┐   │
│  │  NSSM Service    │   │
│  │  ┌────────────┐  │   │
│  │  │ WAN Monitor│  │   │
│  │  └────────────┘  │   │
│  └────────┬─────────┘   │
│           │ Auto-start  │
└───────────┼─────────────┘
            ↓
    Omada Controller
```

### Service Deployment (Linux)
```
┌─────────────────────────┐
│   Linux Server          │
│                         │
│  ┌──────────────────┐   │
│  │ Systemd Service  │   │
│  │  ┌────────────┐  │   │
│  │  │ WAN Monitor│  │   │
│  │  └────────────┘  │   │
│  └────────┬─────────┘   │
│           │ Auto-start  │
└───────────┼─────────────┘
            ↓
    Omada Controller
```

## 📈 Performance Characteristics

### Resource Usage
```
CPU: < 1% (sleeps between checks)
Memory: 20-30 MB (Python interpreter + libraries)
Disk I/O: Minimal (log writes only)
Network: ~5KB per check (API calls)
```

### Timing
```
Check Interval: 180 seconds (configurable)
API Response: < 1 second (typical)
Remediation Time: ~35-40 seconds
  ├─→ Disconnect: ~1 second
  ├─→ Wait: 5 seconds
  ├─→ Reconnect: ~1 second
  ├─→ Stabilization: 30 seconds
  └─→ Verification: ~1 second
```

### Scalability
```
Single Instance:
- Monitors: 1 device
- API Calls: 1 per interval
- Concurrent: N/A

Multiple Instances:
- Each monitors different device or port
- Independent operation
- Shared Omada Controller
```

## 🔍 Observability

### Logging Levels
```
DEBUG: Detailed flow, API responses
INFO: Normal operation, IP changes
WARNING: Private IP detected, remediation
ERROR: Failures, authentication issues
CRITICAL: System failures
```

### Metrics (Logged)
```
- Check frequency
- IP changes
- Remediation events
- Success/failure rates
- API response times
- Authentication events
```

## 🛠️ Extensibility Points

### Custom Notifications
```python
def remediate_private_ip(self):
    # Existing remediation code
    ...
    # Add custom notification
    self.send_notification("Private IP detected")
```

### Custom IP Extraction
```python
def extract_wan_ip(self, device_status):
    # Modify for different API versions
    # Add custom parsing logic
```

### Custom Validation
```python
def is_private_ip(ip_str):
    # Add custom IP ranges
    # Add whitelist/blacklist logic
```

---

**Architecture Version:** 1.0.0  
**Last Updated:** November 2, 2024  
**Compatibility:** Omada Controller API v2
