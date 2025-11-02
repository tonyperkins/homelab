# ER707 WAN Monitor - Deployment Checklist

Use this checklist to ensure proper deployment and operation.

## 📋 Pre-Deployment

### Environment Preparation
- [ ] Python 3.7+ installed and verified (`python --version`)
- [ ] Network access to Omada Controller confirmed
- [ ] Omada Controller admin credentials available
- [ ] ER707 device MAC address obtained

### Installation
- [ ] Project files downloaded/cloned
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] All dependencies verified (`python troubleshoot.py`)

## ⚙️ Configuration

### config.yaml Setup
- [ ] Copied `config.example.yaml` to `config.yaml` (if needed)
- [ ] Updated `omada.controller_url` with correct URL and port
- [ ] Updated `omada.username` with admin username
- [ ] Updated `omada.password` with admin password
- [ ] Updated `omada.site_name` (usually "Default")
- [ ] Set `omada.verify_ssl` appropriately (false for self-signed certs)
- [ ] Updated `device.mac_address` with ER707 MAC address
- [ ] Verified `device.wan_port_id` (0 for WAN1, 1 for WAN2)
- [ ] Reviewed `monitoring.check_interval_seconds` (default: 180)
- [ ] Reviewed `monitoring.reconnect_wait_seconds` (default: 5)
- [ ] Reviewed `monitoring.max_reconnect_attempts` (default: 3)
- [ ] Set `logging.level` appropriately (INFO for production)
- [ ] Verified `logging.file` path (default: logs/wan_monitor.log)

### Security
- [ ] Set restrictive permissions on `config.yaml` (chmod 600 on Linux)
- [ ] Verified `config.yaml` is in `.gitignore`
- [ ] Ensured credentials are not committed to version control

## 🧪 Testing

### Diagnostic Tests
- [ ] Ran `python troubleshoot.py` - all checks passed
- [ ] Ran `python test_connection.py` - connection successful
- [ ] Verified WAN IP is correctly detected
- [ ] Confirmed private vs public IP detection works

### Manual Test Run
- [ ] Started monitor manually (`python er707_wan_monitor.py`)
- [ ] Verified successful authentication
- [ ] Confirmed WAN IP detection in logs
- [ ] Observed at least one check cycle
- [ ] Stopped monitor cleanly (Ctrl+C)

### Optional: Test Remediation
- [ ] Manually triggered private IP scenario (if safe to test)
- [ ] Verified remediation sequence executes
- [ ] Confirmed public IP is obtained after remediation
- [ ] Reviewed logs for proper event recording

## 🚀 Production Deployment

### Service Installation

#### Windows Service (if applicable)
- [ ] Downloaded NSSM from https://nssm.cc/download
- [ ] Extracted nssm.exe to accessible location
- [ ] Updated `$PythonPath` in `install_windows_service.ps1`
- [ ] Ran PowerShell as Administrator
- [ ] Executed `.\install_windows_service.ps1`
- [ ] Started service (`nssm start ER707WANMonitor`)
- [ ] Verified service status (`nssm status ER707WANMonitor`)
- [ ] Confirmed service starts automatically on boot

#### Linux Systemd Service (if applicable)
- [ ] Updated paths in `wan-monitor.service`
- [ ] Updated username in `wan-monitor.service`
- [ ] Copied service file to `/etc/systemd/system/`
- [ ] Ran `sudo systemctl daemon-reload`
- [ ] Enabled service (`sudo systemctl enable wan-monitor`)
- [ ] Started service (`sudo systemctl start wan-monitor`)
- [ ] Verified service status (`sudo systemctl status wan-monitor`)
- [ ] Confirmed service starts automatically on boot

### Log Management
- [ ] Verified logs directory exists and is writable
- [ ] Confirmed logs are being written
- [ ] Set up log rotation (optional but recommended)
- [ ] Documented log file locations

## 📊 Post-Deployment Verification

### Immediate Checks (First Hour)
- [ ] Service is running
- [ ] Logs show successful authentication
- [ ] WAN IP is being detected correctly
- [ ] No error messages in logs
- [ ] Check interval is working as configured

### Short-Term Monitoring (First 24 Hours)
- [ ] Service remains running
- [ ] Multiple check cycles completed successfully
- [ ] No authentication failures
- [ ] No unexpected errors
- [ ] Log file size is reasonable

### Long-Term Monitoring (First Week)
- [ ] Service uptime is stable
- [ ] Remediation events (if any) are logged correctly
- [ ] Public IP is maintained consistently
- [ ] No resource issues (CPU, memory, disk)
- [ ] Log rotation is working (if configured)

## 🔍 Operational Readiness

### Monitoring Setup
- [ ] Know how to check service status
- [ ] Know how to view logs
- [ ] Know how to restart service if needed
- [ ] Documented log file locations
- [ ] Set up alerts (optional - email/SMS on remediation)

### Documentation
- [ ] Team knows where to find documentation
- [ ] Troubleshooting procedures documented
- [ ] Contact information for support documented
- [ ] Configuration backup created

### Maintenance Plan
- [ ] Log review schedule established
- [ ] Log rotation configured
- [ ] Backup procedure for configuration
- [ ] Update procedure documented
- [ ] Rollback procedure documented

## 🛠️ Troubleshooting Readiness

### Known Issues & Solutions
- [ ] Reviewed common issues in README.md
- [ ] Tested `troubleshoot.py` utility
- [ ] Tested `test_connection.py` utility
- [ ] Know how to enable DEBUG logging
- [ ] Know how to restart service

### Emergency Procedures
- [ ] Know how to stop the service
- [ ] Know how to manually reconnect WAN port
- [ ] Have Omada Controller access credentials
- [ ] Have AT&T gateway access (if needed)
- [ ] Documented escalation path

## 📈 Performance Baseline

### Initial Metrics
- [ ] Documented normal check interval
- [ ] Recorded typical log file growth rate
- [ ] Noted CPU usage (should be negligible)
- [ ] Noted memory usage (~20-30 MB)
- [ ] Documented API call frequency

### Expected Behavior
- [ ] Understand normal log output
- [ ] Know what remediation looks like in logs
- [ ] Understand error messages
- [ ] Know acceptable response times

## ✅ Final Sign-Off

### Deployment Complete
- [ ] All tests passed
- [ ] Service running in production
- [ ] Logs being written correctly
- [ ] Team trained on operation
- [ ] Documentation accessible
- [ ] Monitoring in place

### Stakeholder Approval
- [ ] Network team notified
- [ ] Change management completed (if required)
- [ ] Deployment documented
- [ ] Success criteria met

## 📅 Post-Deployment Schedule

### Daily (First Week)
- [ ] Check service status
- [ ] Review logs for errors
- [ ] Verify WAN IP detection

### Weekly (First Month)
- [ ] Review log files
- [ ] Check for remediation events
- [ ] Verify service uptime
- [ ] Review resource usage

### Monthly (Ongoing)
- [ ] Review overall performance
- [ ] Check for software updates
- [ ] Verify backup procedures
- [ ] Review and update documentation

## 🎯 Success Criteria

Deployment is successful when:
- ✅ Service runs continuously without intervention
- ✅ WAN IP is correctly detected every check cycle
- ✅ Private IP detection triggers remediation
- ✅ Remediation successfully obtains public IP
- ✅ Logs show normal operation
- ✅ No manual WAN port reconnections needed
- ✅ Network uptime improved

## 📞 Support Contacts

Document your support contacts:

| Role | Contact | Notes |
|------|---------|-------|
| Network Admin | __________ | Primary contact |
| Omada Controller | __________ | Controller access |
| AT&T Support | __________ | Gateway issues |
| Python/Script | __________ | Technical support |

## 📝 Deployment Notes

Use this space to document deployment-specific information:

**Deployment Date:** _______________

**Deployed By:** _______________

**Environment:** _______________

**Special Considerations:** 
_________________________________
_________________________________
_________________________________

**Issues Encountered:**
_________________________________
_________________________________
_________________________________

**Resolutions:**
_________________________________
_________________________________
_________________________________

---

**Checklist Version:** 1.0.0  
**Last Updated:** November 2, 2024

**Status:** [ ] Not Started  [ ] In Progress  [ ] Complete
