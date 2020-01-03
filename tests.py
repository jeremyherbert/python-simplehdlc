import unittest
from simplehdlc import SimpleHDLC


class ParserTests(unittest.TestCase):
    def test_encode_zero_length_payload(self):
        encoded = SimpleHDLC.encode(b"")

        self.assertEqual(len(encoded), 7)

    def test_encode(self):
        encoded = SimpleHDLC.encode(bytes([1]))

        self.assertEqual(encoded, bytes([0x7E, 0x00, 0x01, 0x01, 0xA5, 0x05, 0xDF, 0x1B]))

    def test_encode_escaping(self):
        encoded = SimpleHDLC.encode(bytes([0x7E, 0x7D]))

        self.assertEqual(encoded, bytes([0x7E, 0x00, 0x02, 0x7D, 0x7E ^ (1<<5), 0x7D, 0x7D ^ (1<<5), 0xDE, 0xD1,
                                         0x4B, 0x06]))

    def test_parse(self):
        encoded = SimpleHDLC.encode(bytes([1]))

        parsed = False

        def parse_success(payload):
            nonlocal parsed
            self.assertEqual(payload, bytes([1]))
            parsed = True

        hdlc = SimpleHDLC(parse_success)
        hdlc.parse(encoded)
        self.assertTrue(parsed)

    def test_parse_zero_length(self):
        encoded = SimpleHDLC.encode(b'')

        parsed = False

        def parse_success(payload):
            nonlocal parsed
            self.assertEqual(payload, b'')
            parsed = True

        hdlc = SimpleHDLC(parse_success)
        hdlc.parse(encoded)
        self.assertTrue(parsed)

    def test_parse_packet_too_big(self):
        encoded = SimpleHDLC.encode(bytes([0] * 10))

        parsed = False

        def parse_success(payload):
            nonlocal parsed
            parsed = True

        hdlc = SimpleHDLC(parse_success, max_len=9)
        hdlc.parse(encoded)
        self.assertFalse(parsed)

        hdlc = SimpleHDLC(parse_success, max_len=10)
        hdlc.parse(encoded)
        self.assertTrue(parsed)


if __name__ == '__main__':
    unittest.main()
