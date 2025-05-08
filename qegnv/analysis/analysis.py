import numpy as np
from scipy.optimize import curve_fit
import matplotlib
import matplotlib.pyplot as plt

from qegnv.experiment.config import u
from qegnv.experiment.base_experiment import Experiment

class DataFitter:
    def __init__(self, experiment):
        """
        Initialize the DataFitter with an experiment instance.
        
        :param experiment: An instance of an experiment class containing data to fit.
        """
        self.experiment = experiment
        self.fit_results = {}
        self.load_data()
        
    def load_data(self):
        """
        Pull data from the experiment instance, and prepare it for fitting and plotting.
        """
        contrast = np.array(self.experiment.counts0) - np.array(self.experiment.counts_ref0)
        self.x_data = np.array(self.experiment.var_vec) / self.experiment.x_axis_scale
        self.x_label = self.experiment.x_axis_label
        
        if self.experiment.counts1 is None:
            self.y_label = "Contrast [a.u.]"
            self.y_data = contrast
        else:
            self.y_label = r"<$\sigma_z$> [a.u.]"
            self.y_data = contrast -  (np.array(self.experiment.counts1) - np.array(self.experiment.counts_ref1))
        

    def fit(self, model_function, initial_params=None, bounds=(-np.inf, np.inf)):
        """
        Fit the experiment data to a given model function.
        
        :param model_function: A callable representing the model to fit the data to.
        :param initial_params: Initial guess for the parameters.
        :param bounds: Bounds for the parameters as a tuple (lower_bounds, upper_bounds).
        :return: The optimized parameters and covariance matrix.
        """
        try:
            params, covariance = curve_fit(model_function, self.x_data, self.y_data, p0=initial_params, bounds=bounds)
            self.fit_results[model_function.__name__] = (params, covariance)
            return params, covariance
        except Exception as e:
            print(f"Error during fitting: {e}")
            return None, None
        
    def plot_fit(self, model_function, inline=True, initial_params=None, bounds=(-np.inf, np.inf)):
        """
        Plot the fitted function along with the experimental data. If the fit results for the model
        are not available, it will perform the fit first.

        :param model_function: The model function used for fitting.
        :param ax: A matplotlib Axes object to plot on. If None, a new figure is created.
        :param initial_params: Initial guess for the parameters (used if fitting is required).
        :param bounds: Bounds for the parameters as a tuple (lower_bounds, upper_bounds) (used if fitting is required).
        """

        # Check if fit results for the model exist
        fit_result = self.get_fit_results(model_function.__name__)
        if fit_result is None:
            # Perform the fit if no results are available
            params, _ = self.fit(model_function, initial_params=initial_params, bounds=bounds)
            if params is None:
                print(f"Could not fit the model: {model_function.__name__}")
                return
        else:
            params, _ = fit_result

        fig = plt.figure()
        # Plot the experimental data
        plt.scatter(self.x_data, self.y_data, label="Data", color="blue", alpha=0.7)

        # Generate the fitted curve
        x_fit = np.linspace(min(self.x_data), max(self.x_data), 500)
        y_fit = model_function(x_fit, *params)
        plt.plot(x_fit, y_fit, label="Fit", color="red")

        # Add labels and legend
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.legend()

        plt.show(block=False)

    def get_fit_results(self, model_name):
        """
        Retrieve the fit results for a specific model.
        
        :param model_name: The name of the model function.
        :return: The parameters and covariance matrix, or None if not found.
        """
        return self.fit_results.get(model_name, None)
