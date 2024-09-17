import asyncio
import json
import logging
from aiohttp import ClientSession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def _do_login(session: ClientSession, email: str, password: str):
    """Login to the MyEldom server."""
    url = 'https://myeldom.com/api/Account/Login'
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Connection": "Keep-Alive",
    }
    login_data = {"Email": email, "Password": password}

    try:
        async with session.post(url, data=login_data, headers=headers, allow_redirects=False) as resp:
            if resp.status == 302:
                _LOGGER.info("Login successful!")
                return True
            else:
                _LOGGER.error(f"Login failed with status {resp.status}")
                return False
    except Exception as e:
        _LOGGER.error(f"Exception occurred during login: {e}")
        return False

async def set_temperature(session: ClientSession, device_id: str, temperature: int):
    """Set temperature of the boiler."""
    url = 'https://myeldom.com/api/flatboiler/setTemperature'
    payload = {"deviceId": device_id, "temperature": temperature}

    try:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                _LOGGER.info(f"Temperature set to {temperature}°C for {device_id}")
            else:
                _LOGGER.error(f"Failed to set temperature: {resp.status}")
    except Exception as e:
        _LOGGER.error(f"Exception occurred while setting temperature: {e}")

async def set_state(session: ClientSession, device_id: str, state: int):
    """Set state of the boiler (1 for ON, 0 for OFF)."""
    url = 'https://myeldom.com/api/flatboiler/setState'
    payload = {"deviceId": device_id, "state": state}

    try:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                state_str = "ON" if state == 1 else "OFF"
                _LOGGER.info(f"Boiler {device_id} set to {state_str}")
            else:
                _LOGGER.error(f"Failed to set state: {resp.status}")
    except Exception as e:
        _LOGGER.error(f"Exception occurred while setting state: {e}")

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Eldom boiler component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Eldom Boiler from a config entry."""
    boiler_id = entry.data["boiler_id"]
    email = entry.data.get("email")
    password = entry.data.get("password")

    session = async_get_clientsession(hass)
    
    # Perform login
    if not await _do_login(session, email, password):
        return False

    # WebSocket connection setup (existing logic)
    websocket_url = 'wss://myeldom.com/'

    async def connect():
        while True:
            try:
                async with session.ws_connect(websocket_url) as websocket:
                    subscribe_message = {
                        "MessageType": "MessageDistributor",
                        "Data": json.dumps({
                            "Data": boiler_id,
                            "ProviderID": 9,
                            "Command": 2
                        })
                    }
                    await websocket.send_json(subscribe_message)
                    _LOGGER.debug("Subscribed to WebSocket channel.")

                    async for msg in websocket:
                        if msg.type == WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            _LOGGER.debug(f"Received data: {data}")
                            hass.data[DOMAIN][boiler_id] = data
                            async_dispatcher_send(
                                hass,
                                f"{DOMAIN}_data_update_{boiler_id}"
                            )
                        elif msg.type == WSMsgType.ERROR:
                            _LOGGER.error("WebSocket error")
                            break
            except Exception as e:
                _LOGGER.error(f"WebSocket connection error: {e}")
                await asyncio.sleep(5)

    hass.loop.create_task(connect())

    # Register services for controlling the boiler
    async def handle_set_temperature(call):
        """Handle setting temperature."""
        temperature = call.data.get("temperature")
        await set_temperature(session, boiler_id, temperature)

    async def handle_set_state(call):
        """Handle setting state."""
        state = call.data.get("state")
        await set_state(session, boiler_id, state)

    hass.services.async_register(DOMAIN, "set_temperature", handle_set_temperature)
    hass.services.async_register(DOMAIN, "set_state", handle_set_state)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return unloaded
