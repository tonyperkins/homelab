# ER707 WAN Monitor - File Structure

## 📁 Complete Project Layout

```
homelab/
│
├── 📄 Core Application Files
│   ├── er707_wan_monitor.py          # Main monitoring service (20KB)
│   │   └── Classes:
│   │       ├── OmadaController        # API communication
│   │       ├── IPValidator            # RFC 1918 detection
│   │       └── WANMonitor             # Main monitoring logic
│   │
│   ├── config.yaml                    # Active configuration (EDIT THIS)
│   │   └── Sections:
│   │       ├── omada                  # Controller settings
│   │       ├── device                 # ER707 settings
│   │       ├── monitoring             # Behavior settings
│   │       └── logging                # Log settings
│   │
│   └── requirements.txt               # Python dependencies
│       ├── requests>=2.31.0
│       ├── PyYAML>=6.0.1
│       └── urllib3>=2.0.7
│
├── 🔧 Utility Scripts
│   ├── test_connection.py             # Connection test utility (11KB)
│   │   └── Tests:
│   │       ├── Controller connectivity
│   │       ├── Authentication
│   │       ├── Device access
│   │       └── WAN IP extraction
│   │
│   └── troubleshoot.py                # Diagnostic utility (13KB)
│       └── Checks:
│           ├── Python version
│           ├── Dependencies
│           ├── Configuration
│           ├── Network connectivity
│           ├── Authentication
│           ├── MAC address format
│           └── IP detection logic
│
├── 🚀 Deployment Files
│   ├── install_windows_service.ps1    # Windows service installer (4KB)
│   │   └── Uses NSSM to create Windows service
│   │
│   └── wan-monitor.service            # Linux systemd service template (1KB)
│       └── Copy to /etc/systemd/system/
│
├── 📚 Documentation
│   ├── README.md                      # Complete documentation (12KB)
│   │   └── Sections:
│   │       ├── Problem statement
│   │       ├── Features
│   │       ├── Installation
│   │       ├── Configuration
│   │       ├── Usage
│   │       ├── Troubleshooting
│   │       ├── Windows service setup
│   │       ├── Linux systemd setup
│   │       └── API compatibility
│   │
│   ├── GETTING_STARTED.md             # Step-by-step setup guide (11KB)
│   │   └── Sections:
│   │       ├── Prerequisites
│   │       ├── Installation steps
│   │       ├── Configuration guide
│   │       ├── Testing procedures
│   │       ├── Deployment options
│   │       ├── Monitoring guide
│   │       └── Troubleshooting
│   │
│   ├── QUICKSTART.md                  # 5-minute quick reference (2KB)
│   │   └── Sections:
│   │       ├── Install dependencies
│   │       ├── Configure
│   │       ├── Test run
│   │       └── Run continuously
│   │
│   ├── PROJECT_SUMMARY.md             # Project overview (10KB)
│   │   └── Sections:
│   │       ├── Overview
│   │       ├── File list
│   │       ├── Quick setup
│   │       ├── Features
│   │       ├── Configuration
│   │       ├── How it works
│   │       ├── Deployment options
│   │       ├── Performance metrics
│   │       └── Security practices
│   │
│   └── FILE_STRUCTURE.md              # This file
│       └── Visual project layout
│
├── 🔒 Configuration Templates
│   └── config.example.yaml            # Configuration template (554 bytes)
│       └── Copy to config.yaml and customize
│
├── 📋 Project Files
│   ├── LICENSE                        # MIT License (1KB)
│   └── .gitignore                     # Git ignore rules (372 bytes)
│       └── Excludes:
│           ├── Python cache files
│           ├── Log files
│           ├── config.yaml (contains credentials)
│           └── IDE files
│
└── 📊 Runtime Files (Created automatically)
    └── logs/                          # Log directory
        ├── wan_monitor.log            # Main application log
        ├── service_output.log         # Windows service stdout
        └── service_error.log          # Windows service stderr
```

## 📖 File Descriptions

### Core Application Files

| File | Purpose | Size | Edit? |
|------|---------|------|-------|
| `er707_wan_monitor.py` | Main monitoring service | 20KB | Only for customization |
| `config.yaml` | Active configuration | 2KB | **YES - Required** |
| `requirements.txt` | Python dependencies | 46B | No |

### Utility Scripts

| File | Purpose | Size | When to Use |
|------|---------|------|-------------|
| `test_connection.py` | Test Omada connection | 11KB | Before first run |
| `troubleshoot.py` | Diagnostic checks | 13KB | When issues occur |

### Deployment Files

| File | Purpose | Platform | Size |
|------|---------|----------|------|
| `install_windows_service.ps1` | Service installer | Windows | 4KB |
| `wan-monitor.service` | Service template | Linux | 1KB |

### Documentation Files

| File | Purpose | Length | Audience |
|------|---------|--------|----------|
| `README.md` | Complete docs | 12KB | All users |
| `GETTING_STARTED.md` | Setup guide | 11KB | New users |
| `QUICKSTART.md` | Quick reference | 2KB | Experienced users |
| `PROJECT_SUMMARY.md` | Overview | 10KB | Decision makers |
| `FILE_STRUCTURE.md` | This file | 5KB | Developers |

## 🎯 Which File Do I Need?

### "I'm just getting started"
→ Start with **GETTING_STARTED.md**

### "I want to set up quickly"
→ Follow **QUICKSTART.md**

### "I need complete documentation"
→ Read **README.md**

### "I want to understand the project"
→ Check **PROJECT_SUMMARY.md**

### "Something isn't working"
→ Run **troubleshoot.py**

### "I want to test before deploying"
→ Run **test_connection.py**

### "I need to configure the monitor"
→ Edit **config.yaml**

### "I want to run as a service"
→ Use **install_windows_service.ps1** (Windows) or **wan-monitor.service** (Linux)

## 🔄 Typical Workflow

```
1. Read GETTING_STARTED.md
   ↓
2. Install dependencies (requirements.txt)
   ↓
3. Copy config.example.yaml → config.yaml
   ↓
4. Edit config.yaml with your settings
   ↓
5. Run troubleshoot.py
   ↓
6. Run test_connection.py
   ↓
7. Run er707_wan_monitor.py
   ↓
8. Deploy as service (install_windows_service.ps1 or wan-monitor.service)
   ↓
9. Monitor logs/wan_monitor.log
```

## 📏 File Sizes

| Category | Files | Total Size |
|----------|-------|------------|
| Core Application | 3 files | ~20KB |
| Utilities | 2 files | ~24KB |
| Deployment | 2 files | ~5KB |
| Documentation | 5 files | ~50KB |
| Configuration | 2 files | ~2KB |
| **Total** | **14 files** | **~101KB** |

## 🔐 Security Considerations

### Files Containing Sensitive Data
- ❌ **config.yaml** - Contains credentials (excluded from git)
- ✅ **config.example.yaml** - Template only (safe to share)

### Files Safe to Share
- ✅ All Python scripts
- ✅ All documentation
- ✅ All deployment files
- ✅ config.example.yaml

### Files to Protect
- ❌ config.yaml
- ❌ logs/*.log (may contain IP addresses)

## 📝 Modification Guide

### Files You Should Edit
1. **config.yaml** - Required for your environment
2. **wan-monitor.service** - Update paths and user (Linux)
3. **install_windows_service.ps1** - Update Python path (Windows)

### Files You Might Customize
1. **er707_wan_monitor.py** - Add custom logic or notifications
2. **.gitignore** - Add custom exclusions

### Files You Shouldn't Edit
1. **requirements.txt** - Managed dependencies
2. **LICENSE** - Legal terms
3. **Documentation files** - Reference material

## 🎨 File Relationships

```
config.yaml ──────────────┐
                          ├──→ er707_wan_monitor.py ──→ logs/wan_monitor.log
requirements.txt ─────────┘

test_connection.py ────────→ config.yaml
troubleshoot.py ───────────→ config.yaml

install_windows_service.ps1 ──→ er707_wan_monitor.py
wan-monitor.service ──────────→ er707_wan_monitor.py

README.md ─────────────────┐
GETTING_STARTED.md ────────├──→ User Documentation
QUICKSTART.md ─────────────│
PROJECT_SUMMARY.md ────────┘
```

## 🏗️ Directory Structure (Runtime)

After running the monitor, your directory will look like:

```
homelab/
├── [All files listed above]
└── logs/                          # Created automatically
    ├── wan_monitor.log            # Main log
    ├── service_output.log         # Windows service stdout
    └── service_error.log          # Windows service stderr
```

## 📦 Distribution

### Minimal Distribution (For Deployment)
```
homelab/
├── er707_wan_monitor.py
├── config.yaml (configured)
├── requirements.txt
└── logs/ (empty directory)
```

### Complete Distribution (For Sharing)
```
homelab/
├── All files except:
│   ├── config.yaml (use config.example.yaml instead)
│   └── logs/ (exclude log files)
```

## 🔍 Quick Reference

| Task | File(s) |
|------|---------|
| Install | requirements.txt |
| Configure | config.yaml |
| Test | test_connection.py, troubleshoot.py |
| Run | er707_wan_monitor.py |
| Deploy (Windows) | install_windows_service.ps1 |
| Deploy (Linux) | wan-monitor.service |
| Learn | README.md, GETTING_STARTED.md |
| Quick Start | QUICKSTART.md |
| Overview | PROJECT_SUMMARY.md |
| Navigate | FILE_STRUCTURE.md (this file) |

---

**Need help?** Start with GETTING_STARTED.md for a complete walkthrough.
