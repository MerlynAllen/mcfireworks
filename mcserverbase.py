import socket
import collections
import struct

Packet = collections.namedtuple("Packet", ("ident", "kind", "payload"))


class IncompletePacket(Exception):
    def __init__(self, minimum):
        self.minimum = minimum


class ServerBase():
    # BUFSIZE = 4096
    def __init__(self):
        self.__sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__logged_in__ = False
        pass

    def login(self, host, port, password):
        self.__host__ = host
        self.__port__ = port
        self.__sock__.connect((host, port))
        self.__logged_in__ = True
        """
        Send a "login" packet to the server. Returns a boolean indicating whether
        the login was successful.
        """

        self.send_packet(Packet(0, 3, password.encode("utf8")))
        packet = self.receive_packet()
        return packet.ident == 0

    @staticmethod
    def decode_packet(data):
        """
        Decodes a packet from the beginning of the given byte string. Returns a
        2-tuple, where the first element is a ``Packet`` instance and the second
        element is a byte string containing any remaining data after the packet.
        """

        if len(data) < 14:
            raise IncompletePacket(14)

        length = struct.unpack("<i", data[:4])[0] + 4
        if len(data) < length:
            raise IncompletePacket(length)

        ident, kind = struct.unpack("<ii", data[4:12])
        payload, padding = data[12:length-2], data[length-2:length]
        assert padding == b"\x00\x00"
        return Packet(ident, kind, payload), data[length:]

    def receive_packet(self):
        """
        Receive a packet from the given socket. Returns a ``Packet`` instance.
        """

        data = b""
        while True:
            try:
                return self.decode_packet(data)[0]
            except IncompletePacket as exc:
                while len(data) < exc.minimum:
                    data += self.__sock__.recv(exc.minimum - len(data))

    def command(self, text):
        """
        Sends a "command" packet to the server. Returns the response as a string.
        """

        self.send_packet(Packet(0, 2, text.encode("utf8")))
        self.send_packet(Packet(1, 0, b""))
        response = b""
        while True:
            packet = self.receive_packet()
            if packet.ident != 0:
                break
            response += packet.payload
        return response.decode("utf8")

    @staticmethod
    def encode_packet(packet):
        """
        Encodes a packet from the given ``Packet` instance. Returns a byte string.
        """

        data = struct.pack("<ii", packet.ident, packet.kind) + \
            packet.payload + b"\x00\x00"
        return struct.pack("<i", len(data)) + data

    def receive_packet(self):
        """
        Receive a packet from the given socket. Returns a ``Packet`` instance.
        """

        data = b""
        while True:
            try:
                return self.decode_packet(data)[0]
            except IncompletePacket as exc:
                while len(data) < exc.minimum:
                    data += self.__sock__.recv(exc.minimum - len(data))

    def send_packet(self, packet):
        """
        Send a packet to the given socket.
        """

        self.__sock__.sendall(self.encode_packet(packet))
