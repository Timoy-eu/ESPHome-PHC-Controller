import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import uart
from esphome.components.uart import UARTComponent
from esphome.const import CONF_ID

AUTO_LOAD = ["cover", "light", "switch", "binary_sensor", "AMD", "EMD", "JRM"]

DEPENDENCIES = ["uart"]

CONTROLLER_ID = "phc_controller_id"
UART_ID = "uart_id"
FLOW_CONTROL_PIN = "flow_control_pin"
TIMING_DELAY = "timing_delay"


phc_controller_ns = cg.esphome_ns.namespace("phc_controller")
PHCController = phc_controller_ns.class_("PHCController", cg.Component, uart.UARTDevice)

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(PHCController),
            cv.Required(UART_ID): cv.use_id(UARTComponent),
            cv.Optional(FLOW_CONTROL_PIN): pins.gpio_output_pin_schema,
            # Delay in microseconds before answering a module request (original PHC
            # controller: ~250us total). Overridable from YAML so the value can be
            # calibrated on real hardware without code changes (see UPDATE_TESTING.md).
            cv.Optional(TIMING_DELAY): cv.int_range(min=0, max=1000),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(uart.UART_DEVICE_SCHEMA)
)


def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)
    yield uart.register_uart_device(var, config)

    if FLOW_CONTROL_PIN in config:
        pin = yield cg.gpio_pin_expression(config[FLOW_CONTROL_PIN])
        cg.add(var.set_flow_control_pin(pin))

    if TIMING_DELAY in config:
        cg.add(var.set_timing_delay(config[TIMING_DELAY]))
