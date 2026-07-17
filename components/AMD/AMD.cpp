#include "esphome/core/log.h"
#include "AMD.h"

namespace esphome
{
    namespace AMD_binary
    {

        static const char *TAG = "AMD";

        void AMD::setup()
        {
        }

        void AMD::loop()
        {
            if (get_state() != target_state)
            {
                // Wait before retransmitting
                if (millis() - last_request > RESEND_TIMEOUT)
                {
                    if (resend_counter < MAX_RESENDS)
                    {
                        // Retry for as long as possible. Only attempts that actually reached the
                        // wire consume resend budget - under bus contention weak writes are
                        // frequently skipped, and counting those would burn through MAX_RESENDS
                        // without the module ever seeing a single command.
                        if (transmit_current_command_())
                            resend_counter++;
                    }
                    else
                    {
                        // Reset the state and log a warning, device cannot be reached
                        ESP_LOGW(TAG, "Device not responding! Is the device connected to the bus? (DIP: %i)", address);
                        publish_state(get_state());
                        write_state(get_state());
                    }
                }
            }
        }

        void AMD::write_state(bool state)
        {
            resend_counter = 0;
            target_state = state;
            has_transmitted_ = false;
            // We don't publish the state here, we wait for the answer and use the callback to make sure the output acutally switched
            transmit_current_command_();
        }

        bool AMD::transmit_current_command_()
        {
            // The toggle bit is an alternating-bit shared per module: a transmitted command must
            // flip it exactly once relative to the previously transmitted command, and the module
            // treats an unchanged toggle as a retransmission (re-ack without executing again).
            // Compute the flip at transmission time and only commit it once the write actually
            // reached the bus - committing a flip for a skipped weak write desyncs the shared
            // toggle and makes the module ignore other channels' commands as duplicates.
            bool tx_toggle = has_transmitted_ ? toggle_map->get_toggle(this) : !toggle_map->get_toggle(this);

            // 3 MSBits determine the channel, lower 5 bits are for functionality
            uint8_t function = (channel << 5) | (target_state ? 0x02 : 0x03);

            uint8_t message[5] = {static_cast<uint8_t>(AMD_MODULE_ADDRESS | address), static_cast<uint8_t>((tx_toggle ? 0x80 : 0x00) | 0x01), function, 0x00, 0x00};
            short crc = util::PHC_CRC(message, 3);

            message[3] = static_cast<uint8_t>(crc & 0xFF);
            message[4] = static_cast<uint8_t>((crc & 0xFF00) >> 8);

            bool sent = write_array(message, 5, true);
            if (sent && !has_transmitted_)
            {
                toggle_map->set_toggle(this, tx_toggle);
                has_transmitted_ = true;
            }
            last_request = millis();
            return sent;
        }

        void AMD::dump_config()
        {
            ESP_LOGCONFIG(TAG, "AMD DIP-ID: %u\t Channel: %u", address, channel);
        }

    } // namespace AMD_binary
} // namespace esphome
