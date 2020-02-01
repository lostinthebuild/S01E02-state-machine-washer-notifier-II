"""Support for apply multiple schmitt triggers on a sensor value."""
import logging
from collections import namedtuple

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_MAXIMUM,
    CONF_MINIMUM,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_ENTITY_ID,
    STATE_UNKNOWN,
    ATTR_ENTITY_ID,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change

_LOGGER = logging.getLogger(__name__)

CONF_RANGES = "ranges"
CONF_UTP = "utp"
CONF_LTP = "ltp"
CONF_ID = "id"

DEFAULT_NAME = "Schmitt Trigger Sensor"
DEFAULT_UTP = 0.0
DEFAULT_LTP = 0.0

ICON = "mdi:graphic-eq"

_RANGE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_LTP, default=DEFAULT_LTP): cv.small_float,
        vol.Optional(CONF_UTP, default=DEFAULT_UTP): cv.small_float,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_RANGES): [_RANGE_SCHEMA],
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Random number sensor."""
    name = config.get(CONF_NAME)
    entity_id = config.get(CONF_ENTITY_ID)
    ranges = config.get(CONF_RANGES)
    unique_id = config.get(CONF_ID)
    async_add_entities([SchmittSensor(hass, name, entity_id, unique_id, ranges)], True)


Range = namedtuple("Range", ["name", "ltp", "utp"])


class SchmittSensor(Entity):
    def __init__(self, hass, name, entity_id, unique_id, ranges):
        range_from_config = lambda conf: Range(
            conf.get(CONF_NAME), conf.get(CONF_LTP), conf.get(CONF_UTP)
        )
        is_default = lambda r: r.utp == DEFAULT_UTP and r.ltp == DEFAULT_LTP
        not_default = lambda x: not is_default(x)
        utp = lambda r: r.utp

        self._name = name
        self._hass = hass
        self._entity_id = entity_id
        self._id = unique_id
        self.entity_id = "sensor.{}".format(unique_id)
        self._ranges = list([range_from_config(x) for x in ranges])
        self._default_range = next((r for r in self._ranges if is_default(r)), None)
        self._ranges = sorted(filter(not_default, self._ranges), key=utp, reverse=True)
        self.current_range = self._default_range
        self.sensor_value = None

        @callback
        def async_sensor_state_listener(entity, old_state, new_state):
            """Handle sensor state changes."""
            try:
                self.sensor_value = (
                    None if new_state.state == STATE_UNKNOWN else float(new_state.state)
                )
            except (ValueError, TypeError):
                self.sensor_value = None
                _LOGGER.warning("State is not numerical")

            hass.async_add_job(self.async_update_ha_state, True)

        async_track_state_change(hass, entity_id, async_sensor_state_listener)

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self.current_range.name if self.current_range else STATE_UNKNOWN

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return ICON

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._id

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {ATTR_ENTITY_ID: self._entity_id}

    async def async_update(self):
        if not self.sensor_value:
            self.current_range = None
            return

        sv = self.sensor_value
        probable_range = next((r for r in self._ranges if sv >= r.utp), None)

        if self.current_range:
            is_oob_current = sv < self.current_range.ltp

            if is_oob_current:
                self.current_range = probable_range or self._default_range
            else:
                if probable_range and probable_range.utp > self.current_range.utp:
                    self.current_range = probable_range
        else:
            self.current_range = probable_range or self._default_range
