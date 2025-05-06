import numpy as np
from scipy.optimize import curve_fit

from qegnv.experiment.config import u
from qegnv.experiment.base_experiment import Experiment

class DataFitter:
    def __init__(self, experiment):
        """
        Initialize the DataFitter with an experiment instance.
        
        :param experiment: An instance of an experiment class containing data to fit.
        """
        self.experiment = experiment
        self.load_data()
        
    def load_data(self):
        """
        Pull data from the experiment instance, and prepare it for fitting and plotting.
        """
        contrast = self.experiment.counts0 - self.experiment.counts_ref0
        self.x_data = self.experiment.var_vec / self.experiment.x_axis_scale
        self.x_label = self.experiment.x_axis_label
        
        if self.experiment.counts1 is None:
            self.y_label = "Contrast [a.u.]"
            self.y_data = (self.experiment.var_vec, contrast)
        else:
            self.y_label = r"<$\sigma_z$> [a.u.]"
            self.y_data = contrast -  (self.experiment.counts1 - self.experiment.counts_ref1)
        

    def fit(self, model_function, initial_params=None, bounds=(-np.inf, np.inf)):
        """
        Fit the experiment data to a given model function.
        
        :param model_function: A callable representing the model to fit the data to.
        :param initial_params: Initial guess for the parameters.
        :param bounds: Bounds for the parameters as a tuple (lower_bounds, upper_bounds).
        :return: The optimized parameters and covariance matrix.
        """
        x_data, y_data = self.data
        try:
            params, covariance = curve_fit(model_function, x_data, y_data, p0=initial_params, bounds=bounds)
            self.fit_results[model_function.__name__] = (params, covariance)
            return params, covariance
        except Exception as e:
            print(f"Error during fitting: {e}")
            return None, None

    def get_fit_results(self, model_name):
        """
        Retrieve the fit results for a specific model.
        
        :param model_name: The name of the model function.
        :return: The parameters and covariance matrix, or None if not found.
        """
        return self.fit_results.get(model_name, None)

# Example usage:
# Assuming `experiment` is an instance of an experiment class with a `get_data()` method
# that returns (x_data, y_data).

# def linear_model(x, a, b):
#     return a * x + b

# fitter = DataFitter(experiment)
# params, cov = fitter.fit(linear_model, initial_params=[1, 0])
# print("Fit parameters:", params)