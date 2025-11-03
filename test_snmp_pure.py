#!/usr/bin/env python3
"""
Test SNMP connectivity to ER707 using puresnmp
"""

from puresnmp import Client, V2C
from puresnmp.exc import Timeout, NoSuchOID
import asyncio

async def test_snmp():
    """Test SNMP connectivity."""
    
    print("=" * 60)
    print("ER707 SNMP Test")
    print("=" * 60)
    # Try both ER707 IP and Omada Controller IP
    test_ips = [
        ('192.168.50.1', 'ER707 LAN IP'),
        ('omada.homelab.lan', 'Omada Controller'),
    ]
    
    for ip, description in test_ips:
        print(f"\nTesting SNMP connection to {ip} ({description})...")
        print("Community string: monitoring2025!")
        print("-" * 60)
        
        # Create SNMP client with SNMPv2c credentials
        client = Client(ip.encode(), V2C(b'monitoring2025!'))
    
    # Test 1: Get system description
    print("\n1. Testing system description query...")
    try:
        # OID for sysDescr
        sys_descr = await client.get(b'1.3.6.1.2.1.1.1.0')
        print(f"✅ System: {sys_descr}")
    except Timeout:
        print("❌ Timeout - SNMP not responding")
        print("   Check: Is SNMP enabled? Is firewall blocking port 161?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Get IP addresses
    print("\n2. Querying IP addresses...")
    try:
        found_ips = []
        
        # Walk the IP address table
        # OID for ipAdEntAddr (IP-MIB::ipAdEntAddr)
        async for oid, value in client.walk(b'1.3.6.1.2.1.4.20.1.1'):
            ip = str(value)
            found_ips.append(ip)
            
            # Identify IP type
            if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                ip_type = "Private (LAN)"
            elif ip.startswith('127.'):
                ip_type = "Loopback"
            else:
                ip_type = "Public (WAN) ✓"
            
            print(f"  Found IP: {ip:15s} - {ip_type}")
        
        if found_ips:
            print(f"\n✅ Successfully retrieved {len(found_ips)} IP address(es)")
            
            # Identify likely WAN IP
            wan_ips = [ip for ip in found_ips 
                      if not ip.startswith(('192.168.', '10.', '172.', '127.'))]
            
            if wan_ips:
                print(f"\n🎯 WAN IP detected: {wan_ips[0]}")
                print(f"\nThis is the IP assigned to the ER707's WAN interface.")
            else:
                print("\n⚠️  No public WAN IP found")
                print("   The ER707's WAN interface has a private IP from the gateway.")
            
            return True
        else:
            print("❌ No IP addresses found")
            return False
            
    except Timeout:
        print("❌ Timeout during IP query")
        return False
    except NoSuchOID:
        print("❌ IP address OID not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    success = asyncio.run(test_snmp())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ SNMP is working!")
        print("\nYou can now use SNMP-based monitoring to check the")
        print("ER707's actual WAN interface IP (not the gateway's IP).")
    else:
        print("❌ SNMP test failed")
        print("\nTroubleshooting:")
        print("  1. Verify SNMP is enabled in ER707 (Omada Controller)")
        print("  2. Check community string is 'monitoring2025!'")
        print("  3. Ensure firewall allows UDP port 161")
    print("=" * 60)

if __name__ == '__main__':
    main()
