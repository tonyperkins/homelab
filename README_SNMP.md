# ER707 WAN Monitor - SNMP Version

## Overview

This is an SNMP-based monitoring solution for standalone TP-Link ER707 firewalls. It queries the ER707 directly via SNMP to get the **actual WAN interface IP** (not the gateway's public IP).

## ⚠️ Important Notes

### For Omada-Managed ER707 Devices
- **SNMP may not be accessible** when the ER707 is managed by Omada Controller
- Omada Controller's SNMP settings might only apply to the controller itself, not managed devices
- **Use the Omada API version instead** (`er707_wan_monitor.py`) for Omada-managed devices

### For Standalone ER707 Devices
- ✅ SNMP works great on standalone ER707 devices
- ✅ Enable SNMP directly in the ER707's web interface
- ✅ This version provides direct access to the WAN interface IP

## 🎯 Use Case

This SNMP version is specifically for:
- **Standalone ER707 devices** (not managed by Omada Controller)
- Users who need to know the **ER707's WAN IP specifically** (not the gateway's public IP)
- Scenarios where SSH is disabled or CLI is locked down
- Environments where API access is not available

## 📋 Requirements

- Python 3.7 or higher
- TP-Link ER707 firewall (standalone, not Omada-managed)
- SNMP enabled on ER707
- Network access to ER707 management interface

## 🔧 Installation

### 1. Install Python Dependencies

```bash
pip install puresnmp PyYAML
```

Or use the requirements file:
```bash
pip install -r requirements_snmp.txt
```

### 2. Enable SNMP on ER707

**For Standalone ER707:**
1. Log into ER707 web interface (e.g., `https://192.168.1.1`)
2. Navigate to **System Tools** → **SNMP**
3. Enable **SNMPv1 & SNMPv2c**
4. Set **Community String** (e.g., `monitoring2025!`)
   - Must be 10-64 characters
   - Combination of letters, numbers, and special symbols
   - No consecutive identical characters
5. Optionally set **Location** and **Contact**
6. Click **Apply**

**Note**: For Omada-managed devices, SNMP configuration in Omada Controller may not enable SNMP on the device itself.

### 3. Test SNMP Connectivity

```bash
python test_snmp_pure.py
```

Expected output:
```
============================================================
ER707 SNMP Test
============================================================

Testing SNMP connection to 192.168.50.1...
Community string: monitoring2025!
------------------------------------------------------------

1. Testing system description query...
✅ System: TP-Link ER707 v1.0

2. Querying IP addresses...
  Found IP: 192.168.50.1   - Private (LAN)
  Found IP: 107.217.163.105 - Public (WAN) ✓

✅ Successfully retrieved 2 IP address(es)

🎯 WAN IP detected: 107.217.163.105

This is the IP assigned to the ER707's WAN interface.
============================================================
✅ SNMP is working!
============================================================
```

## 🚀 Usage

### Configure the Monitor

Edit `config_snmp.yaml`:

```yaml
er707:
  host: "192.168.1.1"           # ER707 IP address
  community_string: "monitoring2025!"  # SNMP community string
  wan_port_id: 0                # WAN port (0 = WAN1, 1 = WAN2, etc.)

monitoring:
  check_interval_seconds: 180    # Check every 3 minutes
  max_reconnect_attempts: 3      # Try up to 3 times

logging:
  level: "INFO"
  file: "logs/wan_monitor_snmp.log"
```

### Run the Monitor

```bash
python er707_wan_monitor_snmp.py
```

## 🔍 How It Works

1. **SNMP Query**: Connects to ER707 via SNMP (UDP port 161)
2. **IP Detection**: Walks the IP address table (IP-MIB::ipAdEntAddr)
3. **Private IP Check**: Validates if IP is in RFC 1918 private ranges
4. **Remediation**: If private IP detected:
   - Logs the issue
   - Attempts to restart WAN interface (if supported via SNMP)
   - Or triggers external remediation (reboot, smart plug, etc.)

## 📝 SNMP OIDs Used

The monitor queries these SNMP OIDs:

- **System Description**: `1.3.6.1.2.1.1.1.0` (SNMPv2-MIB::sysDescr)
- **IP Addresses**: `1.3.6.1.2.1.4.20.1.1` (IP-MIB::ipAdEntAddr)
- **Interface Status**: `1.3.6.1.2.1.2.2.1` (IF-MIB::ifTable)

## ⚠️ Limitations

### SNMP Version Limitations
- **Read-only access**: SNMP typically provides read-only access
- **Cannot restart interfaces**: Most devices don't allow interface control via SNMP
- **Remediation requires alternative method**: Use web UI, SSH, or smart plug for WAN restart

### Omada-Managed Devices
- **SNMP may not be accessible** on Omada-managed ER707 devices
- **Use Omada API version instead** for managed devices
- **Standalone mode required** for full SNMP functionality

### Network Requirements
- **UDP port 161** must be accessible
- **Firewall rules** must allow SNMP traffic
- **Community string** must match exactly

## 🐛 Troubleshooting

### "Timeout - SNMP not responding"

**Possible causes:**
1. SNMP is not enabled on ER707
2. Wrong community string
3. Firewall blocking UDP port 161
4. Device is Omada-managed (SNMP not accessible)

**Solutions:**
- Verify SNMP is enabled in ER707 web interface
- Check community string matches exactly
- Ensure firewall allows SNMP (UDP 161)
- For Omada-managed devices, use Omada API version

### "No public WAN IP found"

This is **expected behavior** when:
- ER707's WAN interface has a private IP from the gateway
- This is the condition you're monitoring for!
- The monitor should trigger remediation in this case

### "IP address OID not found"

**Possible causes:**
- ER707 firmware doesn't support standard IP-MIB
- SNMP version mismatch

**Solutions:**
- Try SNMPv1 instead of SNMPv2c
- Check ER707 firmware version and SNMP support

## 🔄 Comparison: SNMP vs Other Methods

| Feature | SNMP | Omada API | SSH | External IP Check |
|---------|------|-----------|-----|-------------------|
| **Requires Omada Controller** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Shows ER707 WAN IP** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No (shows gateway) |
| **Works on Omada-Managed** | ⚠️ Maybe | ✅ Yes | ⚠️ Limited | ❌ No |
| **Can Restart Interface** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Setup Complexity** | ✅ Simple | ⚠️ Medium | ⚠️ Medium | ✅ Simple |
| **Reliability** | ✅ High | ✅ High | ⚠️ Medium | ⚠️ Low |

## 🚀 Recommended Approach by Scenario

### Scenario 1: Omada-Managed ER707
**Use**: Omada API version (`er707_wan_monitor.py`)
- Full control via API
- Can restart WAN interface
- Most reliable

### Scenario 2: Standalone ER707 with SNMP
**Use**: SNMP version (`er707_wan_monitor_snmp.py`)
- Direct device query
- No controller needed
- Read-only monitoring

### Scenario 3: Standalone ER707 without SNMP
**Use**: SSH version (`er707_wan_monitor_ssh.py`)
- CLI-based monitoring
- Can restart interface
- Requires SSH access

### Scenario 4: Any Setup, Simple Detection
**Use**: External IP check (`wan_monitor_simple.py`)
- Universal compatibility
- Cannot distinguish gateway vs ER707 IP
- Requires external remediation

## 📦 Files

- `test_snmp_pure.py` - SNMP connectivity test script
- `er707_wan_monitor_snmp.py` - Main SNMP monitoring script (to be created)
- `config_snmp.yaml` - Configuration file for SNMP version
- `requirements_snmp.txt` - Python dependencies
- `README_SNMP.md` - This file

## 🔐 Security Best Practices

1. **Use strong community strings**: 10+ characters, mixed case, numbers, symbols
2. **Restrict SNMP access**: Configure firewall to only allow SNMP from monitoring host
3. **Use SNMPv3 if available**: Provides encryption and authentication (ER707 may not support)
4. **Read-only community**: Use read-only community strings (default for most setups)
5. **Monitor access logs**: Review SNMP access logs regularly

## 📄 License

MIT License - Free to use and modify

---

## 🆘 Support

For issues specific to:
- **SNMP configuration**: Check TP-Link ER707 documentation
- **Omada-managed devices**: Use Omada API version instead
- **This script**: Open an issue in the repository

---

**Note**: This SNMP version is tested with standalone ER707 devices. For Omada-managed devices, the Omada API version (`er707_wan_monitor.py`) is recommended for better reliability and full control.
