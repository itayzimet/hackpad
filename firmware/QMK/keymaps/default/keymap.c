// Copyright 2023 QMK
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    /*
     * ┌───┬───┬───┐
     * │ 7 │ 8 │ 9 │
     * ├───┼───┼───┤
     * │ 4 │ 5 │ 6 │
     * ├───┼───┼───┤
     * │ 1 │ 2 │ 3 │
     * └───┴───┴───┘
     */
    /* row/col (based on the physical layout of the keypad)
     * ┌───┬───┬───┐
     * │K00│K01│K02│
     * ├───┼───┼───┤
     * │K10│K11│K12│
     * ├───┼───┼───┤
     * │K20│K21│K22│
     * └───┴───┴───┘
     * EC11: click registers as pushing all buttons in row 2 (by pins) or column2 (by geography) - K02, K12, K22
     */
    [0] = LAYOUT(
        KC_MPRV,   KC_MPLY,   KC_MNXT,
        KC_P4,   KC_P5,   KC_P6,
        KC_P1,   KC_P2,   KC_P3
    )
};

const uint16_t PROGMEM encoder_map[][1][2] = {
    [0] = {ENCODER_CCW_CW(KC_VOLU, KC_VOLD)},
};

const uint16_t PROGMEM encoder_map_press[] = {KC_MNXT, KC_P6, KC_P3, COMBO_END};
combo_t key_combos[] = {
    COMBO(encoder_map_press, KC_MUTE)};


#ifdef OLED_ENABLE

#define OLED_BUFFER_SIZE (128 * 32 / 8)  // bytes for full 128x32 bitmap

static uint8_t oled_buffer[OLED_BUFFER_SIZE];
static bool frame_ready = false;

// Called from raw HID with the frame bytes
void raw_hid_receive(uint8_t *data, uint8_t length) {
    if (length == OLED_BUFFER_SIZE) {
        memcpy(oled_buffer, data, OLED_BUFFER_SIZE);
        frame_ready = true;
    } else {
        frame_ready = false;
    }
}

bool oled_task_user(void) {
    if (frame_ready) {
        oled_write_raw((const char*)oled_buffer, OLED_BUFFER_SIZE);
    } else {
        oled_write_ln_P(PSTR("Itay's HackPad\nPlease connect to host and run the host script"), false);
    }
    return false;  // We don't need to redraw the OLED
}

#endif
