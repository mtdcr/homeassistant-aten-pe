"""The ATEN PE component."""
import logging

from atenpdu import AtenPE, AtenPEError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo

from .const import CONF_AUTH_KEY, CONF_COMMUNITY, CONF_PRIV_KEY, DOMAIN

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    config = entry.data

    node = config[CONF_HOST]
    serv = config[CONF_PORT]

    dev = AtenPE(
        node=node,
        serv=serv,
        community=config[CONF_COMMUNITY],
        username=config[CONF_USERNAME],
        authkey=config.get(CONF_AUTH_KEY),
        privkey=config.get(CONF_PRIV_KEY),
    )

    try:
        await dev.initialize()
        mac = await dev.deviceMAC()
        name = await dev.deviceName()
        model = await dev.modelName()
        sw_version = await dev.deviceFWversion()
    except AtenPEError as exc:
        _LOGGER.error("Failed to initialize %s:%s: %s", node, serv, str(exc))
        dev.close()
        raise ConfigEntryNotReady from exc

    info = DeviceInfo(
        connections={(CONNECTION_NETWORK_MAC, mac)},
        manufacturer="ATEN",
        model=model,
        name=name,
        sw_version=sw_version,
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = (dev, info, mac)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    dev = hass.data[DOMAIN][entry.entry_id][0]
    dev.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
