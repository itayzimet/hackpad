# oled config
OLED_ENABLE = yes
OLED_TRANSPORT = i2c
OLED_DRIVER = ssd1306
I2C_DRIVER = vendor

# led config
RGBLIGHT_ENABLE = yes
WS2812_DRIVER = vendor
WS2812_DI_PIN = GP1
RGBLIGHT_LED_COUNT = 16

# encoder config
ENCODER_ENABLE = yes

# required for rp2040
LTO_ENABLE = yes

# HID coms for song info