#!/usr/bin/env python3
"""
ER707 WAN IP Monitor and Auto-Remediation Utility

Monitors the WAN interface of an ER707 firewall managed by Omada Controller.
Automatically detects private IP assignment and triggers WAN port reconnection
to obtain a proper public IP address.

Author: Automated Network Management
License: MIT
"""

import requests
import json
import time
import logging
import ipaddress
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import yaml


class OmadaController:
    """Interface for Omada Controller API operations."""
    
    def __init__(self, base_url: str, username: str, password: str, site_name: str = "Default", verify_ssl: bool = True):
        """
        Initialize Omada Controller connection.
        
        Args:
            base_url: Controller URL (e.g., https://192.168.1.10:8043)
            username: Controller admin username
            password: Controller admin password
            site_name: Site name in controller (default: "Default")
            verify_ssl: Verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.site_name = site_name
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.token = None
        self.controller_id = None
        self.site_id = None
        
        # Disable SSL warnings if verification is disabled
        if not verify_ssl:
            requests.packages.urllib3.disable_warnings()
    
    def login(self) -> bool:
        """
        Authenticate with Omada Controller.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            login_url = f"{self.base_url}/api/v2/login"
            payload = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(
                login_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('errorCode') == 0:
                    self.token = data.get('result', {}).get('token')
                    logging.info("Successfully authenticated with Omada Controller")
                    
                    # Get controller ID
                    self._get_controller_info()
                    return True
            
            logging.error(f"Login failed: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            logging.error(f"Login exception: {e}")
            return False
    
    def _get_controller_info(self) -> None:
        """Retrieve controller and site information."""
        try:
            # Get controller ID
            info_url = f"{self.base_url}/api/v2/controllers"
            response = self.session.get(info_url, verify=self.verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('errorCode') == 0:
                    controllers = data.get('result', [])
                    if controllers:
                        self.controller_id = controllers[0].get('omadacId')
                        logging.info(f"Controller ID: {self.controller_id}")
            
            # Get site ID
            if self.controller_id:
                sites_url = f"{self.base_url}/{self.controller_id}/api/v2/sites"
                response = self.session.get(sites_url, verify=self.verify_ssl, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('errorCode') == 0:
                        sites = data.get('result', {}).get('data', [])
                        for site in sites:
                            if site.get('name') == self.site_name:
                                self.site_id = site.get('id')
                                logging.info(f"Site ID: {self.site_id}")
                                break
        
        except Exception as e:
            logging.error(f"Error getting controller info: {e}")
    
    def get_wan_status(self, device_mac: str) -> Optional[Dict[str, Any]]:
        """
        Get WAN interface status for specified device.
        
        Args:
            device_mac: MAC address of the ER707 device
            
        Returns:
            Dictionary with WAN status information or None if failed
        """
        try:
            if not self.controller_id or not self.site_id:
                logging.error("Controller or Site ID not available")
                return None
            
            # Get device status
            device_url = f"{self.base_url}/{self.controller_id}/api/v2/sites/{self.site_id}/gateways/{device_mac}"
            response = self.session.get(device_url, verify=self.verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('errorCode') == 0:
                    return data.get('result', {})
            
            logging.warning(f"Failed to get WAN status: {response.status_code}")
            return None
            
        except Exception as e:
            logging.error(f"Exception getting WAN status: {e}")
            return None
    
    def disconnect_wan_port(self, device_mac: str, port_id: int = 0) -> bool:
        """
        Disconnect WAN port on the device.
        
        Args:
            device_mac: MAC address of the ER707 device
            port_id: WAN port ID (default: 0 for WAN1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.controller_id or not self.site_id:
                logging.error("Controller or Site ID not available")
                return False
            
            # Disable WAN port
            port_url = f"{self.base_url}/{self.controller_id}/api/v2/sites/{self.site_id}/gateways/{device_mac}/ports/{port_id}"
            payload = {
                "enable": False
            }
            
            response = self.session.patch(
                port_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('errorCode') == 0:
                    logging.info(f"WAN port {port_id} disconnected successfully")
                    return True
            
            logging.error(f"Failed to disconnect WAN port: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            logging.error(f"Exception disconnecting WAN port: {e}")
            return False
    
    def connect_wan_port(self, device_mac: str, port_id: int = 0) -> bool:
        """
        Connect WAN port on the device.
        
        Args:
            device_mac: MAC address of the ER707 device
            port_id: WAN port ID (default: 0 for WAN1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.controller_id or not self.site_id:
                logging.error("Controller or Site ID not available")
                return False
            
            # Enable WAN port
            port_url = f"{self.base_url}/{self.controller_id}/api/v2/sites/{self.site_id}/gateways/{device_mac}/ports/{port_id}"
            payload = {
                "enable": True
            }
            
            response = self.session.patch(
                port_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('errorCode') == 0:
                    logging.info(f"WAN port {port_id} connected successfully")
                    return True
            
            logging.error(f"Failed to connect WAN port: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            logging.error(f"Exception connecting WAN port: {e}")
            return False
    
    def reconnect_wan_port(self, device_mac: str, port_id: int = 0, wait_time: int = 5) -> bool:
        """
        Perform disconnect-reconnect sequence on WAN port.
        
        Args:
            device_mac: MAC address of the ER707 device
            port_id: WAN port ID (default: 0 for WAN1)
            wait_time: Seconds to wait between disconnect and reconnect
            
        Returns:
            bool: True if successful, False otherwise
        """
        logging.info(f"Starting WAN port reconnection sequence (port {port_id})")
        
        # Disconnect
        if not self.disconnect_wan_port(device_mac, port_id):
            return False
        
        # Wait
        logging.info(f"Waiting {wait_time} seconds before reconnecting...")
        time.sleep(wait_time)
        
        # Reconnect
        if not self.connect_wan_port(device_mac, port_id):
            return False
        
        logging.info("WAN port reconnection sequence completed")
        return True


class IPValidator:
    """Utility class for IP address validation."""
    
    # RFC 1918 private IP ranges
    PRIVATE_RANGES = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16')
    ]
    
    @staticmethod
    def is_private_ip(ip_str: str) -> bool:
        """
        Check if IP address is in RFC 1918 private range.
        
        Args:
            ip_str: IP address string
            
        Returns:
            bool: True if private IP, False otherwise
        """
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # Check against RFC 1918 ranges
            for private_range in IPValidator.PRIVATE_RANGES:
                if ip in private_range:
                    return True
            
            return False
            
        except ValueError:
            logging.error(f"Invalid IP address format: {ip_str}")
            return False
    
    @staticmethod
    def is_valid_ip(ip_str: str) -> bool:
        """
        Validate IP address format.
        
        Args:
            ip_str: IP address string
            
        Returns:
            bool: True if valid IP format, False otherwise
        """
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False


class WANMonitor:
    """Main monitoring and remediation service."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize WAN monitor.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        self.controller = OmadaController(
            base_url=self.config['omada']['controller_url'],
            username=self.config['omada']['username'],
            password=self.config['omada']['password'],
            site_name=self.config['omada'].get('site_name', 'Default'),
            verify_ssl=self.config['omada'].get('verify_ssl', True)
        )
        
        self.device_mac = self.config['device']['mac_address']
        self.wan_port_id = self.config['device'].get('wan_port_id', 0)
        self.check_interval = self.config['monitoring'].get('check_interval_seconds', 300)
        self.reconnect_wait = self.config['monitoring'].get('reconnect_wait_seconds', 5)
        self.max_reconnect_attempts = self.config['monitoring'].get('max_reconnect_attempts', 3)
        
        self.last_known_ip = None
        self.consecutive_failures = 0
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.error(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def _setup_logging(self) -> None:
        """Configure logging system."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        log_file = log_config.get('file', 'wan_monitor.log')
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def extract_wan_ip(self, device_status: Dict[str, Any]) -> Optional[str]:
        """
        Extract WAN IP address from device status.
        
        Args:
            device_status: Device status dictionary from API
            
        Returns:
            WAN IP address string or None if not found
        """
        try:
            # Try common paths in API response
            # Note: Actual path may vary based on Omada Controller version
            
            # Check WAN interface status
            wan_info = device_status.get('wan', {})
            if isinstance(wan_info, dict):
                ip = wan_info.get('ipAddr') or wan_info.get('ip') or wan_info.get('ipv4')
                if ip:
                    return ip
            
            # Check network status
            network_status = device_status.get('networkStatus', {})
            wan_status = network_status.get('wan', {})
            if isinstance(wan_status, dict):
                ip = wan_status.get('ipAddr') or wan_status.get('ip')
                if ip:
                    return ip
            
            # Check ports array
            ports = device_status.get('ports', [])
            for port in ports:
                if port.get('type') == 'wan' or port.get('name', '').lower().startswith('wan'):
                    ip = port.get('ipAddr') or port.get('ip')
                    if ip:
                        return ip
            
            logging.warning("Could not extract WAN IP from device status")
            logging.debug(f"Device status structure: {json.dumps(device_status, indent=2)}")
            return None
            
        except Exception as e:
            logging.error(f"Error extracting WAN IP: {e}")
            return None
    
    def check_wan_ip(self) -> Optional[str]:
        """
        Check current WAN IP address.
        
        Returns:
            Current WAN IP or None if check failed
        """
        device_status = self.controller.get_wan_status(self.device_mac)
        
        if not device_status:
            logging.warning("Failed to retrieve device status")
            return None
        
        wan_ip = self.extract_wan_ip(device_status)
        
        if wan_ip and IPValidator.is_valid_ip(wan_ip):
            return wan_ip
        
        return None
    
    def remediate_private_ip(self) -> bool:
        """
        Perform remediation when private IP is detected.
        
        Returns:
            bool: True if remediation successful, False otherwise
        """
        logging.warning("Private IP detected - initiating remediation")
        
        for attempt in range(1, self.max_reconnect_attempts + 1):
            logging.info(f"Remediation attempt {attempt}/{self.max_reconnect_attempts}")
            
            # Perform reconnection
            if self.controller.reconnect_wan_port(
                self.device_mac,
                self.wan_port_id,
                self.reconnect_wait
            ):
                # Wait for interface to stabilize
                logging.info("Waiting 30 seconds for WAN interface to stabilize...")
                time.sleep(30)
                
                # Check if we now have a public IP
                new_ip = self.check_wan_ip()
                
                if new_ip:
                    if not IPValidator.is_private_ip(new_ip):
                        logging.info(f"Remediation successful! Public IP obtained: {new_ip}")
                        self.last_known_ip = new_ip
                        self.consecutive_failures = 0
                        return True
                    else:
                        logging.warning(f"Still have private IP after attempt {attempt}: {new_ip}")
                else:
                    logging.warning(f"Could not verify IP after attempt {attempt}")
            else:
                logging.error(f"Reconnection failed on attempt {attempt}")
            
            # Wait before next attempt (except on last attempt)
            if attempt < self.max_reconnect_attempts:
                logging.info("Waiting 60 seconds before next attempt...")
                time.sleep(60)
        
        logging.error("All remediation attempts failed")
        self.consecutive_failures += 1
        return False
    
    def monitor_loop(self) -> None:
        """Main monitoring loop."""
        logging.info("Starting WAN IP monitoring service")
        logging.info(f"Device MAC: {self.device_mac}")
        logging.info(f"WAN Port ID: {self.wan_port_id}")
        logging.info(f"Check interval: {self.check_interval} seconds")
        
        # Initial authentication
        if not self.controller.login():
            logging.error("Failed to authenticate with Omada Controller")
            sys.exit(1)
        
        while True:
            try:
                # Check WAN IP
                current_ip = self.check_wan_ip()
                
                if current_ip:
                    is_private = IPValidator.is_private_ip(current_ip)
                    
                    if is_private:
                        logging.warning(f"Private IP detected: {current_ip}")
                        self.remediate_private_ip()
                    else:
                        # Public IP - all good
                        if current_ip != self.last_known_ip:
                            logging.info(f"Public IP confirmed: {current_ip}")
                            self.last_known_ip = current_ip
                        else:
                            logging.debug(f"Public IP stable: {current_ip}")
                        
                        self.consecutive_failures = 0
                else:
                    logging.warning("Could not determine WAN IP")
                    self.consecutive_failures += 1
                
                # Check if we need to re-authenticate
                if self.consecutive_failures >= 3:
                    logging.info("Multiple failures detected, re-authenticating...")
                    if self.controller.login():
                        self.consecutive_failures = 0
                    else:
                        logging.error("Re-authentication failed")
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logging.info("Monitoring service stopped by user")
                break
            except Exception as e:
                logging.error(f"Unexpected error in monitoring loop: {e}", exc_info=True)
                time.sleep(60)  # Wait before retrying after error


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ER707 WAN IP Monitor and Auto-Remediation Utility'
    )
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    monitor = WANMonitor(config_path=args.config)
    monitor.monitor_loop()


if __name__ == '__main__':
    main()
