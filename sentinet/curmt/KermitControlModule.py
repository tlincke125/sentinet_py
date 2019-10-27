from sentinet.core.control import ControlClient, pub_params, sub_params
from sentinet.core.messages.Message import Data_Message, Ping_Message
from sentinet.core.messages.MessageKeys import *
from struct import pack

CMD_VEL = "tcp://localhost:5570"
DATA_ADDR = "tcp://localhost:5556"
COMMAND_ADDR = "tcp://localhost:5570"
REAL_TIME_ADDR = "tcp://localhost:5571"


class KermitControlModule:

    def __init__(self):

        # Control Client
        self.control = None
    
        # Real time requsting channel 
        self.requesting = False
        # Real time publish channel
        self.publishing = False

        # Messages
        self.cmd_vel_data = None
        self.command_data = None

        # Params
        self.cmd_vel = None
        self.cmd_vel_callback = None

        self.data = None
        self.data_callback = None

        self.command = None

    def start_kermit(self):
        # Start control module
        self.control = ControlClient(self.publishing, (self.requesting, CMD_VEL))
        # Start data subscriber if implimented
        self.control.spin_subscriber(self.data) if self.data is not None else print("Data not implimented")
        # Start publisher module if implimented
        self.control.spin_publisher(self.cmd_vel) if self.cmd_vel is not None else print("Cmd vel not implimented")
        
    # Stop kermit
    def quit_kermit(self):
        self.control.quit()

    def __cmd_vel_get_data(self):
        a, l = self.cmd_vel_callback()
        self.cmd_vel_data.set_data(a, 4, FLOAT, 0)
        self.cmd_vel_data.set_data(l, 4, FLOAT, 1)
        return bytes(self.cmd_vel_data.message)

    def set_cmd_vel_get_data(self, func):
        # Initialize message space
        self.cmd_vel_data = Data_Message()
        self.cmd_vel_data.push_data(0.0, 4, FLOAT)
        self.cmd_vel_data.push_data(0.0, 4, FLOAT)
        self.cmd_vel_data.to_wire()

        # Nothing to do with CC
        self.cmd_vel_callback = func

        # Create a new pub params
        self.cmd_vel = pub_params()
        # The address to publish to 
        self.cmd_vel.address = CMD_VEL
        # The callback to get data
        self.cmd_vel.get_data = self.__cmd_vel_get_data
        # The topic
        self.cmd_vel.topic = "cmd_vel"
        # The period to publish on
        self.cmd_vel.period = 0.000001
        # The start on creation
        self.cmd_vel.start_on_creation = True 

    # func gets two floats and returns void
    def __data_callback(self, incomming_message):
        self.data.parse_from_similar_message(incomming_message)
        a = struct.unpack('f', self.data.get_data(0))
        b = struct.unpack('f', self.data.get_data(1))
        self.data_callback(a, b)

    def set_data_callback(self, func):
        self.data = Data_Message()
        self.data.push_data(0.0, 4, FLOAT)
        self.data.push_data(0.0, 4, FLOAT)

        # Nothing to do with CC
        self.data_callback = func

        # Create a new sub params
        self.data = sub_params()
        # Attach callback, takes in a string, needs a wrapper function
        self.data.callback = self.__data_callback
        # Attach the data topic
        self.data.topic = "data"
        # Start on creation
        self.data.start_on_creation = True
