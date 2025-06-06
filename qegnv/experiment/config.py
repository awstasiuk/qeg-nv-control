import json

from datetime import datetime
import numpy as np

from qegnv.utils import NumpyEncoder, can_save_json
from qegnv.devices.SG384 import SG384Control


from qualang_tools.units import unit
from qm import QuantumMachinesManager

u = unit(coerce_to_integer=True)


# IQ imbalance matrix
def IQ_imbalance(g, phi):
    """
    Creates the correction matrix for the mixer imbalance caused by the gain and phase imbalances, more information can
    be seen here:
    https://docs.qualang.io/libs/examples/mixer-calibration/#non-ideal-mixer
    :param g: relative gain imbalance between the 'I' & 'Q' ports. (unit-less), set to 0 for no gain imbalance.
    :param phi: relative phase imbalance between the 'I' & 'Q' ports (radians), set to 0 for no phase imbalance.
    """
    c = np.cos(phi)
    s = np.sin(phi)
    N = 1 / ((1 - g**2) * (2 * c**2 - 1))
    return [float(N * x) for x in [(1 - g) * c, (1 + g) * s, (1 - g) * s, (1 + g) * c]]


class ConfigNV:
    __initialized = False

    def __init__(self, filename=None, connect_qmm=True, connect_SG1=True, connect_SG2=True):
        """
        Initializes the configuration for the experiment.
        This constructor sets up the configuration by either loading a default 
        configuration or loading a specified configuration file. It also establishes 
        connections to various components of the system and updates the configuration 
        state.
        
        Args:
            filename (str, optional): The name of the configuration file to load. 
                If not provided, a default configuration is loaded, and a new 
                filename is generated based on the current date in the format 
                'config_YYYYMMDD.json'.
            connect_qmm (bool, optional): Whether to establish a connection to the 
                Quantum Machine Manager (QMM). Defaults to True.
            connect_SG1 (bool, optional): Whether to establish a connection to the 
                first microwave source (SG1). Defaults to True.
            connect_SG2 (bool, optional): Whether to establish a connection to the 
                second microwave source (SG2). Defaults to True.
                
        Methods:
            - `load_default()`: Loads the default configuration parameters and addresses.
            - `load(filename)`: Loads configuration parameters and addresses from the 
              specified file.
            - `connect(qmm, SG1, SG2)`: Establishes connections to the specified components.
            - `update_config()`: Updates the configuration state based on the current 
              parameters and connections.
            - `save(filename)`: Saves the current configuration to a JSON file.
            
        Notes:
            - If no filename is provided, the configuration is initialized with default 
              parameters, and a new configuration file is named using the current date.
            - The `connect` method is used to establish connections to the Quantum Machine 
              Manager and microwave sources, which are essential for the experiment setup.
            - The `update_config` method ensures that the configuration state is consistent 
              and up-to-date after loading or modifying parameters. This automatically runs
              when modifying the attributes of the class.
        """
        
        # load parameters and addresses
        if filename is None:
            self.load_default()
            filename = f"config_{datetime.now().strftime('%Y%m%d')}.json"
        else:
            self.load(filename)
        self.filename = filename

        self.connect(qmm=connect_qmm, SG1=connect_SG1, SG2=connect_SG2)
        self.update_config()
        self.__initialized = True

    def connect(self, qmm=True, SG1=True, SG2=True):
        """
        Establishes connections to various components required for the experiment. This
        class assumes that there are no more than 2 microwave sources connected to the QM,
        and that both are SG384 devices. This can be generalized in the future if hardware
        changes.
        
        Parameters:
            qmm (bool): If True, initializes the Quantum Machines Manager (QMM) connection.
                        Default is True.
            SG1 (bool): If True, initializes the SG384Control connection for the first microwave port.
                        Default is True.
            SG2 (bool): If True, initializes the SG384Control connection for the second microwave port.
                        Default is True.
        Initializes:
            self.qmm: An instance of QuantumMachinesManager if `qmm` is True.
            self.SG384_1: An instance of SG384Control for the first microwave port if `SG1` is True.
            self.SG384_2: An instance of SG384Control for the second microwave port if `SG2` is True.
        """
        
        if qmm:
            self.qmm = QuantumMachinesManager(
                host=self.qop_ip, cluster_name=self.cluster_name, octave=self.octave_config
            )
        if SG1:
            self.SG384_1 = SG384Control(self.mw_port1)
        if SG2:
            self.SG384_2 = SG384Control(self.mw_port2)

    def enable_SG(self):
        """
        Checks if the microwave sources are connected and enables them.
        """
        if self.SG384_1 is not None:
            self.enable_SG1()
        if self.SG384_2 is not None:
            self.enable_SG2()

    def enable_SG1(self):
        """
        Enables the microwave source for the NV center.
        """
        self.SG384_1.set_amplitude(self.SG1_LO_amp)
        self.SG384_1.set_frequency(self.SG1_LO_freq)
        self.SG384_1.ntype_on()
        self.SG384_1.enable_modulation()
        self.SG384_1.do_set_modulation_type("IQ")

    def disable_SG1(self):
        """
        Disables the microwave source for the NV center.
        """
        self.SG384_1.ntype_off()

    def enable_SG2(self):
        """
        Enable the microwave source for the dark spinss
        """
        self.SG384_2.set_amplitude(self.SG2_LO_amp)
        self.SG384_2.set_frequency(self.SG2_LO_freq)
        self.SG384_2.ntype_on()
        self.SG384_2.enable_modulation()
        self.SG384_2.do_set_modulation_type("IQ")

    def disable_SG2(self):
        """
        Disables the microwave source for the dark spins.
        """
        self.SG384_2.ntype_off()

    def save(self, filename=None):
        """
        Saves the configuration to a JSON file.
        """
        self.filename = filename if filename is not None else self.filename

        try:
            with open(self.filename, "w") as f:
                json.dump(self.to_dict(), f, cls=NumpyEncoder, indent=4)
        except (OSError, IOError) as e:
            print(f"Error saving file: {e}")

    def load(self, filename):
        """
        Loads the configuration from a JSON file.
        """
        try:
            with open(filename, "r") as f:
                attributes = json.load(f)
            self.__initialized = False
            for k, v in attributes.items():
                self.__dict__[k] = v
            self.__initialized = True
            self.filename = filename
        except (OSError, IOError, FileNotFoundError) as e:
            print(f"Error loading file: {e}")

    def to_dict(self):
        """
        Returns the configuration as a dictionary.
        """
        return {k: v for k, v in self.__dict__.items() if can_save_json(v)}

    @staticmethod
    def from_dict(d):
        """
        Creates a ConfigNV object from a dictionary.
        """
        config = ConfigNV(connect_SG1=False, connect_SG2=False, connect_qmm=False)
        config.__initialized = False
        for k, v in d.items():
            config.__dict__[k] = v
        config.__initialized = True
        config.update_config()
        return config

    def __repr__(self):
        return "\n".join(["ConfigNV Interface for QM", json.dumps(self.to_dict(), cls=NumpyEncoder, indent=4)])

    __str__ = __repr__

    def __setattr__(self, name, value):
        """
        Overrides the default python __setattr__ method to update the configuration dictionary whenever we
        make any changes to this object. This is necessary to ensure that the configuration is always up-to-date,
        and ensures that the setter avoids issues with infinite recursion and first-time initialization spam.
        """
        if self.__initialized and name != "config":
            self.__dict__[name] = value
            self.update_config()
        else:
            self.__dict__[name] = value

    def load_default(self):
        """
        Loads the default configuration for an NV experiment.
        """
        # communication addresses
        self.qop_ip = "18.25.10.244"
        self.cluster_name = "QM_NV2"
        self.qop_port = None  # Write the QOP port if version < QOP220
        self.octave_config = None  # Set octave_config to None if no octave are present
        self.mw_port1 = "TCPIP0::18.25.11.6::5025::SOCKET"
        self.mw_port2 = "TCPIP0::18.25.11.5::5025::SOCKET"

        # Signal generator parameters
        self.SG1_LO_freq = 1.769 * u.GHz #B = 365 Gauss
        self.SG1_LO_amp = -24  # in dBm
        self.SG2_LO_freq = 0.940 * u.GHz #free electron larmor frequency
        self.SG2_LO_amp = -23 # in dBm

        # Pulses lengths
        self.initialization_len_1 = 3000 * u.ns
        self.meas_len_1 = 600 * u.ns
        self.long_meas_len_1 = 10_000 * u.ns

        self.initialization_len_2 = 3000 * u.ns
        self.meas_len_2 = 500 * u.ns
        self.long_meas_len_2 = 5_000 * u.ns

        # Relaxation time from the metastable state to the ground state after during initialization
        self.relaxation_time = 300 * u.ns
        self.wait_for_initialization = 2 * self.relaxation_time 

        # NV MW parameters
        self.IF_freq_NV = 80 * u.MHz
        self.mw_amp_NV = 0.25  # in units of volts
        self.mw_len_NV = 500 * u.ns
        self.x180_amp_NV = 0.238  # in units of volts
        self.x180_len_NV = 500 * u.ns  # in units of ns
        self.x90_amp_NV = self.x180_amp_NV / 2  # in units of volts
        self.x90_len_NV = self.x180_len_NV  # in units of ns

        # X MW parameters
        self.IF_freq_X = 80 * u.MHz
        self.mw_amp_X = 0.25  # in units of volts
        self.mw_len_X = 500 * u.ns
        self.x180_amp_X = 0.144  # in units of volts
        self.x180_len_NV = 500 * u.ns  # in units of ns
        self.x90_amp_NV = self.x180_amp_NV / 2  # in units of volts
        self.x90_len_NV = self.x180_len_NV  # in units of ns

        # RF parameters
        self.rf_frequency = 10 * u.MHz
        self.rf_amp = 0.1
        self.rf_length = 1000 * u.ns

        # Readout parameters
        self.signal_threshold_1 = -8_00  # ADC untis, to convert to volts divide by 4096 (12 bit ADC)
        self.signal_threshold_2 = -2_000  # ADC untis, to convert to volts divide by 4096 (12 bit ADC)

        # Delays
        self.detection_delay_1 = 292 * u.ns
        self.detection_delay_2 = 80 * u.ns
        self.laser_delay_1 = 140 * u.ns
        self.laser_delay_2 = 0 * u.ns
        self.mw_delay = 0 * u.ns
        self.rf_delay = 0 * u.ns
        self.wait_between_runs = 500 * u.ns

        # IQ imbalance params
        self.g = 0.03
        self.phi = -0.05

    def update_config(self):
        """
        Updates the configuration dictionary with the latest values. This formatting is enforced by the QUA compiler,
        and may need updating in the future depending on how quantum machine hardware/software evolves.
        """
        self.config = {
            "version": 1,
            "controllers": {
                "con1": {
                    "type": "opx1",
                    "analog_outputs": {
                        1: {"offset": -0.02, "delay": self.mw_delay},  # NV I calibrated 20241029
                        2: {"offset": -0.02, "delay": self.mw_delay},  # NV Q calibrated 20241029
                        3: {"offset": -0.005, "delay": self.mw_delay},  # X I #calibrated 20241014
                        4: {"offset": -0.023, "delay": self.mw_delay},  # X Q #calibrated 20241014
                    },
                    "digital_outputs": {
                        1: {},  # AOM/Laser
                        2: {},  # AOM/Laser
                        3: {},  # SPCM1 - indicator
                        4: {},  # SPCM2 - indicator
                    },
                    "analog_inputs": {
                        1: {"offset": 0.004},  # SPCM1
                        2: {"offset": 0},  # SPCM2
                    },
                }
            },
            "elements": {
                "NV": {
                    "mixInputs": {
                        "I": ("con1", 1),
                        "Q": ("con1", 2),
                        "lo_frequency": self.SG1_LO_freq,
                        "mixer": "mixer_NV",
                    },
                    "intermediate_frequency": self.IF_freq_NV,
                    "operations": {
                        "cw": "const_pulse",
                        "x180": "x180_pulse",
                        "x90": "x90_pulse",
                        "-x90": "-x90_pulse",
                        "-y90": "-y90_pulse",
                        "y90": "y90_pulse",
                        "y180": "y180_pulse",
                    },
                },
                "RF": {
                    "singleInput": {"port": ("con1", 3)},
                    "intermediate_frequency": self.rf_frequency,
                    "operations": {
                        "const": "const_pulse_single",
                    },
                },
                "AOM1": {
                    "digitalInputs": {
                        "marker": {
                            "port": ("con1", 1),
                            "delay": self.laser_delay_1,
                            "buffer": 0,
                        },
                    },
                    "operations": {
                        "laser_ON": "laser_ON_1",
                    },
                },
                "AOM2": {
                    "digitalInputs": {
                        "marker": {
                            "port": ("con1", 2),
                            "delay": self.laser_delay_2,
                            "buffer": 0,
                        },
                    },
                    "operations": {
                        "laser_ON": "laser_ON_2",
                    },
                },
                "SPCM1": {
                    "singleInput": {"port": ("con1", 1)},  # not used
                    "digitalInputs": {  # for visualization in simulation
                        "marker": {
                            "port": ("con1", 3),
                            "delay": self.detection_delay_1,
                            "buffer": 0,
                        },
                    },
                    "operations": {
                        "readout": "readout_pulse_1",
                        "long_readout": "long_readout_pulse_1",
                    },
                    "outputs": {"out1": ("con1", 1)},
                    "outputPulseParameters": {
                        "signalThreshold": self.signal_threshold_1,  # ADC units
                        "signalPolarity": "Below",
                        "derivativeThreshold": -2_000,
                        "derivativePolarity": "Above",
                    },
                    "time_of_flight": self.detection_delay_1,
                    "smearing": 0,
                },
                "SPCM2": {
                    "singleInput": {"port": ("con1", 1)},  # not used
                    "digitalInputs": {  # for visualization in simulation
                        "marker": {
                            "port": ("con1", 4),
                            "delay": self.detection_delay_2,
                            "buffer": 0,
                        },
                    },
                    "operations": {
                        "readout": "readout_pulse_2",
                        "long_readout": "long_readout_pulse_2",
                    },
                    "outputs": {"out1": ("con1", 2)},
                    "outputPulseParameters": {
                        "signalThreshold": self.signal_threshold_2,  # ADC units
                        "signalPolarity": "Below",
                        "derivativeThreshold": -2_000,
                        "derivativePolarity": "Above",
                    },
                    "time_of_flight": self.detection_delay_2,
                    "smearing": 0,
                },
            },
            "pulses": {
                "const_pulse": {
                    "operation": "control",
                    "length": self.mw_len_NV,
                    "waveforms": {"I": "cw_wf", "Q": "zero_wf"},
                },
                "x180_pulse": {
                    "operation": "control",
                    "length": self.x180_len_NV,
                    "waveforms": {"I": "x180_wf", "Q": "zero_wf"},
                },
                "x90_pulse": {
                    "operation": "control",
                    "length": self.x90_len_NV,
                    "waveforms": {"I": "x90_wf", "Q": "zero_wf"},
                },
                "-x90_pulse": {
                    "operation": "control",
                    "length": self.x90_len_NV,
                    "waveforms": {"I": "minus_x90_wf", "Q": "zero_wf"},
                },
                "-y90_pulse": {
                    "operation": "control",
                    "length": self.x90_len_NV,
                    "waveforms": {"I": "zero_wf", "Q": "minus_x90_wf"},
                },
                "y90_pulse": {
                    "operation": "control",
                    "length": self.x90_len_NV,
                    "waveforms": {"I": "zero_wf", "Q": "x90_wf"},
                },
                "y180_pulse": {
                    "operation": "control",
                    "length": self.x180_len_NV,
                    "waveforms": {"I": "zero_wf", "Q": "x180_wf"},
                },
                "const_pulse_single": {
                    "operation": "control",
                    "length": self.rf_length,  # in ns
                    "waveforms": {"single": "rf_const_wf"},
                },
                "laser_ON_1": {
                    "operation": "control",
                    "length": self.initialization_len_1,
                    "digital_marker": "ON",
                },
                "laser_ON_2": {
                    "operation": "control",
                    "length": self.initialization_len_2,
                    "digital_marker": "ON",
                },
                "readout_pulse_1": {
                    "operation": "measurement",
                    "length": self.meas_len_1,
                    "digital_marker": "ON",
                    "waveforms": {"single": "zero_wf"},
                },
                "long_readout_pulse_1": {
                    "operation": "measurement",
                    "length": self.long_meas_len_1,
                    "digital_marker": "ON",
                    "waveforms": {"single": "zero_wf"},
                },
                "readout_pulse_2": {
                    "operation": "measurement",
                    "length": self.meas_len_2,
                    "digital_marker": "ON",
                    "waveforms": {"single": "zero_wf"},
                },
                "long_readout_pulse_2": {
                    "operation": "measurement",
                    "length": self.long_meas_len_2,
                    "digital_marker": "ON",
                    "waveforms": {"single": "zero_wf"},
                },
            },
            "waveforms": {
                "cw_wf": {"type": "constant", "sample": self.mw_amp_NV},
                "rf_const_wf": {"type": "constant", "sample": self.rf_amp},
                "x180_wf": {"type": "constant", "sample": self.x180_amp_NV},
                "x90_wf": {"type": "constant", "sample": self.x90_amp_NV},
                "minus_x90_wf": {"type": "constant", "sample": -self.x90_amp_NV},
                "zero_wf": {"type": "constant", "sample": 0.0},
            },
            "digital_waveforms": {
                "ON": {"samples": [(1, 0)]},  # [(on/off, ns)]
                "OFF": {"samples": [(0, 0)]},  # [(on/off, ns)]
            },
            "mixers": {
                "mixer_NV": [
                    {
                        "intermediate_frequency": self.IF_freq_NV,
                        "lo_frequency": self.SG1_LO_freq,
                        "correction": IQ_imbalance(self.g, self.phi),  # calibrated 20241029
                    },
                ],
            },
        }
