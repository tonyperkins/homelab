#!/usr/bin/env python3
"""
Test script to verify Omada Controller connection and device access.
Run this before starting the main monitoring service to validate configuration.

Usage: python test_connection.py
"""

import sys
import yaml
import requests
from pathlib import Path

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings()


def load_config(config_path='config.yaml'):
    """Load configuration file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing configuration file: {e}")
        sys.exit(1)


def test_controller_connection(config):
    """Test connection to Omada Controller."""
    print("\n" + "="*60)
    print("Testing Omada Controller Connection")
    print("="*60)
    
    base_url = config['omada']['controller_url'].rstrip('/')
    username = config['omada']['username']
    password = config['omada']['password']
    verify_ssl = config['omada'].get('verify_ssl', True)
    
    print(f"\n📡 Controller URL: {base_url}")
    print(f"👤 Username: {username}")
    print(f"🔒 SSL Verification: {verify_ssl}")
    
    # Test basic connectivity
    print("\n1️⃣  Testing basic connectivity...")
    try:
        response = requests.get(
            f"{base_url}/api/info",
            verify=verify_ssl,
            timeout=5
        )
        print(f"   ✅ Controller is reachable (HTTP {response.status_code})")
    except requests.exceptions.SSLError:
        print("   ⚠️  SSL certificate error - consider setting verify_ssl: false")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to {base_url}")
        print("   💡 Check URL, port, and network connectivity")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Connection timeout")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test authentication
    print("\n2️⃣  Testing authentication...")
    try:
        session = requests.Session()
        login_url = f"{base_url}/api/v2/login"
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
                token = data.get('result', {}).get('token')
                print(f"   ✅ Authentication successful")
                print(f"   🔑 Token received: {token[:20]}..." if token else "   ⚠️  No token in response")
                return session, verify_ssl
            else:
                print(f"   ❌ Login failed: {data.get('msg', 'Unknown error')}")
                print("   💡 Check username and password")
                return False
        else:
            print(f"   ❌ Login failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return False


def test_device_access(session, verify_ssl, config):
    """Test access to ER707 device."""
    print("\n" + "="*60)
    print("Testing ER707 Device Access")
    print("="*60)
    
    base_url = config['omada']['controller_url'].rstrip('/')
    device_mac = config['device']['mac_address']
    site_name = config['omada'].get('site_name', 'Default')
    
    print(f"\n📱 Device MAC: {device_mac}")
    print(f"🏢 Site Name: {site_name}")
    
    # Get controller ID
    print("\n1️⃣  Getting controller information...")
    try:
        info_url = f"{base_url}/api/v2/controllers"
        response = session.get(info_url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('errorCode') == 0:
                controllers = data.get('result', [])
                if controllers:
                    controller_id = controllers[0].get('omadacId')
                    print(f"   ✅ Controller ID: {controller_id}")
                else:
                    print("   ❌ No controllers found")
                    return False
            else:
                print(f"   ❌ Error: {data.get('msg')}")
                return False
        else:
            print(f"   ❌ Failed to get controller info: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Get site ID
    print("\n2️⃣  Getting site information...")
    try:
        sites_url = f"{base_url}/{controller_id}/api/v2/sites"
        response = session.get(sites_url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('errorCode') == 0:
                sites = data.get('result', {}).get('data', [])
                site_id = None
                
                print(f"   📋 Available sites:")
                for site in sites:
                    site_name_found = site.get('name')
                    site_id_found = site.get('id')
                    print(f"      - {site_name_found} (ID: {site_id_found})")
                    if site_name_found == site_name:
                        site_id = site_id_found
                
                if site_id:
                    print(f"   ✅ Site '{site_name}' found: {site_id}")
                else:
                    print(f"   ❌ Site '{site_name}' not found")
                    print("   💡 Update site_name in config.yaml to match one of the above")
                    return False
            else:
                print(f"   ❌ Error: {data.get('msg')}")
                return False
        else:
            print(f"   ❌ Failed to get sites: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Get device status
    print("\n3️⃣  Getting device status...")
    try:
        device_url = f"{base_url}/{controller_id}/api/v2/sites/{site_id}/gateways/{device_mac}"
        response = session.get(device_url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('errorCode') == 0:
                device_info = data.get('result', {})
                device_name = device_info.get('name', 'Unknown')
                device_model = device_info.get('model', 'Unknown')
                device_status = device_info.get('status', 'Unknown')
                
                print(f"   ✅ Device found!")
                print(f"   📱 Name: {device_name}")
                print(f"   🔧 Model: {device_model}")
                print(f"   📊 Status: {device_status}")
                
                # Try to extract WAN IP
                print("\n4️⃣  Checking WAN IP...")
                wan_ip = None
                
                # Try different possible paths
                if 'wan' in device_info:
                    wan_info = device_info.get('wan', {})
                    wan_ip = wan_info.get('ipAddr') or wan_info.get('ip') or wan_info.get('ipv4')
                
                if not wan_ip and 'networkStatus' in device_info:
                    network_status = device_info.get('networkStatus', {})
                    wan_status = network_status.get('wan', {})
                    wan_ip = wan_status.get('ipAddr') or wan_status.get('ip')
                
                if not wan_ip and 'ports' in device_info:
                    ports = device_info.get('ports', [])
                    for port in ports:
                        if port.get('type') == 'wan' or port.get('name', '').lower().startswith('wan'):
                            wan_ip = port.get('ipAddr') or port.get('ip')
                            if wan_ip:
                                break
                
                if wan_ip:
                    print(f"   ✅ WAN IP detected: {wan_ip}")
                    
                    # Check if private IP
                    import ipaddress
                    try:
                        ip_obj = ipaddress.ip_address(wan_ip)
                        private_ranges = [
                            ipaddress.ip_network('10.0.0.0/8'),
                            ipaddress.ip_network('172.16.0.0/12'),
                            ipaddress.ip_network('192.168.0.0/16')
                        ]
                        is_private = any(ip_obj in range for range in private_ranges)
                        
                        if is_private:
                            print(f"   ⚠️  WARNING: Private IP detected (RFC 1918)")
                            print(f"   💡 This is the condition that triggers remediation")
                        else:
                            print(f"   ✅ Public IP confirmed")
                    except:
                        pass
                else:
                    print(f"   ⚠️  Could not extract WAN IP from device status")
                    print(f"   💡 This may indicate an API structure issue")
                    print(f"\n   📋 Device status structure (for debugging):")
                    import json
                    print(json.dumps(device_info, indent=2)[:1000] + "...")
                
                return True
            else:
                print(f"   ❌ Error: {data.get('msg')}")
                return False
        else:
            print(f"   ❌ Device not found: HTTP {response.status_code}")
            print("   💡 Check MAC address format (XX-XX-XX-XX-XX-XX)")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Main test function."""
    print("\n" + "="*60)
    print("ER707 WAN Monitor - Connection Test")
    print("="*60)
    
    # Load configuration
    print("\n📄 Loading configuration...")
    config = load_config()
    print("   ✅ Configuration loaded")
    
    # Test controller connection
    result = test_controller_connection(config)
    if not result:
        print("\n" + "="*60)
        print("❌ FAILED: Cannot connect to Omada Controller")
        print("="*60)
        sys.exit(1)
    
    session, verify_ssl = result
    
    # Test device access
    if not test_device_access(session, verify_ssl, config):
        print("\n" + "="*60)
        print("❌ FAILED: Cannot access ER707 device")
        print("="*60)
        sys.exit(1)
    
    # Success
    print("\n" + "="*60)
    print("✅ SUCCESS: All tests passed!")
    print("="*60)
    print("\n🚀 You can now run the main monitoring service:")
    print("   python er707_wan_monitor.py")
    print()


if __name__ == '__main__':
    main()
