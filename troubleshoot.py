#!/usr/bin/env python3
"""
Troubleshooting utility for ER707 WAN Monitor.
Performs diagnostic checks and provides recommendations.

Usage: python troubleshoot.py
"""

import sys
import os
import yaml
import requests
import ipaddress
from pathlib import Path
from datetime import datetime

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section."""
    print(f"\n{'─'*70}")
    print(f"  {text}")
    print(f"{'─'*70}")


def check_python_version():
    """Check Python version."""
    print_section("1. Python Version Check")
    version = sys.version_info
    print(f"   Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("   ❌ FAIL: Python 3.7 or higher required")
        return False
    else:
        print("   ✅ PASS: Python version is compatible")
        return True


def check_dependencies():
    """Check required Python packages."""
    print_section("2. Dependency Check")
    
    required = {
        'requests': 'requests',
        'yaml': 'PyYAML',
        'ipaddress': 'ipaddress (built-in)'
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            __import__(module)
            print(f"   ✅ {package}: Installed")
        except ImportError:
            print(f"   ❌ {package}: NOT INSTALLED")
            all_ok = False
    
    if not all_ok:
        print("\n   💡 Install missing packages:")
        print("      pip install -r requirements.txt")
        return False
    
    return True


def check_config_file():
    """Check configuration file."""
    print_section("3. Configuration File Check")
    
    if not os.path.exists('config.yaml'):
        print("   ❌ FAIL: config.yaml not found")
        print("\n   💡 Create configuration file:")
        print("      1. Copy config.example.yaml to config.yaml")
        print("      2. Edit config.yaml with your settings")
        return False, None
    
    print("   ✅ config.yaml exists")
    
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("   ✅ config.yaml is valid YAML")
    except yaml.YAMLError as e:
        print(f"   ❌ FAIL: Invalid YAML syntax")
        print(f"      Error: {e}")
        return False, None
    
    # Check required fields
    required_fields = {
        'omada.controller_url': ['omada', 'controller_url'],
        'omada.username': ['omada', 'username'],
        'omada.password': ['omada', 'password'],
        'device.mac_address': ['device', 'mac_address']
    }
    
    missing = []
    for field_name, field_path in required_fields.items():
        value = config
        for key in field_path:
            value = value.get(key, {}) if isinstance(value, dict) else None
        
        if not value or value == "your_password_here" or value == "00-00-00-00-00-00":
            missing.append(field_name)
    
    if missing:
        print(f"   ⚠️  WARNING: Unconfigured fields:")
        for field in missing:
            print(f"      - {field}")
        print("\n   💡 Update these fields in config.yaml")
    else:
        print("   ✅ All required fields configured")
    
    return True, config


def check_log_directory(config):
    """Check log directory."""
    print_section("4. Log Directory Check")
    
    if not config:
        print("   ⏭️  SKIP: No configuration loaded")
        return True
    
    log_file = config.get('logging', {}).get('file', 'logs/wan_monitor.log')
    log_dir = os.path.dirname(log_file)
    
    if log_dir and not os.path.exists(log_dir):
        print(f"   ⚠️  Log directory does not exist: {log_dir}")
        try:
            os.makedirs(log_dir)
            print(f"   ✅ Created log directory: {log_dir}")
        except Exception as e:
            print(f"   ❌ FAIL: Could not create log directory")
            print(f"      Error: {e}")
            return False
    else:
        print(f"   ✅ Log directory ready: {log_dir or 'current directory'}")
    
    # Check write permissions
    test_file = os.path.join(log_dir or '.', '.write_test')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("   ✅ Log directory is writable")
    except Exception as e:
        print("   ❌ FAIL: Cannot write to log directory")
        print(f"      Error: {e}")
        return False
    
    return True


def check_network_connectivity(config):
    """Check network connectivity to Omada Controller."""
    print_section("5. Network Connectivity Check")
    
    if not config:
        print("   ⏭️  SKIP: No configuration loaded")
        return True
    
    controller_url = config.get('omada', {}).get('controller_url', '')
    
    if not controller_url:
        print("   ⏭️  SKIP: No controller URL configured")
        return True
    
    print(f"   Testing: {controller_url}")
    
    # Parse URL
    try:
        from urllib.parse import urlparse
        parsed = urlparse(controller_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        print(f"   Host: {host}")
        print(f"   Port: {port}")
    except Exception as e:
        print(f"   ❌ FAIL: Invalid URL format")
        print(f"      Error: {e}")
        return False
    
    # Test basic connectivity
    try:
        verify_ssl = config.get('omada', {}).get('verify_ssl', True)
        response = requests.get(
            f"{controller_url}/api/info",
            verify=verify_ssl,
            timeout=5
        )
        print(f"   ✅ Controller is reachable (HTTP {response.status_code})")
        return True
    except requests.exceptions.SSLError:
        print("   ❌ FAIL: SSL certificate error")
        print("\n   💡 Solutions:")
        print("      1. Set verify_ssl: false in config.yaml (for self-signed certs)")
        print("      2. Install valid SSL certificate on controller")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ FAIL: Cannot connect to {controller_url}")
        print("\n   💡 Check:")
        print("      1. Controller URL is correct")
        print("      2. Controller is running")
        print("      3. Network connectivity")
        print("      4. Firewall rules")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ FAIL: Connection timeout")
        print("\n   💡 Check:")
        print("      1. Controller is responding")
        print("      2. Network latency")
        return False
    except Exception as e:
        print(f"   ❌ FAIL: {type(e).__name__}")
        print(f"      Error: {e}")
        return False


def check_authentication(config):
    """Check Omada Controller authentication."""
    print_section("6. Authentication Check")
    
    if not config:
        print("   ⏭️  SKIP: No configuration loaded")
        return True
    
    controller_url = config.get('omada', {}).get('controller_url', '').rstrip('/')
    username = config.get('omada', {}).get('username', '')
    password = config.get('omada', {}).get('password', '')
    verify_ssl = config.get('omada', {}).get('verify_ssl', True)
    
    if not all([controller_url, username, password]):
        print("   ⏭️  SKIP: Credentials not configured")
        return True
    
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    
    try:
        session = requests.Session()
        login_url = f"{controller_url}/api/v2/login"
        payload = {
            "username": username,
            "password": password
        }
        
        response = session.post(
            login_url,
            json=payload,
            verify=verify_ssl,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('errorCode') == 0:
                print("   ✅ Authentication successful")
                return True
            else:
                print(f"   ❌ FAIL: Login failed")
                print(f"      Error: {data.get('msg', 'Unknown error')}")
                print("\n   💡 Check:")
                print("      1. Username is correct")
                print("      2. Password is correct")
                print("      3. Account is not locked")
                return False
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            print(f"      Response: {response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"   ❌ FAIL: {type(e).__name__}")
        print(f"      Error: {e}")
        return False


def check_mac_address_format(config):
    """Check MAC address format."""
    print_section("7. MAC Address Format Check")
    
    if not config:
        print("   ⏭️  SKIP: No configuration loaded")
        return True
    
    mac = config.get('device', {}).get('mac_address', '')
    
    if not mac or mac == "00-00-00-00-00-00":
        print("   ⏭️  SKIP: MAC address not configured")
        return True
    
    print(f"   MAC Address: {mac}")
    
    # Check format
    import re
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    
    if re.match(pattern, mac):
        print("   ✅ MAC address format is valid")
        return True
    else:
        print("   ❌ FAIL: Invalid MAC address format")
        print("\n   💡 Expected format:")
        print("      XX-XX-XX-XX-XX-XX or XX:XX:XX:XX:XX:XX")
        print("      Example: A1-B2-C3-D4-E5-F6")
        return False


def check_ip_detection_logic():
    """Test IP detection logic."""
    print_section("8. IP Detection Logic Test")
    
    test_cases = [
        ("192.168.1.1", True, "Private - Class C"),
        ("10.0.0.1", True, "Private - Class A"),
        ("172.16.0.1", True, "Private - Class B (start)"),
        ("172.31.255.254", True, "Private - Class B (end)"),
        ("172.15.0.1", False, "Public - Before Class B range"),
        ("172.32.0.1", False, "Public - After Class B range"),
        ("8.8.8.8", False, "Public - Google DNS"),
        ("1.1.1.1", False, "Public - Cloudflare DNS"),
        ("203.0.113.1", False, "Public - TEST-NET-3"),
    ]
    
    all_passed = True
    
    for ip_str, expected_private, description in test_cases:
        try:
            ip = ipaddress.ip_address(ip_str)
            private_ranges = [
                ipaddress.ip_network('10.0.0.0/8'),
                ipaddress.ip_network('172.16.0.0/12'),
                ipaddress.ip_network('192.168.0.0/16')
            ]
            is_private = any(ip in range for range in private_ranges)
            
            if is_private == expected_private:
                status = "✅"
            else:
                status = "❌"
                all_passed = False
            
            result = "Private" if is_private else "Public"
            print(f"   {status} {ip_str:15} → {result:7} ({description})")
        
        except Exception as e:
            print(f"   ❌ {ip_str:15} → Error: {e}")
            all_passed = False
    
    if all_passed:
        print("\n   ✅ All IP detection tests passed")
    else:
        print("\n   ❌ Some IP detection tests failed")
    
    return all_passed


def generate_report(results):
    """Generate summary report."""
    print_header("DIAGNOSTIC SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"\n   Total Checks: {total}")
    print(f"   Passed: {passed} ✅")
    print(f"   Failed: {failed} ❌")
    
    if failed == 0:
        print("\n   🎉 All checks passed! System is ready.")
        print("\n   Next steps:")
        print("      1. Run: python test_connection.py")
        print("      2. Run: python er707_wan_monitor.py")
    else:
        print("\n   ⚠️  Some checks failed. Review the output above.")
        print("\n   Failed checks:")
        for name, result in results.items():
            if not result:
                print(f"      - {name}")
    
    print("\n" + "="*70 + "\n")


def main():
    """Main troubleshooting function."""
    print_header("ER707 WAN Monitor - Troubleshooting Utility")
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {os.getcwd()}")
    
    results = {}
    
    # Run checks
    results['Python Version'] = check_python_version()
    results['Dependencies'] = check_dependencies()
    
    config_ok, config = check_config_file()
    results['Configuration File'] = config_ok
    
    results['Log Directory'] = check_log_directory(config)
    results['Network Connectivity'] = check_network_connectivity(config)
    results['Authentication'] = check_authentication(config)
    results['MAC Address Format'] = check_mac_address_format(config)
    results['IP Detection Logic'] = check_ip_detection_logic()
    
    # Generate report
    generate_report(results)
    
    # Exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == '__main__':
    main()
