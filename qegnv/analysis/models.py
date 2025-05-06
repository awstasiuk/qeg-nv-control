import numpy as np
import scipy as sp

def Gaussian(x, amplitude, mean, stddev):
    """Gaussian function."""
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2))

def Lorentzian(x, amplitude, mean, gamma):
    """Lorentzian function."""
    return amplitude * (gamma ** 2) / ((x - mean) ** 2 + gamma ** 2)

def ExpDampedCosine(x, amplitude, decay, frequency, phase):
    """Exponentially damped cosine function."""
    return amplitude * np.exp(-decay * x) * np.cos(2 * np.pi * frequency * x + phase)