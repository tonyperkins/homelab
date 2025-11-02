# Getting Started with ER707 WAN Monitor

Welcome! This guide will walk you through setting up the ER707 WAN Monitor from scratch.

## 📋 What You'll Need

Before starting, gather this information:

- [ ] Omada Controller URL (e.g., `https://192.168.1.10:8043`)
- [ ] Omada Controller admin username
- [ ] Omada Controller admin password
- [ ] ER707 device MAC address (find in Omada Controller → Devices → Gateways)
- [ ] Python 3.7+ installed on your system

## 🚀 Installation Steps

### Step 1: Verify Python Installation

Open a terminal/command prompt and run:

```bash
python --version
```

You should see Python 3.7 or higher. If not, download from [python.org](https://www.python.org/downloads/).

### Step 2: Install Dependencies

Navigate to the project directory and run:

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - For API communication
- `PyYAML` - For configuration file parsing
- `urllib3` - For HTTP handling

### Step 3: Configure the Monitor

1. **Open `config.yaml`** in a text editor

2. **Update Omada Controller settings:**
   ```yaml
   omada:
     controller_url: "https://YOUR_CONTROLLER_IP:8043"  # Change this
     username: "admin"                                   # Change this
     password: "your_actual_password"                    # Change this
     site_name: "Default"                                # Usually "Default"
     verify_ssl: false                                   # false for self-signed certs
   ```

3. **Update device settings:**
   ```yaml
   device:
     mac_address: "XX-XX-XX-XX-XX-XX"  # Your ER707 MAC address
     wan_port_id: 0                     # 0 = WAN1, 1 = WAN2
   ```

4. **Adjust monitoring settings (optional):**
   ```yaml
   monitoring:
     check_interval_seconds: 180        # How often to check (3 minutes)
     reconnect_wait_seconds: 5          # Wait between disconnect/reconnect
     max_reconnect_attempts: 3          # Retry attempts
   ```

5. **Save the file**

### Step 4: Find Your ER707 MAC Address

If you don't know your ER707's MAC address:

1. Log into Omada Controller web interface
2. Navigate to **Devices** → **Gateways**
3. Click on your ER707 device
4. Look for **MAC Address** in the device details
5. Copy it (format: `XX-XX-XX-XX-XX-XX`)
6. Paste into `config.yaml`

### Step 5: Test the Configuration

Run the troubleshooting utility to verify everything is configured correctly:

```bash
python troubleshoot.py
```

This will check:
- ✅ Python version
- ✅ Dependencies installed
- ✅ Configuration file valid
- ✅ Log directory accessible
- ✅ Network connectivity to controller
- ✅ Authentication credentials
- ✅ MAC address format
- ✅ IP detection logic

**All checks should pass.** If any fail, follow the recommendations provided.

### Step 6: Test the Connection

Run the connection test utility:

```bash
python test_connection.py
```

This performs a live test:
- Connects to Omada Controller
- Authenticates with your credentials
- Finds your ER707 device
- Retrieves current WAN IP
- Checks if it's public or private

**Expected output:**
```
==============================================================
ER707 WAN Monitor - Connection Test
==============================================================

📄 Loading configuration...
   ✅ Configuration loaded

==============================================================
Testing Omada Controller Connection
==============================================================

📡 Controller URL: https://192.168.1.10:8043
👤 Username: admin
🔒 SSL Verification: False

1️⃣  Testing basic connectivity...
   ✅ Controller is reachable (HTTP 200)

2️⃣  Testing authentication...
   ✅ Authentication successful
   🔑 Token received: eyJhbGciOiJIUzI1NiIs...

==============================================================
Testing ER707 Device Access
==============================================================

📱 Device MAC: A1-B2-C3-D4-E5-F6
🏢 Site Name: Default

1️⃣  Getting controller information...
   ✅ Controller ID: 1234567890abcdef

2️⃣  Getting site information...
   📋 Available sites:
      - Default (ID: 5f8a9b7c6d5e4f3a2b1c0d9e)
   ✅ Site 'Default' found: 5f8a9b7c6d5e4f3a2b1c0d9e

3️⃣  Getting device status...
   ✅ Device found!
   📱 Name: ER707-Main
   🔧 Model: ER707-M2
   📊 Status: Connected

4️⃣  Checking WAN IP...
   ✅ WAN IP detected: 203.0.113.45
   ✅ Public IP confirmed

==============================================================
✅ SUCCESS: All tests passed!
==============================================================

🚀 You can now run the main monitoring service:
   python er707_wan_monitor.py
```

### Step 7: Run the Monitor

If all tests pass, start the monitoring service:

```bash
python er707_wan_monitor.py
```

**You should see:**
```
2024-11-02 10:30:15 - INFO - Starting WAN IP monitoring service
2024-11-02 10:30:15 - INFO - Device MAC: A1-B2-C3-D4-E5-F6
2024-11-02 10:30:15 - INFO - WAN Port ID: 0
2024-11-02 10:30:15 - INFO - Check interval: 180 seconds
2024-11-02 10:30:16 - INFO - Successfully authenticated with Omada Controller
2024-11-02 10:30:17 - INFO - Controller ID: 1234567890abcdef
2024-11-02 10:30:17 - INFO - Site ID: 5f8a9b7c6d5e4f3a2b1c0d9e
2024-11-02 10:30:18 - INFO - Public IP confirmed: 203.0.113.45
```

The monitor is now running! It will check every 3 minutes (or your configured interval).

**To stop:** Press `Ctrl+C`

## 🔄 Running Continuously

For production use, you'll want the monitor to run continuously, even after reboots.

### Option A: Windows Service (Recommended for Windows)

1. Download NSSM from https://nssm.cc/download
2. Extract `nssm.exe` to a folder in your PATH
3. Edit `install_windows_service.ps1` and update the `$PythonPath` variable
4. Run PowerShell as Administrator
5. Execute: `.\install_windows_service.ps1`
6. Start the service: `nssm start ER707WANMonitor`

**Manage the service:**
```powershell
nssm status ER707WANMonitor    # Check status
nssm start ER707WANMonitor     # Start
nssm stop ER707WANMonitor      # Stop
nssm restart ER707WANMonitor   # Restart
```

### Option B: Linux Systemd Service (Recommended for Linux)

1. Edit `wan-monitor.service` and update paths and username
2. Copy to systemd directory:
   ```bash
   sudo cp wan-monitor.service /etc/systemd/system/
   ```
3. Reload systemd:
   ```bash
   sudo systemctl daemon-reload
   ```
4. Enable auto-start:
   ```bash
   sudo systemctl enable wan-monitor
   ```
5. Start the service:
   ```bash
   sudo systemctl start wan-monitor
   ```

**Manage the service:**
```bash
sudo systemctl status wan-monitor     # Check status
sudo systemctl start wan-monitor      # Start
sudo systemctl stop wan-monitor       # Stop
sudo systemctl restart wan-monitor    # Restart
sudo journalctl -u wan-monitor -f     # View logs
```

### Option C: Screen (Linux/macOS)

For quick deployment without setting up a service:

```bash
screen -S wan-monitor
python er707_wan_monitor.py
# Press Ctrl+A, then D to detach
```

**Reattach later:**
```bash
screen -r wan-monitor
```

### Option D: Background Process

Simple background execution:

```bash
nohup python er707_wan_monitor.py > output.log 2>&1 &
```

## 📊 Monitoring the Monitor

### Check Logs

Logs are written to `logs/wan_monitor.log` (or your configured path).

**View logs:**
```bash
# Linux/macOS
tail -f logs/wan_monitor.log

# Windows (PowerShell)
Get-Content logs/wan_monitor.log -Wait -Tail 20
```

### What to Look For

**Normal operation:**
```
2024-11-02 10:30:18 - INFO - Public IP confirmed: 203.0.113.45
2024-11-02 10:33:18 - DEBUG - Public IP stable: 203.0.113.45
```

**Private IP detected (remediation triggered):**
```
2024-11-02 10:36:18 - WARNING - Private IP detected: 192.168.1.100
2024-11-02 10:36:18 - WARNING - Private IP detected - initiating remediation
2024-11-02 10:36:18 - INFO - Starting WAN port reconnection sequence (port 0)
2024-11-02 10:36:19 - INFO - WAN port 0 disconnected successfully
2024-11-02 10:36:24 - INFO - WAN port 0 connected successfully
2024-11-02 10:36:54 - INFO - Remediation successful! Public IP obtained: 203.0.113.45
```

**Errors (need attention):**
```
2024-11-02 10:36:18 - ERROR - Failed to authenticate with Omada Controller
2024-11-02 10:36:18 - ERROR - All remediation attempts failed
```

## ❓ Troubleshooting

### Problem: "Login failed"

**Cause:** Incorrect credentials or URL

**Solution:**
1. Verify `controller_url` includes `https://` and port `:8043`
2. Check username and password in `config.yaml`
3. Try logging into Omada Controller web interface with same credentials
4. If using self-signed certificate, ensure `verify_ssl: false`

### Problem: "Device not found"

**Cause:** Incorrect MAC address or device not adopted

**Solution:**
1. Verify MAC address in Omada Controller
2. Ensure format is `XX-XX-XX-XX-XX-XX` (dashes or colons)
3. Check device is adopted and online in controller
4. Verify `site_name` matches your controller configuration

### Problem: "Could not extract WAN IP"

**Cause:** API response structure different than expected

**Solution:**
1. Enable DEBUG logging in `config.yaml`: `level: "DEBUG"`
2. Check logs for API response structure
3. WAN interface may not have an IP assigned
4. May need to adjust `extract_wan_ip()` method for your controller version

### Problem: "Remediation not working"

**Cause:** AT&T gateway not reassigning IP properly

**Solution:**
1. Increase `reconnect_wait_seconds` to 10
2. Increase `max_reconnect_attempts` to 5
3. Verify IP passthrough is configured correctly on BGW320-500
4. Ensure only one device is configured for IP passthrough
5. May need to reboot the AT&T gateway

### Problem: High CPU usage

**Cause:** Check interval too low

**Solution:**
1. Increase `check_interval_seconds` to 300 (5 minutes)
2. Check for error loops in logs

## 📚 Next Steps

Now that you're up and running:

1. **Monitor for a few days** - Observe how often private IPs occur
2. **Review logs regularly** - Check for any errors or issues
3. **Adjust settings** - Fine-tune intervals based on your needs
4. **Set up log rotation** - Prevent logs from growing too large
5. **Consider notifications** - Add email/SMS alerts (see README.md)

## 🎯 Success Checklist

- [x] Python 3.7+ installed
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] `config.yaml` configured with your settings
- [x] Troubleshooting script passes all checks
- [x] Connection test successful
- [x] Monitor running and detecting IP correctly
- [x] Service configured for continuous operation
- [x] Logs being written successfully

## 📖 Additional Resources

- **README.md** - Complete documentation
- **QUICKSTART.md** - 5-minute quick reference
- **PROJECT_SUMMARY.md** - Project overview
- **troubleshoot.py** - Diagnostic utility
- **test_connection.py** - Connection test utility

## 💡 Tips

1. **Start with INFO logging** - Switch to DEBUG only when troubleshooting
2. **Monitor logs initially** - Watch for the first few remediation events
3. **Document your settings** - Note what works best for your environment
4. **Keep config.yaml secure** - It contains your credentials
5. **Test remediation manually** - Verify it works before relying on automation

## 🎉 You're All Set!

The ER707 WAN Monitor is now protecting your network from private IP assignment issues. It will automatically detect and remediate the problem without manual intervention.

**Questions?** Check the README.md for detailed documentation.

**Issues?** Run `python troubleshoot.py` for diagnostics.

---

**Happy monitoring!** 🚀
