# 🚀 ER707 WAN Monitor - START HERE

Welcome to the ER707 WAN Monitor project! This automated solution eliminates network downtime caused by AT&T BGW320-500 gateway IP passthrough issues.

## ⚡ Quick Navigation

### 🆕 New Users - Start Here
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete step-by-step setup guide
2. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick setup for experienced users

### 📚 Documentation
- **[README.md](README.md)** - Complete documentation with all features and options
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview and highlights
- **[FILE_STRUCTURE.md](FILE_STRUCTURE.md)** - Navigate the project files

### 🔧 Tools & Utilities
- **[test_connection.py](test_connection.py)** - Test your Omada Controller connection
- **[troubleshoot.py](troubleshoot.py)** - Diagnose configuration issues

### ⚙️ Configuration
- **[config.yaml](config.yaml)** - Main configuration file (EDIT THIS)
- **[config.example.yaml](config.example.yaml)** - Configuration template

### 🚀 Deployment
- **[install_windows_service.ps1](install_windows_service.ps1)** - Windows service installer
- **[wan-monitor.service](wan-monitor.service)** - Linux systemd service template

## 🎯 What This Does

**Problem:** Your ER707 occasionally gets a private IP (192.168.x.x, 10.x.x.x) instead of a public IP through AT&T's IP passthrough, breaking internet connectivity.

**Solution:** This monitor automatically detects private IPs and triggers a WAN port reconnection to obtain a proper public IP - no manual intervention needed!

## ⚡ Super Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (edit config.yaml with your settings)
# - Omada Controller URL and credentials
# - ER707 MAC address

# 3. Run
python er707_wan_monitor.py
```

## 📋 Setup Checklist

- [ ] Python 3.7+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Omada Controller URL and credentials ready
- [ ] ER707 MAC address obtained (from Omada Controller)
- [ ] `config.yaml` edited with your settings
- [ ] Connection tested: `python test_connection.py`
- [ ] Monitor running: `python er707_wan_monitor.py`
- [ ] Service configured for continuous operation

## 🎓 Choose Your Path

### Path 1: I'm New to This
→ Read **[GETTING_STARTED.md](GETTING_STARTED.md)** for detailed walkthrough

### Path 2: I Know What I'm Doing
→ Follow **[QUICKSTART.md](QUICKSTART.md)** for rapid deployment

### Path 3: I Want All the Details
→ Study **[README.md](README.md)** for complete documentation

### Path 4: Something's Wrong
→ Run **[troubleshoot.py](troubleshoot.py)** for diagnostics

## 🔑 Key Files You Need to Edit

### 1. config.yaml (Required)
```yaml
omada:
  controller_url: "https://YOUR_IP:8043"  # Change this
  username: "admin"                        # Change this
  password: "your_password"                # Change this

device:
  mac_address: "XX-XX-XX-XX-XX-XX"        # Change this
```

### 2. install_windows_service.ps1 (Windows Only)
```powershell
$PythonPath = "C:\Python\python.exe"  # Update this path
```

### 3. wan-monitor.service (Linux Only)
```ini
User=your_username                    # Update this
WorkingDirectory=/path/to/homelab     # Update this
ExecStart=/usr/bin/python3 /path/to/homelab/er707_wan_monitor.py  # Update this
```

## 🧪 Testing Before Production

### Step 1: Troubleshoot
```bash
python troubleshoot.py
```
Checks: Python, dependencies, config, network, authentication

### Step 2: Test Connection
```bash
python test_connection.py
```
Tests: Controller connection, device access, WAN IP detection

### Step 3: Manual Run
```bash
python er707_wan_monitor.py
```
Watch for: Successful authentication, IP detection, normal operation

## 📊 What Success Looks Like

```
2024-11-02 10:30:15 - INFO - Starting WAN IP monitoring service
2024-11-02 10:30:16 - INFO - Successfully authenticated with Omada Controller
2024-11-02 10:30:17 - INFO - Public IP confirmed: 203.0.113.45
```

## ⚠️ Common Issues

| Issue | Quick Fix |
|-------|-----------|
| "Login failed" | Check URL format, credentials, SSL settings |
| "Device not found" | Verify MAC address in config.yaml |
| "WAN IP not detected" | Run test_connection.py to debug |
| "Permission denied" | Run as admin/sudo or check file permissions |

## 🎯 Next Steps After Setup

1. **Monitor logs** - Watch `logs/wan_monitor.log` for activity
2. **Observe behavior** - See how often private IPs occur
3. **Verify remediation** - Confirm automatic fixes work
4. **Deploy as service** - Set up for continuous operation
5. **Review periodically** - Check logs for any issues

## 📞 Need Help?

1. **Configuration issues?** → Run `python troubleshoot.py`
2. **Connection problems?** → Run `python test_connection.py`
3. **Want to understand more?** → Read `README.md`
4. **Need step-by-step help?** → Follow `GETTING_STARTED.md`
5. **Looking for quick reference?** → Check `QUICKSTART.md`

## 🎉 Ready to Begin?

**New users:** Start with [GETTING_STARTED.md](GETTING_STARTED.md)

**Experienced users:** Jump to [QUICKSTART.md](QUICKSTART.md)

**Having issues:** Run [troubleshoot.py](troubleshoot.py)

---

**Project Status:** Production Ready ✅  
**Version:** 1.0.0  
**License:** MIT  
**Last Updated:** November 2, 2024

**Let's eliminate those private IP issues! 🚀**
