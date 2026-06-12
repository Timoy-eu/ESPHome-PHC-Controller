#include "esphome/core/log.h"
#include "EMD.h"
#include "esphome/core/application.h"

namespace esphome
{
    namespace EMD_binary_sensor
    {

        static const char *TAG = "EMD.binary_sensor";

        void EMD::setup()
        {
            // disabled_by_default is set via the python schema, the runtime setter no longer exists
            publish_initial_state(false);
        }

        void EMD::dump_config()
        {
            ESP_LOGCONFIG(TAG, "EMD DIP-ID: %u \t Channel: %u", address, channel);
        }

    } // namespace EMD_binary_sensor
} // namespace esphome