from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "NotInstalledYet"
    
import qegnv.analysis
import qegnv.devices
import qegnv.experiment

import qegnv.analysis.analysis
import qegnv.analysis.models
import qegnv.devices.SG384
import qegnv.experiment.base_experiment
import qegnv.experiment.experiment
import qegnv.experiment.config

from qegnv.analysis.analysis import DataFitter
from qegnv.analysis.models import Lorentzian, Gaussian, ExpDampedCosine
from qegnv.experiment.experiment import NVExperiment
from qegnv.experiment.config import ConfigNV, u
