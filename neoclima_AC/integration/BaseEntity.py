from typing import Optional

from homeassistant.helpers.entity import Entity

NAME_CONFIG = "name"
UNIQUE_ID_CONFIG = "unique_id"


class BaseEntity(Entity):
    def __init__(self, hass, config):
        self._hass = hass
        self._name = config.get(NAME_CONFIG, None)
        self._unique_id = config.get(UNIQUE_ID_CONFIG, None)

    @property
    def unique_id(self) -> Optional[str]:
        return self._unique_id

    @property
    def name(self) -> Optional[str]:
        return self._name