# ER707 WAN Monitor (SSH Version - No Omada Controller Required)

A standalone monitoring solution for TP-Link ER707 firewalls accessed directly via SSH. This version **does not require Omada Controller** and works with standalone ER707 devices.

## 🎯 Use Case

This SSH-based version is for:
- ✅ Standalone ER707 devices (not managed by Omada Controller)
- ✅ Users who prefer direct device access
- ✅ Environments without Omada Controller infrastructure
- ✅ Testing/development scenarios

## 📋 Requirements

- Python 3.7 or higher
- TP-Link ER707 firewall with SSH enabled
- Network access to ER707 management interface
- SSH credentials (admin username/password)

## 🔧 Installation

### 1. Install Python Dependencies

```bash
pip install paramiko PyYAML
```

Or use the requirements file:
```bash
pip install -r requirements_ssh.txt
```

### 2. Enable SSH on ER707

If SSH is not already enabled on your ER707:

1. Log into ER707 web interface
2. Navigate to **System Tools** → **Administration**
3. Enable **SSH Service**
4. Set SSH port (default: 22)
5. Save settings

### 3. Configure the Monitor

Edit `config_ssh.yaml`:

```yaml
er707:
  host: "192.168.1.1"           # Your ER707 IP address
  username: "admin"              # SSH username
  password: "your_password"      # SSH password
  ssh_port: 22                   # SSH port
  wan_interface: "wan1"          # WAN interface (wan1, wan2, etc.)

monitoring:
  check_interval_seconds: 180    # Check every 3 minutes
  reconnect_wait_seconds: 5      # Wait 5s between shutdown/no-shutdown
  max_reconnect_attempts: 3      # Try up to 3 times

logging:
  level: "INFO"
  file: "logs/wan_monitor_ssh.log"
```

## 🚀 Usage

### Run the Monitor

```bash
python er707_wan_monitor_ssh.py
```

### Run with Custom Config

```bash
python er707_wan_monitor_ssh.py --config /path/to/custom_config.yaml
```

### Run in Background (Linux/macOS)

```bash
nohup python er707_wan_monitor_ssh.py > output.log 2>&1 &
```

## 🔍 How It Works

1. **SSH Connection**: Connects to ER707 via SSH using provided credentials
2. **IP Detection**: Executes CLI commands to retrieve WAN IP address
3. **Private IP Check**: Validates if IP is in RFC 1918 private ranges
4. **Remediation**: If private IP detected:
   - Enters configuration mode
   - Executes `shutdown` on WAN interface
   - Waits configured interval
   - Executes `no shutdown` to re-enable interface
   - Verifies new IP assignment

## 📝 CLI Commands Used

The monitor uses these ER707 CLI commands:

```bash
# Get WAN IP
show interface wan1

# Restart WAN interface
configure terminal
interface wan1
shutdown
exit
exit

# (wait 5 seconds)

configure terminal
interface wan1
no shutdown
exit
exit
```

## ⚠️ Important Notes

### SSH Access
- Ensure SSH is enabled on your ER707
- Use strong passwords for SSH access
- Consider using SSH keys instead of passwords (future enhancement)
- Restrict SSH access to trusted networks

### CLI Command Compatibility
- Commands tested on ER707 firmware 1.2.x
- CLI syntax may vary between firmware versions
- If commands fail, check ER707 documentation for your firmware version

### Limitations vs Omada API Version
- **No centralized management**: Must run on each ER707 or accessible host
- **CLI parsing**: More fragile than API (output format may change)
- **Limited visibility**: Can't see other devices or network-wide status
- **SSH overhead**: Maintains persistent SSH connection

## 🔐 Security Best Practices

1. **Secure credentials**: Store `config_ssh.yaml` with restricted permissions
   ```bash
   chmod 600 config_ssh.yaml  # Linux/macOS
   ```

2. **Use SSH keys** (recommended enhancement):
   - Generate SSH key pair
   - Add public key to ER707
   - Modify script to use key authentication

3. **Restrict SSH access**:
   - Configure ER707 to only allow SSH from monitoring host
   - Use firewall rules to limit SSH access

4. **Monitor logs**: Regularly review `wan_monitor_ssh.log` for unauthorized access

## 🐛 Troubleshooting

### "SSH authentication failed"
- Verify username and password in `config_ssh.yaml`
- Ensure SSH is enabled on ER707
- Check if account is locked (too many failed attempts)

### "Connection timeout"
- Verify ER707 IP address is correct
- Check network connectivity to ER707
- Ensure SSH port is correct (default: 22)
- Check firewall rules

### "Could not parse IP from output"
- CLI output format may have changed
- Enable DEBUG logging to see actual output
- May need to adjust regex patterns in `get_wan_ip()` method

### "Command execution error"
- CLI commands may vary by firmware version
- Check ER707 documentation for correct syntax
- Try commands manually via SSH to verify

## 🔄 Comparison: SSH vs Omada API

| Feature | SSH Version | Omada API Version |
|---------|-------------|-------------------|
| **Requires Omada Controller** | ❌ No | ✅ Yes |
| **Centralized Management** | ❌ No | ✅ Yes |
| **API Stability** | ⚠️ CLI may change | ✅ More stable |
| **Setup Complexity** | ✅ Simpler | ⚠️ More complex |
| **Multi-device Support** | ❌ One at a time | ✅ Multiple devices |
| **Firmware Dependency** | ⚠️ CLI syntax varies | ✅ API more consistent |

## 🚀 Future Enhancements

Potential improvements for the SSH version:

1. **SSH Key Authentication**: Use keys instead of passwords
2. **Command Auto-Discovery**: Detect firmware version and adjust commands
3. **Multiple WAN Ports**: Support monitoring multiple WAN interfaces
4. **Health Checks**: Monitor interface statistics, errors, etc.
5. **Notifications**: Email/SMS alerts on remediation events
6. **Web Dashboard**: Simple web UI for status monitoring

## 📦 Files

- `er707_wan_monitor_ssh.py` - Main monitoring script
- `config_ssh.yaml` - Configuration file
- `requirements_ssh.txt` - Python dependencies
- `README_SSH.md` - This file

## 🆘 Support

For issues specific to:
- **ER707 CLI commands**: Check TP-Link ER707 documentation
- **SSH connectivity**: Verify ER707 SSH configuration
- **This script**: Open an issue in the repository

## 📄 License

MIT License - Free to use and modify

---

**Note**: This is an alternative implementation for users without Omada Controller. If you have Omada Controller, use the API-based version (`er707_wan_monitor.py`) for better reliability and features.
