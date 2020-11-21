from typing import Optional, List, Any

from homeassistant.components.humidifier import HumidifierEntity, DEVICE_CLASS_HUMIDIFIER
from homeassistant.components.humidifier.const import MODE_AUTO, MODE_BOOST, SUPPORT_MODES, MODE_NORMAL, MODE_ECO, \
    DOMAIN
from homeassistant.core import State
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.script import Script

UNIQUE_ID_CONFIG = "unique_id"
NAME_CONFIG = "name"
BOOT_MODE_TETHER_CONFIG = "boot_mode_tether"
HUMIDITY_SENSOR = "humidity_sensor"
MODES = [MODE_AUTO, MODE_ECO, MODE_NORMAL, MODE_BOOST]
OFF_ACTION = "turn_off"
ABOVE_TOLERANCE = "above_tolerance"
BELOW_TOLERANCE = "below_tolerance"


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([GenericHumidifierEntity(hass, config)])


class GenericHumidifierEntity(HumidifierEntity, RestoreEntity):
    def __init__(self, hass, config):
        self._hass = hass
        self._power = False
        self._humidity = 0
        self._mode = MODE_AUTO
        self._name = config.get(NAME_CONFIG, None)
        self._unique_id = config.get(UNIQUE_ID_CONFIG, None)
        self._boot_mode_tether = config.get(BOOT_MODE_TETHER_CONFIG, None)
        self._above_tolerance = float(config.get(ABOVE_TOLERANCE, 0))
        self._below_tolerance = float(config.get(BELOW_TOLERANCE, 0))
        self._first_cycle = True
        self._current_mode = None

        self._modes_script = dict()
        self._available_modes = []

        self.__init_modes_script(config)
        self._init_properties(dict())

        self._turn_off_action = config.get(OFF_ACTION, None)
        if self._turn_off_action:
            if isinstance(self._turn_off_action, list):
                self._turn_off_script = Script(self._hass, self._turn_off_action, self._unique_id, DOMAIN)
            else:
                self._turn_off_script = Script(self._hass, [self._turn_off_action], self._unique_id, DOMAIN)

        self._humidity_sensor = config.get(HUMIDITY_SENSOR, None)
        if self._humidity_sensor:
            async_track_state_change(self._hass, self._humidity_sensor, self._handle_humidity_state_update)

    def __init_modes_script(self, config):
        for mode in MODES:
            mode_action = config.get(mode, None)

            if not mode_action:
                continue

            if isinstance(mode_action, list):
                self._modes_script[mode] = Script(self._hass, mode_action, self._unique_id, DOMAIN)
            else:
                self._modes_script[mode] = Script(self._hass, [mode_action], self._unique_id, DOMAIN)

            self._available_modes.append(mode)

        if len(self._available_modes) > 1:
            self._supported_features = SUPPORT_MODES
        else:
            self._supported_features = 0

    def _handle_humidity_state_update(self, entity_id: str, old_state: State, new_state: State) -> None:
        self.__handle_mode()

    def __handle_mode(self):
        if not self.is_on:
            return

        sensor_state = self._hass.states.get(self._humidity_sensor)

        if not sensor_state or not sensor_state.state:
            return

        sensor_value = float(sensor_state.state)

        if self._first_cycle:
            if self.target_humidity <= sensor_value:
                self.__turn_off()
                return
        else:
            if not self._first_cycle and (self.target_humidity + self._above_tolerance) <= sensor_value:
                self.__turn_off()
                return
            if not self._first_cycle and (self.target_humidity - self._below_tolerance) <= sensor_value:
                return

        self._first_cycle = False

        if self.mode != MODE_AUTO:
            self.__turn_on_mode(self.mode)
        elif self.mode == MODE_AUTO and not self._boot_mode_tether:
            self.__turn_on_mode(MODE_AUTO)
        elif self.mode == MODE_AUTO and self._boot_mode_tether and MODE_BOOST in self._available_modes:
            if self.target_humidity - sensor_value > self._boot_mode_tether:
                self.__turn_on_mode(MODE_BOOST)
            else:
                self.__turn_on_mode(MODE_AUTO)

    def __turn_on_mode(self, mode):
        if mode == self._current_mode:
            return
        self._modes_script[mode].run()
        self._current_mode = mode

    def __turn_off(self):
        if not self._turn_off_script:
            return
        self._turn_off_script.run()
        self._current_mode = None

    @property
    def unique_id(self) -> Optional[str]:
        return self._unique_id

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def device_class(self) -> Optional[str]:
        return DEVICE_CLASS_HUMIDIFIER

    @property
    def is_on(self) -> bool:
        return self._power

    def turn_on(self, **kwargs: Any) -> None:
        self._power = True
        self._first_cycle = True
        self.__handle_mode()

    def turn_off(self, **kwargs: Any) -> None:
        self._power = False
        self.__turn_off()

    @property
    def target_humidity(self) -> Optional[int]:
        return self._humidity

    def set_humidity(self, humidity: int) -> None:
        self._first_cycle = True
        self._humidity = humidity
        self.__handle_mode()

    @property
    def available_modes(self) -> Optional[List[str]]:
        return self._available_modes

    @property
    def mode(self) -> Optional[str]:
        return self._mode

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self.__handle_mode()

    @property
    def supported_features(self) -> Optional[int]:
        return self._supported_features

    async def async_added_to_hass(self) -> None:
        last_state = await self.async_get_last_state()

        if not last_state:
            return

        last_state_dict = last_state.as_dict().get("attributes", dict())

        if last_state.state == 'off':
            last_state_dict["power"] = False
        else:
            last_state_dict["power"] = True

        self._init_properties(last_state_dict)

        await self.async_update_ha_state(True)

    def _init_properties(self, property_store):
        self._humidity = property_store.get("humidity", 0)
        self._mode = property_store.get("mode", MODE_AUTO)
        self._power = property_store.get("power", False)
