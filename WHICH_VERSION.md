# Which Version Should You Use?

This project provides **two versions** of the ER707 WAN Monitor. Choose based on your setup:

## 🎯 Quick Decision

**Do you have Omada Controller managing your ER707?**
- ✅ **YES** → Use the **Omada API Version** (recommended)
- ❌ **NO** → Use the **SSH Version**

---

## 📊 Detailed Comparison

### Omada API Version (`er707_wan_monitor.py`)

**✅ Use this if:**
- You have Omada Controller (hardware or software)
- Your ER707 is adopted/managed by Omada
- You want centralized management
- You manage multiple TP-Link devices

**Pros:**
- ✅ Stable API interface
- ✅ Works with both hardware and software Omada Controllers
- ✅ Can manage multiple devices from one controller
- ✅ Structured JSON responses (easier to parse)
- ✅ Better error handling
- ✅ Consistent across firmware versions

**Cons:**
- ❌ Requires Omada Controller infrastructure
- ❌ More complex initial setup
- ❌ API discovery needed for different controller versions

**Files:**
- `er707_wan_monitor.py`
- `config.yaml`
- `requirements.txt`
- `README.md`

**Dependencies:**
```bash
pip install requests PyYAML urllib3
```

---

### SSH Version (`er707_wan_monitor_ssh.py`)

**✅ Use this if:**
- You DON'T have Omada Controller
- Your ER707 is standalone (not managed)
- You want direct device access
- You prefer simpler setup

**Pros:**
- ✅ No Omada Controller required
- ✅ Direct device access
- ✅ Simpler setup (just SSH credentials)
- ✅ Works immediately with standalone ER707
- ✅ Lower infrastructure requirements

**Cons:**
- ❌ CLI parsing (more fragile)
- ❌ Commands may vary between firmware versions
- ❌ Requires SSH to be enabled on ER707
- ❌ One monitor instance per device
- ❌ Less reliable than API

**Files:**
- `er707_wan_monitor_ssh.py`
- `config_ssh.yaml`
- `requirements_ssh.txt`
- `README_SSH.md`

**Dependencies:**
```bash
pip install paramiko PyYAML
```

---

## 🔄 Can I Switch Between Versions?

**Yes!** Both versions solve the same problem using different methods:

### From SSH → Omada API
If you later adopt your ER707 into Omada Controller:
1. Stop the SSH version
2. Configure `config.yaml` for Omada API version
3. Run `er707_wan_monitor.py`

### From Omada API → SSH
If you remove Omada Controller:
1. Stop the Omada API version
2. Enable SSH on ER707
3. Configure `config_ssh.yaml`
4. Run `er707_wan_monitor_ssh.py`

---

## 📋 Feature Matrix

| Feature | Omada API | SSH |
|---------|-----------|-----|
| **No Omada Controller Required** | ❌ | ✅ |
| **Centralized Management** | ✅ | ❌ |
| **Multi-Device Support** | ✅ | ❌ |
| **API Stability** | ✅ High | ⚠️ Medium |
| **Setup Complexity** | ⚠️ Medium | ✅ Low |
| **Firmware Dependency** | ✅ Low | ⚠️ High |
| **Error Handling** | ✅ Better | ⚠️ Basic |
| **Performance** | ✅ Efficient | ✅ Efficient |
| **Security** | ✅ Token-based | ✅ SSH |

---

## 💡 Recommendations

### For Home Users
- **With Omada Controller**: Use Omada API version
- **Without Omada Controller**: Use SSH version

### For Small Business
- **Recommended**: Omada API version (even if you need to set up Omada Controller)
- **Reason**: Better management, scalability, and reliability

### For Enterprise
- **Required**: Omada API version
- **Reason**: Centralized management, audit trails, and consistency

### For Testing/Development
- **Either version works**
- **SSH version** is faster to set up for quick tests

---

## 🚀 Getting Started

### Omada API Version

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure:**
   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml with your Omada Controller details
   ```

3. **Test:**
   ```bash
   python test_connection.py
   ```

4. **Run:**
   ```bash
   python er707_wan_monitor.py
   ```

### SSH Version

1. **Install dependencies:**
   ```bash
   pip install -r requirements_ssh.txt
   ```

2. **Enable SSH on ER707:**
   - Log into ER707 web interface
   - System Tools → Administration
   - Enable SSH Service

3. **Configure:**
   ```bash
   # Edit config_ssh.yaml with your ER707 IP and credentials
   ```

4. **Run:**
   ```bash
   python er707_wan_monitor_ssh.py
   ```

---

## ❓ Still Not Sure?

**Ask yourself:**

1. **Do I currently use Omada Controller?**
   - YES → Omada API version
   - NO → Continue to question 2

2. **Am I planning to use Omada Controller in the future?**
   - YES → Consider Omada API version (set up controller now)
   - NO → SSH version

3. **Do I manage multiple TP-Link devices?**
   - YES → Omada API version (worth setting up controller)
   - NO → SSH version is fine

4. **Do I need the most reliable solution?**
   - YES → Omada API version
   - NO → Either version works

---

## 📞 Need Help Deciding?

Both versions solve the AT&T BGW320-500 IP passthrough issue effectively. The main difference is the management approach:

- **Omada API** = Centralized, scalable, enterprise-ready
- **SSH** = Direct, simple, standalone

Choose based on your current infrastructure and future plans!
