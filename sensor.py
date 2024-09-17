from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN

SENSOR_TYPES = {
    "SetTemp": ["Set Temperature", "°C", "temperature"],
    "State": ["Power State", None, None],
    "STL_Temp": ["Temperature Cylinder 1", "°C", "temperature"],
    "FT_Temp": ["Temperature Cylinder 2 ", "°C", "temperature"],
    "EnergyD": ["Energy consumption Day", "kWh", "power"],
    "EnergyN": ["Energy consumption Night", "kWh", "power"],
    "PowerFlag": ["Power Status (Power Flag)", None, None],
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Eldom sensors based on a config entry."""
    boiler_id = entry.data["boiler_id"]
    entities = []
    for key, value in SENSOR_TYPES.items():
        entities.append(EldomBoilerSensor(hass, key, value[0], value[1], boiler_id))
    async_add_entities(entities)


class EldomBoilerSensor(SensorEntity):
    """Representation of an Eldom Boiler Sensor."""

    def __init__(self, hass, key, name, unit, boiler_id):
        self.hass = hass
        self.key = key
        self._name = f"{name}"
        self._unit = unit
        self._state = None
        self.boiler_id = boiler_id
        self._device_class = SENSOR_TYPES[key][2]
        self._icon = SENSOR_TYPES[key][2] if not self._device_class else None
        self._unsubscribe_dispatcher = None
        self.entity_id = f"sensor.{self.boiler_id.lower()}_{key.lower()}"

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._unsubscribe_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_data_update_{self.boiler_id}", self._handle_data
        )

    async def async_will_remove_from_hass(self):
        """Disconnect dispatcher."""
        if self._unsubscribe_dispatcher:
            self._unsubscribe_dispatcher()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"eldom_{self.boiler_id}_{self.key}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def device_info(self):
        """Return device information about this Eldom boiler."""
        data = self.hass.data[DOMAIN].get(self.boiler_id)
        device_data = data.get('Data', [])[0] if data else {}
        sw_version = device_data.get('SoftwareVersion', 'Unknown')
        
        return {
            "identifiers": {(DOMAIN, self.boiler_id)},
            "name": f"Eldom Boiler {self.boiler_id}",
            "manufacturer": "Eldom",
            "model": "Boiler",
            "sw_version": '49',
        }

    @callback
    def _handle_data(self):
        """Handle new data from the boiler."""
        data = self.hass.data[DOMAIN].get(self.boiler_id)
        
        if data:
            try:
                device_data = data['Data'][0]
                value = device_data.get(self.key)
                if self.key == 'State':
                    self._state = 'ON' if value == 1 else 'OFF'
                else:
                    self._state = value
                self.async_write_ha_state()
            except (KeyError, IndexError):
                pass
