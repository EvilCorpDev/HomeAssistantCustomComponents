from homeassistant.components.climate import HVAC_MODE_HEAT
from homeassistant.core import State
from homeassistant.helpers.event import async_track_state_change

from custom_components.neoclima.command.SetStateCommand import SetStateCommand
from custom_components.neoclima.integration.BaseClimateEntity import BaseClimateEntity

REQUEST_SERVICE_DOMAIN_CONFIG = "request_service_domain"
REQUEST_SERVICE_NAME_CONFIG = "request_service_name"
RESPONSE_SENSOR_CONFIG = "response_sensor"


class NeoclimaClimateEntity(BaseClimateEntity):
    def __init__(self, hass, config):
        super().__init__(hass, config)

        self._request_service_domain = config.get(REQUEST_SERVICE_DOMAIN_CONFIG)
        self._request_service_name = config.get(REQUEST_SERVICE_NAME_CONFIG)
        self._response_sensor = config.get(RESPONSE_SENSOR_CONFIG)
        self._correlation_id = 1

        async_track_state_change(self._hass, self._response_sensor, self._read_neoclima_response)

    def _read_neoclima_response(self, entity_id: str, old_state: State, new_state: State) -> None:
        if new_state is None:
            return

    def _handle_status_change(self) -> None:
        if self.hvac_mode == HVAC_MODE_HEAT:
            temperature = round(self.target_temperature_high)
        else:
            temperature = round(self.target_temperature_low)

        command = SetStateCommand(
            self.hvac_mode,
            self.fan_mode,
            self.preset_mode,
            self.swing_mode,
            temperature,
            self.correlation_id
        )

        print(command.byte_array)
        self._hass.services.call(domain=self._request_service_domain, service=self._request_service_name,
                                 service_data={"payload": command.byte_array})

    @property
    def correlation_id(self):
        if self._correlation_id > 30:
            self._correlation_id = 1
        else:
            self._correlation_id = self._correlation_id + 1

        return self._correlation_id

    def set_hvac_mode(self, hvac_mode: str) -> None:
        super().set_hvac_mode(hvac_mode)
        self._handle_status_change()

    def set_fan_mode(self, fan_mode: str) -> None:
        super().set_fan_mode(fan_mode)
        self._handle_status_change()

    def set_preset_mode(self, preset_mode: str) -> None:
        super().set_preset_mode(preset_mode)
        self._handle_status_change()

    def set_swing_mode(self, swing_mode: str) -> None:
        super().set_swing_mode(swing_mode)
        self._handle_status_change()

    def set_temperature(self, **kwargs) -> None:
        super().set_temperature(**kwargs)
        self._handle_status_change()
