from homeassistant.components.climate.const import HVAC_MODE_OFF, HVAC_MODE_AUTO, HVAC_MODE_COOL, HVAC_MODE_DRY, \
    HVAC_MODE_HEAT, \
    HVAC_MODE_FAN_ONLY, FAN_LOW, FAN_MIDDLE, FAN_HIGH, FAN_AUTO, PRESET_ECO, PRESET_BOOST, SWING_VERTICAL, \
    SWING_HORIZONTAL

from custom_components.neoclima.command.AbstractSignedCommand import AbstractSignedCommand

HVAC_MODES = dict()
HVAC_MODES[HVAC_MODE_OFF] = 16
HVAC_MODES[HVAC_MODE_AUTO] = 16
HVAC_MODES[HVAC_MODE_COOL] = 48
HVAC_MODES[HVAC_MODE_DRY] = 80
HVAC_MODES[HVAC_MODE_HEAT] = 112
HVAC_MODES[HVAC_MODE_FAN_ONLY] = 144

FAN_MODES = dict()
FAN_MODES[FAN_LOW] = 40
FAN_MODES[FAN_MIDDLE] = 60
FAN_MODES[FAN_HIGH] = 80
FAN_MODES[FAN_AUTO] = 102


class SetStateCommand(AbstractSignedCommand):
    def __init__(self, hvac_mode, fan_mode, preset_mode, swing_mode, temperature, correlation_id):
        super().__init__(24)
        self._byte_array[0] = 64
        self._byte_array[4] = 127
        self._byte_array[6] = 127
        self._byte_array[19] = 30
        self._byte_array[23] = correlation_id

        self._hvac_mode = hvac_mode
        self._fan_mode = fan_mode
        self._preset_mode = preset_mode
        self._swing_mode = swing_mode
        self._temperature = temperature

    @property
    def byte_array(self):
        self._process_hvac_mode()
        self._process_fan_mode()
        self._process_preset_mode()
        self._process_swing_mode()
        return super().byte_array

    def _process_hvac_mode(self):
        if self._hvac_mode == HVAC_MODE_OFF:
            self._byte_array[1] = 66
        else:
            self._byte_array[1] = 67

        self._byte_array[2] = HVAC_MODES[self._hvac_mode] + self._temperature

    def _process_fan_mode(self):
        self._byte_array[3] = FAN_MODES[self._fan_mode]

    def _process_swing_mode(self):
        if self._swing_mode == SWING_VERTICAL:
            self._byte_array[7] = 60
        elif self._swing_mode == SWING_HORIZONTAL:
            self._byte_array[7] = 51
        else:
            self._byte_array[7] = 48

    def _process_preset_mode(self):
        if self._preset_mode == PRESET_BOOST:
            self._byte_array[8] = 32
            self._byte_array[10] = 2
        elif self._preset_mode == PRESET_ECO:
            self._byte_array[9] = 128
        else:
            self._byte_array[8] = 0
            self._byte_array[9] = 0
            self._byte_array[10] = 0
