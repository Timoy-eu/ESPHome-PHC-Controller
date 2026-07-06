import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import light
from esphome.components.light import LightType
from esphome.const import CONF_DISABLED_BY_DEFAULT, CONF_OUTPUT_ID

from ..PHCController.schema_helpers import module_schema, register_module

DEPENDENCIES = ["PHCController"]

amd_light_ns = cg.esphome_ns.namespace("EMD_light")
EMDLight = amd_light_ns.class_(
    "EMD_light", light.LightOutput, cg.EntityBase, cg.Component
)

CONFIG_SCHEMA = (
    light.light_schema(EMDLight, type_=LightType.BINARY)
    .extend(
        {
            cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(EMDLight),
            cv.Optional(CONF_DISABLED_BY_DEFAULT, default=True): cv.boolean,
        }
    )
    .extend(module_schema(max_channel=15))
    .extend(cv.COMPONENT_SCHEMA)
)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID])
    yield cg.register_component(var, config)
    yield light.register_light(var, config)
    yield from register_module(var, config, "register_EMDLight")
