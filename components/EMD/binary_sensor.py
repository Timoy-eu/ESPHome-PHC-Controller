import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import CONF_DISABLED_BY_DEFAULT, CONF_ID

from ..PHCController.schema_helpers import module_schema, register_module

DEPENDENCIES = ["PHCController"]

DEVICE_TYPE = "device_type"

EMD_ns = cg.esphome_ns.namespace("EMD_binary_sensor")
EMD = EMD_ns.class_("EMD", binary_sensor.BinarySensor, cg.Component)

CONFIG_SCHEMA = (
    binary_sensor.binary_sensor_schema(EMD)
    .extend(
        {
            cv.GenerateID(): cv.declare_id(EMD),
            cv.Optional(CONF_DISABLED_BY_DEFAULT, default=True): cv.boolean,
        }
    )
    .extend(module_schema(max_channel=15))
    .extend(cv.COMPONENT_SCHEMA)
)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)
    yield binary_sensor.register_binary_sensor(var, config)
    yield from register_module(var, config, "register_EMD")
