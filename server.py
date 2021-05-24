"""
Receives key inputs from clients and performs them on host machine

To use over the internet, port forward 6700 to your machine's local ip address on port 6700 (NOT TESTED)
If using locally, clients can connect with the local ip address of the host

Only use with trusted people, in theory only letters, numbers, space, backspace, enter and tab can be simulated, however
there may be exploits.
"""

from network import Network
from split import split
import urllib.request
import threading
import time
import queue
import pynput
import string

# used to control keyboard input
kb_controller = pynput.keyboard.Controller()

# a list of keys that are allowed (excluding extras such as space)
ALLOWED_INPUT = [split(string.ascii_letters) + split(string.digits)]

# maps extra keys to pynput keys
KEY_WORDS = {
    "space": pynput.keyboard.Key.space,
    "tab": pynput.keyboard.Key.tab,
    "backspace": pynput.keyboard.Key.backspace,
    "enter": pynput.keyboard.Key.enter
             }


class ServerNetwork(Network):
    def __init__(self):
        super().__init__()
        # use an api to get the external ip address
        self.gateway_ip = urllib.request.urlopen("https://api.ipify.org").read().decode()
        # a list of client connections
        self.connections = []
        # a queue with all messages received from clients
        self.message_queue = queue.Queue()

    def start_server(self):
        # print external ip address, used for others to connect
        print("Your code is:", self.gateway_ip)
        # bind socket to local ip address and port 6700
        self.network_socket.bind((self.local_machine_ip, self.port))
        print("Bound socket to", self.local_machine_ip, ":", self.port)
        # begin listening for incoming connections
        self.network_socket.listen(8)
        print("Listening for connections...")
        # launch a thread that automatically accepts incoming connections
        # a thread is needed because .accept() is a blocking call
        accept_thread = threading.Thread(target=self.accept_connections_thread, daemon=True)
        accept_thread.start()
        print("Started new thread for accepting connections")

    def accept_connections_thread(self):
        """
        Accept incoming connections, add to the connection list and launch a thread to receive data from each client
        """
        while True:
            # maximum clients is 8
            if len(self.connections) < 8:
                connection = self.network_socket.accept()
                print("Accepted new connection:", connection[1])
                self.connections.append(connection)
                # launch a new thread that receives messages from clients, as .recv() is a blocking call
                recv_thread = threading.Thread(target=self.recv_message_thread, daemon=True, args=(connection,))
                recv_thread.start()
                print("Started new thread to receive data from", connection[1])
                if len(self.connections) == 8:
                    print("Max connections reached. (8)")
            time.sleep(1)

    def recv_message_thread(self, conn):
        """
        Receive messages from given connection and put into queue
        """
        while True:
            try:
                message = conn[0].recv(128)
                self.message_queue.put(message)
            except WindowsError:
                print("DISCONNECTED FROM", conn[1])
                break
            time.sleep(1)


s = ServerNetwork()
s.start_server()

while True:
    # messages have been received if queue isnt empty
    if not s.message_queue.empty():
        keys = s.message_queue.get().decode()

        # offset is a variable used to offset the index when iterating to skip past words such as `backspace`
        offset = 0
        for key_index in range(len(keys)):
            key_index = key_index + offset

            try:
                key = keys[key_index]
            except IndexError:
                # loop is over, offset has caused a larger index than is available
                break

            # normal key is pressed
            if key != "`" and key in ALLOWED_INPUT:
                print("Pressing: ", key)
                kb_controller.press(key)
                kb_controller.release(key)
            else:
                # find ending `
                end = keys[key_index+1:].index("`") + 1
                # extract the extra key ('space', 'enter' etc.)
                key_word = keys[key_index + 1:key_index + end]
                print("Pressing: ", key_word)
                try:
                    # check it is a valid extra key and press
                    if key_word in KEY_WORDS.keys():
                        kb_controller.press(KEY_WORDS[key_word])
                        kb_controller.release(KEY_WORDS[key_word])
                except:
                    print("Invalid Key Input")
                offset += (end + 1)
