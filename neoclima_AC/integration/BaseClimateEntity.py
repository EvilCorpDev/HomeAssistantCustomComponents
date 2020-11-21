from typing import Optional, List

from homeassistant.components.climate import SUPPORT_FAN_MODE, HVAC_MODE_OFF, ClimateEntity
from homeassistant.components.climate.const import HVAC_MODE_AUTO, SUPPORT_TARGET_TEMPERATURE, \
    SUPPORT_TARGET_TEMPERATURE_RANGE, SUPPORT_SWING_MODE, HVAC_MODE_COOL, HVAC_MODE_DRY, HVAC_MODE_HEAT, \
    HVAC_MODE_FAN_ONLY, FAN_LOW, FAN_MIDDLE, FAN_HIGH, FAN_AUTO, SWING_OFF, SWING_VERTICAL, SWING_HORIZONTAL, \
    PRESET_BOOST, PRESET_ECO, PRESET_NONE, ATTR_TARGET_TEMP_LOW, ATTR_TARGET_TEMP_HIGH, SUPPORT_PRESET_MODE
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.restore_state import RestoreEntity

from custom_components.neoclima.integration.BaseEntity import BaseEntity


class BaseClimateEntity(BaseEntity, ClimateEntity, RestoreEntity):
    def __init__(self, hass, config):
        super().__init__(hass, config)
        self._init_properties(dict())

    @property
    def supported_features(self) -> Optional[int]:
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_TARGET_TEMPERATURE_RANGE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE | SUPPORT_PRESET_MODE

    @property
    def hvac_modes(self) -> List[str]:
        return [HVAC_MODE_OFF, HVAC_MODE_AUTO, HVAC_MODE_COOL, HVAC_MODE_DRY, HVAC_MODE_HEAT, HVAC_MODE_FAN_ONLY]

    @property
    def hvac_mode(self) -> str:
        return self._hvac_mode

    def set_hvac_mode(self, hvac_mode: str) -> None:
        self._hvac_mode = hvac_mode

    @property
    def fan_modes(self) -> Optional[List[str]]:
        return [FAN_LOW, FAN_MIDDLE, FAN_HIGH, FAN_AUTO]

    @property
    def fan_mode(self) -> Optional[str]:
        return self._fan_mode

    def set_fan_mode(self, fan_mode: str) -> None:
        self._fan_mode = fan_mode

    @property
    def preset_modes(self) -> Optional[List[str]]:
        return [PRESET_NONE, PRESET_ECO, PRESET_BOOST]

    @property
    def preset_mode(self) -> Optional[str]:
        return self._preset_mode

    def set_preset_mode(self, preset_mode: str) -> None:
        self._preset_mode = preset_mode

    @property
    def swing_modes(self) -> Optional[List[str]]:
        return [SWING_OFF, SWING_VERTICAL, SWING_HORIZONTAL]

    @property
    def swing_mode(self) -> Optional[str]:
        return self._swing_mode

    def set_swing_mode(self, swing_mode: str) -> None:
        self._swing_mode = swing_mode

    @property
    def current_temperature(self) -> Optional[float]:
        return self._current_temperature

    @property
    def min_temp(self) -> float:
        return 16

    @property
    def max_temp(self) -> float:
        return 30

    @property
    def temperature_unit(self) -> str:
        return TEMP_CELSIUS

    @property
    def target_temperature_high(self) -> Optional[float]:
        return self._target_temperature_high

    @property
    def target_temperature_low(self) -> Optional[float]:
        return self._target_temperature_low

    @property
    def target_temperature_step(self) -> Optional[float]:
        return 0.1

    def set_temperature(self, **kwargs) -> None:
        for target in kwargs.items():
            if target[0] == ATTR_TARGET_TEMP_LOW:
                self._target_temperature_low = target[1]
            elif target[0] == ATTR_TARGET_TEMP_HIGH:
                self._target_temperature_high = target[1]

    async def async_added_to_hass(self) -> None:
        last_state = await self.async_get_last_state()

        if not last_state:
            return

        last_state_dict = last_state.as_dict().get("attributes", dict())

        if last_state.state == "unknown":
            last_state_dict["hvac_mode"] = HVAC_MODE_OFF
        else:
            last_state_dict["hvac_mode"] = last_state.state

        self._init_properties(last_state_dict)

        await self.async_update_ha_state(True)

    def _init_properties(self, property_store):
        self._hvac_mode = property_store.get("hvac_mode", HVAC_MODE_OFF)
        self._fan_mode = property_store.get("fan_mode", FAN_AUTO)
        self._swing_mode = property_store.get("swing_mode", SWING_OFF)
        self._preset_mode = property_store.get("preset_mode", PRESET_NONE)
        self._current_temperature = property_store.get("current_temperature", None)
        self._target_temperature_low = property_store.get("target_temp_low", self.min_temp)
        self._target_temperature_high = property_store.get("target_temp_high", self.max_temp)