class FakeDevice:
    def __init__(self):
        pass

    async def query(self, cmd: str) -> bytes:
        stubs = {
            "QPIGS" : "(218.6 49.9 230.0 49.9 0368 0265 007 396 53.10 013 021 0046 0013 226.4 00.00 00000 00010010 00 00 01049 010xx\r",
            "QPIRI" : "(230.0 21.7 230.0 50.0 21.7 5000 5000 48.0 51.0 50.8 58.4 54.8 2 030 090 0 2 1 9 01 0 0 52.0 0 1 000xx\r",
            "QPIWS" : "(00000000000010000000000000000000xx\r",
            "QMOD"  : "(Bxx\r"
        }

        if cmd not in stubs:
            return "(NAK\r".encode()
        
        return stubs[cmd].encode()