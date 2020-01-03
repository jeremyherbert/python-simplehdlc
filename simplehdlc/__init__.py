# SPDX-License-Identifier: MIT

import binascii
from typing import Callable


class SimpleHDLC(object):
    FRAME_BOUNDARY_MARKER = 0x7E
    ESCAPE_MARKER = 0x7D

    STATE_WAITING_FOR_FRAME_MARKER = 0
    STATE_CONSUMING_SIZE_MSB = 1
    STATE_CONSUMING_SIZE_LSB = 2
    STATE_CONSUMING_PAYLOAD = 3

    def __init__(self, success_callback: Callable[[bytes], None], max_len=1024):
        self._success_callback = success_callback

        self._max_len = max_len

        self._expected_len = 0

        self._rx_crc32 = 0
        self._rx_crc32_count = 0
        self._escape_next = False
        self._state = SimpleHDLC.STATE_WAITING_FOR_FRAME_MARKER
        self._pending_payload = []

    def parse(self, data: bytes):
        for c in data:
            if c == SimpleHDLC.FRAME_BOUNDARY_MARKER:
                self._expected_len = 0
                self._rx_crc32 = 0
                self._rx_crc32_count = 0
                self._escape_next = False
                self._state = SimpleHDLC.STATE_CONSUMING_SIZE_MSB
                self._pending_payload.clear()
                continue

            if self._state == SimpleHDLC.STATE_WAITING_FOR_FRAME_MARKER:
                continue

            if self._escape_next:
                c ^= (1 << 5)
                self._escape_next = False
            elif c == SimpleHDLC.ESCAPE_MARKER:
                self._escape_next = True
                continue

            if self._state == SimpleHDLC.STATE_CONSUMING_SIZE_MSB:
                self._expected_len |= c << 8
                self._state = SimpleHDLC.STATE_CONSUMING_SIZE_LSB

            elif self._state == SimpleHDLC.STATE_CONSUMING_SIZE_LSB:
                self._expected_len |= c
                self._expected_len += 4  # for CRC32

                if self._expected_len > (self._max_len + 4):
                    self._state = SimpleHDLC.STATE_WAITING_FOR_FRAME_MARKER
                else:
                    self._state = SimpleHDLC.STATE_CONSUMING_PAYLOAD

            elif self._state == SimpleHDLC.STATE_CONSUMING_PAYLOAD:
                if len(self._pending_payload) < (self._expected_len - 4):
                    self._pending_payload.append(c)
                else:
                    self._rx_crc32 |= c
                    self._rx_crc32_count += 1

                    if self._rx_crc32_count == 4:
                        computed_crc32 = binascii.crc32(bytes(self._pending_payload))

                        if self._rx_crc32 == computed_crc32:
                            self._success_callback(bytes(self._pending_payload))

                        self._state = SimpleHDLC.STATE_WAITING_FOR_FRAME_MARKER
                    else:
                        self._rx_crc32 <<= 8

    @classmethod
    def encode(cls, payload: bytes) -> bytes:
        if len(payload) > 65536:
            raise ValueError("Maximum length of payload is 65536")

        output = [SimpleHDLC.FRAME_BOUNDARY_MARKER]

        def add_to_buffer(b: int):
            if b == SimpleHDLC.FRAME_BOUNDARY_MARKER or b == SimpleHDLC.ESCAPE_MARKER:
                output.append(SimpleHDLC.ESCAPE_MARKER)
                output.append(b ^ (1 << 5))
            else:
                output.append(b)

        add_to_buffer((len(payload) & 0xFF00) >> 8)
        add_to_buffer(len(payload) & 0xFF)

        for c in payload:
            add_to_buffer(c)

        crc32 = binascii.crc32(payload)

        add_to_buffer((crc32 & 0xFF000000) >> 24)
        add_to_buffer((crc32 & 0xFF0000) >> 16)
        add_to_buffer((crc32 & 0xFF00) >> 8)
        add_to_buffer((crc32 & 0xFF))

        return bytes(output)
