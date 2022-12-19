"""The ATEN PE sensor component."""
from __future__ import annotations

from atenpdu import AtenPE

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="outletCurrent",
        device_class=SensorDeviceClass.CURRENT,
        name="Current",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="outletVoltage",
        device_class=SensorDeviceClass.VOLTAGE,
        name="Voltage",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="outletPower",
        device_class=SensorDeviceClass.POWER,
        name="Power",
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="outletPowerDissipation",
        device_class=SensorDeviceClass.ENERGY,
        name="Power Dissipation",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="outletPowerFactor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        name="Power Factor",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ATEN PE sensors from a config entry."""
    dev, info, mac = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[AtenSensorEntity] = []
    async for outlet in dev.outlets():
        for description in SENSORS:
            entities.append(
                AtenSensorEntity(
                    dev,
                    info,
                    mac,
                    outlet.id,
                    outlet.name,
                    description,
                )
            )

    async_add_entities(entities, True)


class AtenSensorEntity(SensorEntity):
    """Represents an ATEN PE sensor."""

    def __init__(
        self,
        device: AtenPE,
        info: DeviceInfo,
        mac: str,
        outlet: str,
        name: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize an ATEN PE sensor."""
        self.entity_description = description
        self._device = device
        self._outlet = outlet
        self._attr_device_info = info
        self._attr_unique_id = f"{mac}-{outlet}-{self.entity_description.key}"
        self._attr_name = name or f"Outlet {outlet}"
        self._attr_name += f" {self.entity_description.name}"

    async def async_update(self) -> None:
        """Process update from entity."""
        self._attr_native_value = await self._device.getAttribute(
            self.entity_description.key, self._outlet
        )
