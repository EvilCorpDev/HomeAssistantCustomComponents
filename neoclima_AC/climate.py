import logging

from custom_components.neoclima.integration.NeoclimaClimateEntity import REQUEST_SERVICE_DOMAIN_CONFIG, \
    REQUEST_SERVICE_NAME_CONFIG, RESPONSE_SENSOR_CONFIG
from custom_components.neoclima.integration.ThermostatNeoclimaClimateEntity import ThermostatNeoclimaClimateEntity

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    if not config.get(REQUEST_SERVICE_DOMAIN_CONFIG, None) \
            or not config.get(REQUEST_SERVICE_NAME_CONFIG, None) \
            or not config.get(RESPONSE_SENSOR_CONFIG, None):
        _LOGGER.error(
            "Properties 'request_service_domain' and 'request_service_name' and 'response_sensor' required for 'neoclima' platform")
        return

    thermostat = ThermostatNeoclimaClimateEntity(hass, config)
    add_entities([thermostat])
