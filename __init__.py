import asyncio
import json
import logging

from aiohttp import WSMsgType

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Eldom Smart Boiler component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Eldom Smart Boiler from a config entry."""
    websocket_url = 'wss://myeldom.com/'
    boiler_id = entry.data["boiler_id"]

    session = async_get_clientsession(hass)

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

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return unloaded
