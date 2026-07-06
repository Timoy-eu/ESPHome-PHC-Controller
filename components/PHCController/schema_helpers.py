import esphome.codegen as cg
import esphome.config_validation as cv

from . import CONTROLLER_ID, PHCController

# Shared by every PHC entity platform (AMD switch/light, EMD binary_sensor/light, JRM cover):
# each entity sits on one channel of a module addressed via its bus (DIP-switch) address.
ADDRESS = "dip"
CHANNEL = "channel"


def module_schema(max_channel):
    """Common config fields (parent controller, module address, channel) for a PHC entity platform."""
    return {
        cv.Required(CONTROLLER_ID): cv.use_id(PHCController),
        cv.Required(ADDRESS): cv.int_range(min=0, max=31),
        cv.Required(CHANNEL): cv.int_range(min=0, max=max_channel),
    }


def register_module(var, config, register_method_name):
    """Common to_code() tail for a PHC entity platform: wire address/channel and register
    the entity on its parent PHCController (looked up via CONTROLLER_ID)."""
    controller = yield cg.get_variable(config[CONTROLLER_ID])
    cg.add(var.set_address(config[ADDRESS]))
    cg.add(var.set_channel(config[CHANNEL]))
    cg.add(getattr(controller, register_method_name)(var))
