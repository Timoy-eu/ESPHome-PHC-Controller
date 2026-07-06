import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch
from esphome.const import CONF_DEVICE_CLASS, CONF_ID, DEVICE_CLASS_OUTLET

from ..PHCController.schema_helpers import module_schema, register_module

DEPENDENCIES = ["PHCController"]

AMD_ns = cg.esphome_ns.namespace("AMD_binary")
AMD = AMD_ns.class_("AMD_switch", switch.Switch, cg.Component)

CONFIG_SCHEMA = (
    switch.switch_schema(AMD)
    .extend(
        {
            cv.GenerateID(): cv.declare_id(AMD),
            cv.Optional(CONF_DEVICE_CLASS, default=DEVICE_CLASS_OUTLET): cv.string,
        }
    )
    .extend(module_schema(max_channel=7))
    .extend(cv.COMPONENT_SCHEMA)
)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)
    yield switch.register_switch(var, config)
    yield from register_module(var, config, "register_AMD")
