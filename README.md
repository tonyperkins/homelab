# ER707 WAN IP Monitor & Auto-Remediation Utility

An automated monitoring solution for TP-Link ER707 firewalls managed by Omada Controller. This utility continuously monitors the WAN interface to detect private IP assignment issues and automatically performs remediation by reconnecting the WAN port.

## Problem Statement

When using AT&T fiber with a BGW320-500 gateway in IP passthrough mode (bridge mode unavailable), the ER707 occasionally receives a private IP address (RFC 1918 range) instead of the expected public IP. This disrupts network connectivity and requires manual intervention to resolve.

## Solution

This utility provides:
- **Continuous monitoring** of WAN IP address assignment
- **Automatic detection** of private IP addresses (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- **Automated remediation** via WAN port disconnect/reconnect sequence
- **Comprehensive logging** for troubleshooting and audit trails
- **Configurable behavior** to match your network requirements

## Features

✅ **RFC 1918 Detection** - Identifies all private IP ranges  
✅ **Omada Controller Integration** - Uses official API for reliable control  
✅ **Automatic Remediation** - No manual intervention required  
✅ **Retry Logic** - Multiple attempts with configurable intervals  
✅ **Detailed Logging** - File and console output with multiple log levels  
✅ **Error Handling** - Graceful handling of network interruptions and API failures  
✅ **Configurable Intervals** - Balance between responsiveness and resource usage  
✅ **SSL Support** - Works with self-signed certificates  

## Requirements

- Python 3.7 or higher
- TP-Link ER707 firewall
- Omada Controller (hardware or software)
- Network access to Omada Controller
- Admin credentials for Omada Controller

## Installation

### 1. Clone or Download

Download this repository to your monitoring server or workstation.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests PyYAML urllib3
```

### 3. Configure the Utility

Edit `config.yaml` with your environment details:

```yaml
omada:
  controller_url: "https://192.168.1.10:8043"  # Your controller URL
  username: "admin"                             # Your admin username
  password: "your_password_here"                # Your admin password
  site_name: "Default"                          # Your site name
  verify_ssl: false                             # false for self-signed certs

device:
  mac_address: "XX-XX-XX-XX-XX-XX"              # Your ER707 MAC address
  wan_port_id: 0                                # 0 for WAN1, 1 for WAN2

monitoring:
  check_interval_seconds: 180                   # Check every 3 minutes
  reconnect_wait_seconds: 5                     # Wait 5s between disconnect/reconnect
  max_reconnect_attempts: 3                     # Try up to 3 times

logging:
  level: "INFO"                                 # DEBUG, INFO, WARNING, ERROR
  file: "logs/wan_monitor.log"                  # Log file path
```

### 4. Find Your ER707 MAC Address

1. Log into Omada Controller
2. Navigate to **Devices** → **Gateways**
3. Click on your ER707 device
4. Copy the MAC address (format: XX-XX-XX-XX-XX-XX)
5. Paste it into `config.yaml` under `device.mac_address`

## Usage

### Run Manually

```bash
python er707_wan_monitor.py
```

### Run with Custom Config

```bash
python er707_wan_monitor.py --config /path/to/custom_config.yaml
```

### Run as Background Service (Linux/macOS)

Using `screen`:
```bash
screen -S wan-monitor
python er707_wan_monitor.py
# Press Ctrl+A, then D to detach
```

Using `nohup`:
```bash
nohup python er707_wan_monitor.py > output.log 2>&1 &
```

### Run as Windows Service

See [Windows Service Setup](#windows-service-setup) section below.

## How It Works

1. **Authentication**: Connects to Omada Controller using provided credentials
2. **Monitoring Loop**: 
   - Queries ER707 device status via Omada API
   - Extracts current WAN IP address
   - Validates IP against RFC 1918 private ranges
3. **Detection**: When private IP is detected:
   - Logs warning with detected IP
   - Initiates remediation sequence
4. **Remediation**:
   - Disables WAN port via API
   - Waits configured interval (default: 5 seconds)
   - Re-enables WAN port via API
   - Waits for interface stabilization (30 seconds)
   - Verifies new IP assignment
5. **Retry Logic**: If remediation fails, retries up to configured maximum attempts
6. **Logging**: All events logged to file and console with timestamps

## Configuration Options

### Check Interval

`check_interval_seconds` determines how often the WAN IP is checked:
- **60 seconds (1 min)**: Fast detection, more API calls
- **180 seconds (3 min)**: Balanced (recommended)
- **300 seconds (5 min)**: Conservative, fewer API calls

### Reconnect Wait Time

`reconnect_wait_seconds` is the delay between disconnect and reconnect:
- **5 seconds**: Standard (recommended)
- **10 seconds**: More conservative
- Increase if experiencing issues with rapid reconnection

### Max Reconnect Attempts

`max_reconnect_attempts` controls retry behavior:
- **3 attempts**: Standard (recommended)
- Increase for more persistent remediation
- Each attempt includes 60-second wait between tries

### Log Levels

- **DEBUG**: Verbose output, includes API responses and detailed flow
- **INFO**: Normal operation, logs checks and remediation actions
- **WARNING**: Only logs issues and remediation events
- **ERROR**: Only critical errors

## Logging

Logs are written to both file and console with the following format:
```
2024-11-02 10:30:15 - INFO - Starting WAN IP monitoring service
2024-11-02 10:30:16 - INFO - Successfully authenticated with Omada Controller
2024-11-02 10:30:17 - INFO - Public IP confirmed: 203.0.113.45
2024-11-02 10:35:17 - WARNING - Private IP detected: 192.168.1.100
2024-11-02 10:35:17 - WARNING - Private IP detected - initiating remediation
2024-11-02 10:35:18 - INFO - WAN port 0 disconnected successfully
2024-11-02 10:35:23 - INFO - WAN port 0 connected successfully
2024-11-02 10:35:53 - INFO - Remediation successful! Public IP obtained: 203.0.113.45
```

## Troubleshooting

### Cannot Connect to Omada Controller

**Symptoms**: `Login failed` or connection timeout errors

**Solutions**:
1. Verify `controller_url` is correct (include https:// and port)
2. Check network connectivity to controller
3. Verify credentials are correct
4. If using self-signed certificate, ensure `verify_ssl: false`

### Cannot Find Device

**Symptoms**: `Failed to get WAN status` or device not found errors

**Solutions**:
1. Verify MAC address format (XX-XX-XX-XX-XX-XX)
2. Check device is adopted in Omada Controller
3. Verify `site_name` matches your controller configuration
4. Check device is online and managed

### WAN IP Not Detected

**Symptoms**: `Could not extract WAN IP from device status`

**Solutions**:
1. Enable DEBUG logging to see API response structure
2. Check WAN interface is configured and connected
3. Verify device has obtained an IP (even if private)
4. API response structure may vary by controller version

### Remediation Not Working

**Symptoms**: Private IP persists after reconnection attempts

**Solutions**:
1. Increase `reconnect_wait_seconds` to 10
2. Increase `max_reconnect_attempts` to 5
3. Check AT&T gateway IP passthrough configuration
4. Verify only one device is configured for IP passthrough
5. May need to reboot BGW320-500 gateway

### Permission Errors

**Symptoms**: `Failed to disconnect/connect WAN port`

**Solutions**:
1. Verify user has admin privileges in Omada Controller
2. Check user is not read-only
3. Verify API permissions are enabled

## Windows Service Setup

To run as a Windows service, you can use NSSM (Non-Sucking Service Manager):

### 1. Download NSSM
Download from: https://nssm.cc/download

### 2. Install Service
```powershell
nssm install WANMonitor "C:\Python\python.exe" "C:\path\to\er707_wan_monitor.py"
nssm set WANMonitor AppDirectory "C:\path\to\homelab"
nssm set WANMonitor DisplayName "ER707 WAN Monitor"
nssm set WANMonitor Description "Monitors ER707 WAN IP and performs auto-remediation"
nssm set WANMonitor Start SERVICE_AUTO_START
```

### 3. Start Service
```powershell
nssm start WANMonitor
```

### 4. Check Status
```powershell
nssm status WANMonitor
```

## Linux Systemd Service Setup

### 1. Create Service File

Create `/etc/systemd/system/wan-monitor.service`:

```ini
[Unit]
Description=ER707 WAN IP Monitor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/homelab
ExecStart=/usr/bin/python3 /path/to/homelab/er707_wan_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable wan-monitor
sudo systemctl start wan-monitor
```

### 3. Check Status

```bash
sudo systemctl status wan-monitor
sudo journalctl -u wan-monitor -f
```

## API Compatibility Notes

This utility is designed for Omada Controller API v2. The API structure may vary between controller versions:

- **Tested with**: Omada Controller 5.x
- **Should work with**: Omada Controller 4.x and 5.x
- **May require adjustments**: Older versions (3.x)

If you encounter issues with WAN IP detection, enable DEBUG logging to see the API response structure and adjust the `extract_wan_ip()` method accordingly.

## Security Considerations

1. **Credentials**: Store `config.yaml` securely with restricted permissions
   ```bash
   chmod 600 config.yaml  # Linux/macOS
   ```

2. **SSL Verification**: Use `verify_ssl: true` when possible with valid certificates

3. **Network Access**: Restrict access to the monitoring server

4. **Logging**: Log files may contain IP addresses and network topology information

## Advanced Configuration

### Multiple WAN Ports

If using WAN failover with multiple WAN ports, you can run multiple instances:

```bash
# Monitor WAN1
python er707_wan_monitor.py --config config_wan1.yaml

# Monitor WAN2
python er707_wan_monitor.py --config config_wan2.yaml
```

Each config file should specify different `wan_port_id` values.

### Custom Check Logic

You can modify `extract_wan_ip()` in the script to handle different API response structures or add custom validation logic.

### Notifications

To add email or webhook notifications, modify the `remediate_private_ip()` method to call your notification service when remediation occurs.

## Performance Impact

- **API Calls**: One API call per check interval (default: every 3 minutes)
- **Network Impact**: Minimal - small JSON requests/responses
- **CPU Usage**: Negligible - script sleeps between checks
- **Memory Usage**: ~20-30 MB typical

## Contributing

Feel free to submit issues or pull requests for:
- Additional API compatibility
- Enhanced error handling
- New features (notifications, metrics, etc.)
- Documentation improvements

## License

MIT License - Free to use and modify

## Support

For issues specific to:
- **Omada Controller**: Consult TP-Link documentation
- **ER707 Configuration**: Check TP-Link support forums
- **AT&T Gateway**: Contact AT&T support
- **This Utility**: Open an issue in this repository

## Changelog

### Version 1.0.0 (2024-11-02)
- Initial release
- RFC 1918 private IP detection
- Automatic WAN port reconnection
- Omada Controller API integration
- Comprehensive logging
- Configurable monitoring intervals
- Retry logic with multiple attempts

## Acknowledgments

Created to solve the AT&T BGW320-500 IP passthrough issue affecting ER707 users.

---

**Note**: This utility is not officially affiliated with or endorsed by TP-Link. Use at your own risk.
