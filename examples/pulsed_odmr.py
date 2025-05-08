import qegnv as qnv
from qegnv import u
import numpy as np
import matplotlib.pyplot as plt

cfg = qnv.ConfigNV()
expt = qnv.NVExperiment(cfg)
f_vec = np.arange(75 * u.MHz, 85 * u.MHz, 0.2 * u.MHz)
expt.setup_pulsed_odmr(f_vec=f_vec, amplitude=1)
expt.execute_experiment(n_avg=1e5)
expt.save("p_odmr_example.expt")

fitter = qnv.DataFitter(expt)
# fit to a lorenztian with initial amplitude=1, mean=80, and gamma=0.5
params, cov = fitter.fit(qnv.Lorentzian, initial_params=[1, 80, 0.5], bounds=(0, np.inf))
print("Fitted parameters:", params)
# plot the fit
fitter.plot_fit(qnv.Lorentzian)

# update th config with the new fitted parameters
cfg.NV_LO_freq = params[1] * qnv.u.MHz
cfg.save("p_odmr_example.cfg")