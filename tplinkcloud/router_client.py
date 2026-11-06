"""
Router Web API client for TP-Link routers.

Based on Tether app decompilation - uses /cgi/ endpoints.
"""

import asyncio
import binascii
import hashlib
import re
import urllib.parse
from typing import Optional

import aiohttp
from aiohttp import CookieJar


class TPLinkRouterWebClient:
    """Client for TP-Link router local web interface."""
    
    def __init__(
        self,
        host: str = "192.168.0.1",
        username: str = "admin",
        password: str = None,
        verbose: bool = False
    ):
        self.host = host
        self.username = username
        self.password = password
        self.verbose = verbose
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._cookies: Optional[dict] = None
        self._stok: Optional[str] = None  # Session token
        
    @property
    def base_url(self) -> str:
        return f"http://{self.host}"
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            jar = CookieJar()
            self._session = aiohttp.ClientSession(
                cookie_jar=jar,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session
    
    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
    
    async def login(self, password: str = None) -> bool:
        """Login to the router's web interface."""
        password = password or self.password
        if not password:
            raise ValueError("Password required for router login")
        
        session = await self._get_session()
        
        # Try the standard CGI login endpoint
        login_url = f"{self.base_url}/cgi/login"
        params = {
            "UserName": self.username,
            "Passwd": password,
            "enableSSH": "1"
        }
        
        if self.verbose:
            print(f"POST {login_url} with params: {params}")
        
        try:
            async with session.post(login_url, params=params) as resp:
                text = await resp.text()
                
                if self.verbose:
                    print(f"Login response status: {resp.status}")
                    print(f"Login response: {text[:500]}")
                
                # Check for successful login
                if resp.status == 200:
                    # Check cookies for session
                    cookies = session.cookie_jar.filter_cookies(self.base_url)
                    
                    # Look for auth token in response
                    if "stok" in text.lower():
                        # Try to extract the token
                        match = re.search(r'stok[=/]?([^&"\'\s]+)', text, re.IGNORECASE)
                        if match:
                            self._stok = match.group(1)
                            if self.verbose:
                                print(f"Found token: {self._stok}")
                            return True
                    
                    # Check cookies
                    for cookie in cookies:
                        if 'stok' in cookie.key.lower():
                            self._stok = cookie.value
                            if self.verbose:
                                print(f"Found token in cookie: {self._stok}")
                            return True
                    
                    # Check if we have any cookies set
                    if cookies:
                        if self.verbose:
                            print(f"Cookies set: {[c.key for c in cookies]}")
                        return True
                        
                return False
                
        except aiohttp.ClientError as e:
            if self.verbose:
                print(f"Login error: {e}")
            return False
    
    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make authenticated request to router."""
        session = await self._get_session()
        
        url = f"{self.base_url}{path}"
        
        # Add token to URL if we have one
        if self._stok:
            # Some endpoints use token in query string
            if '?' in path:
                url = f"{url}&stok={self._stok}"
            else:
                url = f"{url}?stok={self._stok}"
        
        if self.verbose:
            print(f"{method} {url}")
        
        try:
            async with session.request(method, url, **kwargs) as resp:
                text = await resp.text()
                
                if self.verbose:
                    print(f"Response status: {resp.status}")
                    print(f"Response: {text[:1000]}")
                
                # Try to parse as JSON
                try:
                    return {"status": resp.status, "data": await resp.json()}
                except:
                    return {"status": resp.status, "text": text}
                    
        except aiohttp.ClientError as e:
            if self.verbose:
                print(f"Request error: {e}")
            return {"error": str(e)}
    
    async def get_connected_devices(self) -> list:
        """Get list of connected devices."""
        # Try various endpoints to find client list
        
        endpoints = [
            # Newer API style with token
            f"/api/connected-device/list",
            f"/api/online-devices",
            f"/api/device/online-list",
            # Try the /cgi/ endpoints
            f"/cgi/get_client_list",
            f"/cgi/get_stations",
            # Old style
            f"/data/conndev.json",
            f"/data/devlist.json",
            # Generic
            "/api/v2/device/list",
            "/api/v1/device-list",
        ]
        
        for endpoint in endpoints:
            result = await self._request("GET", endpoint)
            if self.verbose:
                print(f"Try {endpoint}: {result}")
            
            # Check if we got valid data
            if "data" in result:
                data = result.get("data", {})
                if isinstance(data, dict):
                    # Look for device list in common keys
                    for key in ["device_list", "client_list", "devices", "online_devices", "wlan_stations"]:
                        if key in data:
                            return data[key]
                    return data
                elif isinstance(data, list):
                    return data
        
        return []
    
    async def get_wireless_clients(self) -> list:
        """Get wireless clients specifically."""
        endpoints = [
            f"/api/wlan/station-list",
            f"/api/wireless/client-list",
            f"/api/wlan-stations",
            f"/cgi/wlan_stations",
        ]
        
        for endpoint in endpoints:
            result = await self._request("GET", endpoint)
            if self.verbose:
                print(f"Try {endpoint}: {result}")
            
            if "data" in result:
                data = result.get("data", {})
                if isinstance(data, dict):
                    for key in ["wlan_stations", "stations", "wireless_clients"]:
                        if key in data:
                            return data[key]
                    return data
        
        return []
    
    async def get_dhcp_clients(self) -> list:
        """Get DHCP client list."""
        endpoints = [
            "/api/dhcp-server/client-list",
            "/api/dhcp/clients",
            "/cgi/dhcp_clients",
        ]
        
        for endpoint in endpoints:
            result = await self._request("GET", endpoint)
            if self.verbose:
                print(f"Try {endpoint}: {result}")
            
            if "data" in result:
                data = result.get("data", {})
                if isinstance(data, dict):
                    for key in ["dhcp_clients", "client_list", "lease_list"]:
                        if key in data:
                            return data[key]
                    return data
        
        return []
    
    async def get_device_info(self) -> dict:
        """Get router device info."""
        result = await self._request("GET", "/api/device/info")
        
        if "data" in result:
            return result["data"]
        
        # Try alternative endpoints
        alt = await self._request("GET", "/api/router-status")
        if "data" in alt:
            return alt["data"]
        
        return result
    
    async def get_wan_status(self) -> dict:
        """Get WAN/Internet status."""
        result = await self._request("GET", "/api/wan/status")
        
        if "data" in result:
            return result["data"]
        return result
    
    async def get_wireless_status(self) -> dict:
        """Get wireless status."""
        result = await self._request("GET", "/api/wireless/status")
        
        if "data" in result:
            return result["data"]
        return result

    async def get_clients_mib(self) -> list:
        """
        Get connected clients using MIB-style request.
        Uses LAN_WLAN_ASSOC_DEV to get wireless clients.
        """
        result = await self._mib_request(
            "LAN_WLAN_ASSOC_DEV",
            ["AssociatedDeviceMACAddress", "AssociatedDeviceIPAddress",
             "X_TP_TotalPacketsSent", "X_TP_TotalPacketsReceived", "X_TP_HostName"]
        )
        
        if self.verbose:
            print(f"MIB clients result: {result}")
        
        clients = []
        if "text" in result and result.get("status") == 200:
            text = result["text"]
            lines = text.strip().split('\n')
            for line in lines[1:]:
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 2:
                        client = {
                            "mac": parts[0] if parts[0] else "",
                            "ip": parts[1] if len(parts) > 1 else "",
                        }
                        if len(parts) > 4:
                            client["hostname"] = parts[4]
                        clients.append(client)
        return clients

    async def _mib_request(self, mib_obj: str, fields: list) -> dict:
        """
        Make MIB-style request to router.
        """
        session = await self._get_session()
        mib_request = f"[{mib_obj}#0,0,0,0,0,0#1,0,0,0,0,0]0,{len(fields)}"
        for field in fields:
            mib_request += f"\n{field}"
        url = f"{self.base_url}/cgi"
        params = {"ctx": "1", "obj": mib_obj, "format": "nodev"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self._stok:
            params["stok"] = self._stok
        try:
            async with session.post(url, params=params, data=mib_request, headers=headers) as resp:
                return {"status": resp.status, "text": await resp.text()}
        except aiohttp.ClientError as e:
            return {"error": str(e)}


async def test_router():
    """Test the router client."""
    client = TPLinkRouterWebClient(
        host="192.168.0.1",
        username="admin",
        password="admin",  # Replace with your router password
        verbose=True
    )
    
    try:
        # Try to login
        success = await client.login()
        print(f"Login success: {success}")
        
        if success:
            # Try to get device info
            info = await client.get_device_info()
            print(f"Device info: {info}")
            
            # Try to get connected devices
            devices = await client.get_connected_devices()
            print(f"Connected devices: {devices}")
            
            wireless = await client.get_wireless_clients()
            print(f"Wireless clients: {wireless}")
        else:
            print("Login failed")
            
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_router())