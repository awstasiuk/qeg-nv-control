import numpy as np
import pyvisa
import time


class SG384Control:
    def __init__(self, visa_address):
        """
        Initializes an instance of the SG384 device class.
        Args:
            visa_address (str): The VISA address of the device to connect to.
        Attributes:
            visa_address (str): Stores the VISA address of the device.
            instr: Represents the instrument connection object. Initialized as None.
        """
        
        self.visa_address = visa_address
        self.instr = None
        self.connect()

    def connect(self):
        """
        Establishes a connection to the SG384 device using the specified VISA address.
        This method initializes a connection to the SG384 signal generator by creating
        a PyVISA resource manager, opening the resource at the provided VISA address,
        and setting the appropriate read and write terminations. It also verifies the
        connection by querying the device's identification string.
       
        Prints:
            A success message indicating the connection to the SG384 device if the
            connection is successful.
            An error message if the connection fails.
        """
        
        rm = pyvisa.ResourceManager()
        try:
            self.instr = rm.open_resource(self.visa_address)
        except pyvisa.errors.VisaIOError as e:
            print(f"Error connecting to SG384: {e}")
            return
        self.instr.read_termination = "\n"
        self.instr.write_termination = "\n"
        time.sleep(0.1)
        if self.instr.query("*IDN?"):
            print(f"Connected to SG384 at {self.visa_address}")
        else:
            print("Device connected but not responding.")

    def send_command(self, command, wait=0.1):
        r"""
        Writes command to the device and waits 100ms by default. This function
        does not check for errors in the command. It is assumed that the command is valid.
        Args:
            command (str): The command to send to the device.
            wait (float): The time to wait after sending the command, in seconds. Default is 0.1 seconds.
        """
        self.instr.write(command)
        time.sleep(wait)  # Add a small delay to ensure the command is processed

    def set_amplitude(self, amplitude):
        r"""
        Sets the amplitude of the type-N RF output to `amplitude` in units of dBm
        """
        command = f"AMPR {amplitude}"
        self.send_command(command)

    def set_amplitude_lf(self, amplitude):
        r"""
        Sets the amplitude of the BNC LF output to `amplitude` in units of dBm
        """
        command = f"AMPL {amplitude}"
        self.send_command(command)

    def set_frequency(self, frequency):
        r"""
        Sets the frequency of the SG384 to `frequency` in units of Hz.
        """
        command = f"FREQ {frequency}"
        self.send_command(command)

    def get_frequency(self):
        r"""
        Get the frequency of the SG384 device, in units of MHz
        """
        return float(self.instr.query("FREQ?MHz"))

    def ntype_on(self, print_me=True):
        r"""
        Turns on/off the rf. send `boolean`=True or 1 to turn on RF. Send `boolean`=False or 0
        to turn off the rf.
        """
        command = f"ENBR 1"
        self.send_command(command)
        if print_me:
            print(f"N-type RF bool set to on")
    
    def ntype_off(self, print_me=True):
        r"""
        Turns on/off the rf. send `boolean`=True or 1 to turn on RF. Send `boolean`=False or 0
        to turn off the rf.
        """
        command = f"ENBR 0"
        self.send_command(command)
        if print_me:
            print(f"N-type RF bool set to off")


    def bnctype_on(self, bool2, print_me=True):
        command = f"ENBL {bool2}"
        self.send_command(command)
        if print_me:
            print(f"bnc-type RF bool set to {bool2}")
            
    def enable_modulation(self, print_me=True):
        r"""
        Turns on the modulation.
        """
        command = f"MODL 1"
        self.send_command(command)
        if print_me:
            print(f"Modulation bool set to on")
    
    def disable_modulation(self, print_me=True):
        r"""
        Turns off the modulation. 
        """
        command = f"MODL 0"
        self.send_command(command)
        if print_me:
            print(f"Modulation bool set to off")    

    def do_set_modulation_type(self, mtype):
        """
        Sets the modulation type for the device.
        Parameters:
            mtype (str): The modulation type to set. Must be one of the following:
                         "AM" - Amplitude Modulation
                         "FM" - Frequency Modulation
                         "PHASEM" - Phase Modulation
                         "SWEEP" - Sweep Modulation
                         "PULSE" - Pulse Modulation
                         "BLANK" - Blank Modulation
                         "IQ" - IQ Modulation
        
        Sends:
            A command to the device in the format "TYPE <modulation_code>", where <modulation_code>
            is the corresponding integer value for the specified modulation type.
        """

        type_dict = {"AM": 0, "FM": 1, "PHASEM": 2, "SWEEP": 3, "PULSE": 4, "BLANK": 5, "IQ": 6}
        type = type_dict.get(mtype, -1)
        if type == -1:
            print(f"Modulation type {mtype} not recognized. Please use one of the following: {list(type_dict.keys())}")
            return
        self.send_command("TYPE %s" % type_dict[mtype])

    def close(self):
        """
        Closes the connection to the SG384 device.
        """
        self.instr.close()
        print("Connection closed.")
