from custom_components.neoclima.integration.NeoclimaClimateEntity import NeoclimaClimateEntity

TEMPERATURE_SENSOR_CONFIG = "temperature_sensor"


class ThermostatNeoclimaClimateEntity(NeoclimaClimateEntity):
    def __init__(self, hass, config):
        super().__init__(hass, config)

        self._temperature_sensor = config.get(TEMPERATURE_SENSOR_CONFIG, None)
