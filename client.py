"""
Client's keystrokes are sent to the server's computer
"""

from network import Network
import string
import pynput
from split import split

# whether to prevent connecting and sending data to a server
DISABLE_NETWORK = False


class NetworkClient(Network):
    def __init__(self):
        if not DISABLE_NETWORK:
            super().__init__()
            # ask user to input server ip
            self.server_ip_code = self.enter_server_code()
            self.connect()

    @staticmethod
    def enter_server_code():
        server_code = input("Enter host's code: ")
        return server_code

    def connect(self):
        self.network_socket.connect((self.server_ip_code, self.port))

    def send_key(self, key: str):
        """Sends the key to the server"""
        print("Sending key: Value:", key)
        self.network_socket.send(key.encode())


class KeyboardLogger:
    def __init__(self):
        # a list of allowed keypresses that will be sent to server
        self.allowed_keypresses = split(string.ascii_letters) + split(string.digits) + [
            # extra buttons, surrounded by ` as it is used to mark the beginning and end of extra inputs
            "`tab`", "`space`", "`backspace`", "`enter`"
        ]

    def key_press(self, key):
        try:
            # add ` so that the server knows that the buttons are extra (not numbers/letters)
            key_value = '`' + key.name + '`'
        except:
            # button isnt extra, get 'char' property
            key_value = key.char

        # check input is allowed and script is running on network, then send
        if key_value in self.allowed_keypresses and not DISABLE_NETWORK:
            n.send_key(key_value)
        # Ctrl Q can be used to exit the script from anywhere
        if repr(key_value)[1:-1] == r"\x11":  # Ctrl Q
            exit()


n = NetworkClient()
k = KeyboardLogger()

# begin listening for keys
with pynput.keyboard.Listener(on_press=k.key_press) as listener:
    listener.join()
