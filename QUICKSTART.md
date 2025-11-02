# Quick Start Guide

Get the ER707 WAN Monitor running in 5 minutes.

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure

Edit `config.yaml` and update these critical fields:

```yaml
omada:
  controller_url: "https://YOUR_CONTROLLER_IP:8043"
  username: "YOUR_USERNAME"
  password: "YOUR_PASSWORD"
  verify_ssl: false  # Use false for self-signed certificates

device:
  mac_address: "YOUR_ER707_MAC_ADDRESS"  # Format: XX-XX-XX-XX-XX-XX
```

### Finding Your ER707 MAC Address

1. Open Omada Controller web interface
2. Go to **Devices** → **Gateways**
3. Click your ER707
4. Copy the MAC address shown

## Step 3: Test Run

```bash
python er707_wan_monitor.py
```

You should see:
```
2024-11-02 10:30:15 - INFO - Starting WAN IP monitoring service
2024-11-02 10:30:16 - INFO - Successfully authenticated with Omada Controller
2024-11-02 10:30:17 - INFO - Public IP confirmed: XXX.XXX.XXX.XXX
```

Press `Ctrl+C` to stop.

## Step 4: Run Continuously

### Option A: Screen (Linux/macOS)
```bash
screen -S wan-monitor
python er707_wan_monitor.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r wan-monitor
```

### Option B: Background Process
```bash
nohup python er707_wan_monitor.py > output.log 2>&1 &
```

### Option C: Windows Service
See README.md for NSSM setup instructions.

### Option D: Linux Systemd Service
See README.md for systemd setup instructions.

## Verification

Check the log file to confirm it's working:

```bash
tail -f logs/wan_monitor.log
```

## What Happens Next?

The monitor will:
1. Check WAN IP every 3 minutes (configurable)
2. If private IP detected (192.168.x.x, 10.x.x.x, 172.16-31.x.x):
   - Disconnect WAN port
   - Wait 5 seconds
   - Reconnect WAN port
   - Verify public IP obtained
3. Log all actions to `logs/wan_monitor.log`

## Troubleshooting

### "Login failed"
- Check controller URL includes `https://` and port `:8043`
- Verify username and password
- Set `verify_ssl: false` if using self-signed certificate

### "Could not extract WAN IP"
- Verify ER707 MAC address is correct
- Check device is online in Omada Controller
- Ensure WAN interface has an IP assigned

### "Failed to disconnect/connect WAN port"
- Verify user has admin privileges
- Check `wan_port_id` is correct (0 for WAN1)

## Need Help?

See full README.md for detailed documentation and advanced configuration options.
