#!/usr/bin/env python3
"""
ER707 WAN IP Monitor (SSH-Based - No Omada Controller Required)

Monitors the WAN interface of a standalone ER707 via SSH.
Automatically detects private IP assignment and triggers WAN port reconnection.

Author: Automated Network Management
License: MIT
"""

import paramiko
import time
import logging
import ipaddress
import sys
import re
from datetime import datetime
from typing import Optional
from pathlib import Path
import yaml


class ER707SSH:
    """SSH interface for ER707 device."""
    
    def __init__(self, host: str, username: str, password: str, port: int = 22):
        """
        Initialize SSH connection to ER707.
        
        Args:
            host: ER707 IP address or hostname
            username: SSH username (usually 'admin')
            password: SSH password
            port: SSH port (default: 22)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh_client = None
    
    def connect(self) -> bool:
        """
        Establish SSH connection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )
            
            logging.info(f"Successfully connected to ER707 at {self.host}")
            return True
            
        except paramiko.AuthenticationException:
            logging.error("SSH authentication failed - check username/password")
            return False
        except paramiko.SSHException as e:
            logging.error(f"SSH connection error: {e}")
            return False
        except Exception as e:
            logging.error(f"Connection exception: {e}")
            return False
    
    def disconnect(self):
        """Close SSH connection."""
        if self.ssh_client:
            self.ssh_client.close()
            logging.debug("SSH connection closed")
    
    def execute_command(self, command: str, timeout: int = 30) -> Optional[str]:
        """
        Execute command via SSH.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Command output or None if failed
        """
        try:
            if not self.ssh_client:
                logging.error("SSH client not connected")
                return None
            
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                logging.debug(f"Command stderr: {error}")
            
            return output
            
        except Exception as e:
            logging.error(f"Command execution error: {e}")
            return None
    
    def get_wan_ip(self, wan_interface: str = "wan1") -> Optional[str]:
        """
        Get WAN IP address via CLI.
        
        Args:
            wan_interface: WAN interface name (wan1, wan2, etc.)
            
        Returns:
            WAN IP address or None if not found
        """
        try:
            # Try multiple commands to find WAN IP
            commands_to_try = [
                f"show interface {wan_interface}",
                "show ip interface brief",
                "show interface brief",
                "show wan",
                "show running-config interface wan1",
                "ifconfig wan1",
                "ip addr show wan1",
            ]
            
            output = None
            for cmd in commands_to_try:
                logging.debug(f"Trying command: {cmd}")
                output = self.execute_command(cmd)
                if output and len(output.strip()) > 10:  # Got some meaningful output
                    logging.debug(f"Command '{cmd}' returned {len(output)} bytes")
                    logging.debug(f"Output preview: {output[:300]}")
                    break
            
            if not output:
                logging.warning("Could not get interface information from any command")
                return None
            
            # Parse output for IP address
            # Look for patterns like "inet 107.217.163.105" or "IP Address: 107.217.163.105"
            ip_patterns = [
                r'inet\s+(\d+\.\d+\.\d+\.\d+)',
                r'IP Address:\s*(\d+\.\d+\.\d+\.\d+)',
                r'ipv4:\s*(\d+\.\d+\.\d+\.\d+)',
                r'address\s+(\d+\.\d+\.\d+\.\d+)',
                r'ip:\s*(\d+\.\d+\.\d+\.\d+)',
                r'(\d+\.\d+\.\d+\.\d+)/\d+',  # CIDR notation
            ]
            
            for pattern in ip_patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    ip = match.group(1)
                    if ip != "0.0.0.0" and not ip.startswith("127."):
                        logging.debug(f"Found WAN IP: {ip}")
                        return ip
            
            logging.warning(f"Could not parse IP from output")
            logging.info(f"Full output for debugging:\n{output}")
            return None
            
        except Exception as e:
            logging.error(f"Error getting WAN IP: {e}")
            return None
    
    def restart_wan_interface(self, wan_interface: str = "wan1", wait_time: int = 5) -> bool:
        """
        Restart WAN interface (disable then enable).
        
        Args:
            wan_interface: WAN interface name
            wait_time: Seconds to wait between disable/enable
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logging.info(f"Restarting WAN interface: {wan_interface}")
            
            # Enter configuration mode and disable interface
            commands = [
                "configure terminal",
                f"interface {wan_interface}",
                "shutdown",
                "exit",
                "exit"
            ]
            
            for cmd in commands:
                output = self.execute_command(cmd)
                logging.debug(f"Command '{cmd}': {output[:100] if output else 'No output'}")
            
            logging.info(f"WAN interface disabled, waiting {wait_time} seconds...")
            time.sleep(wait_time)
            
            # Re-enable interface
            commands = [
                "configure terminal",
                f"interface {wan_interface}",
                "no shutdown",
                "exit",
                "exit"
            ]
            
            for cmd in commands:
                output = self.execute_command(cmd)
                logging.debug(f"Command '{cmd}': {output[:100] if output else 'No output'}")
            
            logging.info("WAN interface re-enabled")
            return True
            
        except Exception as e:
            logging.error(f"Error restarting WAN interface: {e}")
            return False


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
        """Check if IP address is in RFC 1918 private range."""
        try:
            ip = ipaddress.ip_address(ip_str)
            for private_range in IPValidator.PRIVATE_RANGES:
                if ip in private_range:
                    return True
            return False
        except ValueError:
            logging.error(f"Invalid IP address format: {ip_str}")
            return False
    
    @staticmethod
    def is_valid_ip(ip_str: str) -> bool:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False


class WANMonitor:
    """Main monitoring and remediation service."""
    
    def __init__(self, config_path: str = "config_ssh.yaml"):
        """Initialize WAN monitor."""
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        self.er707 = ER707SSH(
            host=self.config['er707']['host'],
            username=self.config['er707']['username'],
            password=self.config['er707']['password'],
            port=self.config['er707'].get('ssh_port', 22)
        )
        
        self.wan_interface = self.config['er707'].get('wan_interface', 'wan1')
        self.check_interval = self.config['monitoring'].get('check_interval_seconds', 300)
        self.reconnect_wait = self.config['monitoring'].get('reconnect_wait_seconds', 5)
        self.max_reconnect_attempts = self.config['monitoring'].get('max_reconnect_attempts', 3)
        
        self.last_known_ip = None
        self.consecutive_failures = 0
    
    def _load_config(self, config_path: str) -> dict:
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
        log_file = log_config.get('file', 'wan_monitor_ssh.log')
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def check_wan_ip(self) -> Optional[str]:
        """Check current WAN IP address."""
        wan_ip = self.er707.get_wan_ip(self.wan_interface)
        
        if wan_ip and IPValidator.is_valid_ip(wan_ip):
            return wan_ip
        
        return None
    
    def remediate_private_ip(self) -> bool:
        """Perform remediation when private IP is detected."""
        logging.warning("Private IP detected - initiating remediation")
        
        for attempt in range(1, self.max_reconnect_attempts + 1):
            logging.info(f"Remediation attempt {attempt}/{self.max_reconnect_attempts}")
            
            # Restart WAN interface
            if self.er707.restart_wan_interface(self.wan_interface, self.reconnect_wait):
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
                logging.error(f"Interface restart failed on attempt {attempt}")
            
            if attempt < self.max_reconnect_attempts:
                logging.info("Waiting 60 seconds before next attempt...")
                time.sleep(60)
        
        logging.error("All remediation attempts failed")
        self.consecutive_failures += 1
        return False
    
    def monitor_loop(self) -> None:
        """Main monitoring loop."""
        logging.info("Starting WAN IP monitoring service (SSH mode)")
        logging.info(f"ER707 Host: {self.config['er707']['host']}")
        logging.info(f"WAN Interface: {self.wan_interface}")
        logging.info(f"Check interval: {self.check_interval} seconds")
        
        # Initial connection
        if not self.er707.connect():
            logging.error("Failed to connect to ER707 via SSH")
            sys.exit(1)
        
        try:
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
                    
                    # Reconnect SSH if multiple failures
                    if self.consecutive_failures >= 3:
                        logging.info("Multiple failures detected, reconnecting SSH...")
                        self.er707.disconnect()
                        time.sleep(5)
                        if self.er707.connect():
                            self.consecutive_failures = 0
                        else:
                            logging.error("SSH reconnection failed")
                    
                    # Wait for next check
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logging.error(f"Error in monitoring loop: {e}", exc_info=True)
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            logging.info("Monitoring service stopped by user")
        finally:
            self.er707.disconnect()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ER707 WAN IP Monitor (SSH-Based - No Omada Controller)'
    )
    parser.add_argument(
        '-c', '--config',
        default='config_ssh.yaml',
        help='Path to configuration file (default: config_ssh.yaml)'
    )
    
    args = parser.parse_args()
    
    monitor = WANMonitor(config_path=args.config)
    monitor.monitor_loop()


if __name__ == '__main__':
    main()
