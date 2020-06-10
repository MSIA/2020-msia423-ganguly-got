import logging
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
from cycler import cycler
import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


def eda_plots(df, plot_location=None, target_column=None, eda_plot_features=None):
    """Churns EDA plots for all the features in the model data set

    :param df: model dataFrame
    :param target_column: dependent variable 'class'
    :param plot_location: local file location for storing EDA plots
    :param eda_plot_features: features to create EDA plots for

    :return: None, saves plots as .png files in data/plots
    """
    # Update matplotlib defaults to something nicer
    mpl_update = {
        'font.size': 16,
        'axes.prop_cycle': cycler('color', ['#0085ca', '#888b8d', '#00c389', '#f4364c', '#e56db1']),
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'figure.figsize': [12.0, 8.0],
        'axes.labelsize': 20,
        'axes.labelcolor': '#677385',
        'axes.titlesize': 20,
        'lines.color': '#0055A7',
        'lines.linewidth': 3,
        'text.color': '#677385'
    }
    mpl.rcParams.update(mpl_update)

    # separates dependent and independent variables
    features = df[eda_plot_features]
    target = df[target_column]

    # create plots folder to store EDA plots
    eda_plot_path = os.path.join(plot_location, 'eda_plots')
    if not os.path.exists(eda_plot_path):
        os.mkdir(eda_plot_path)

    # creates and saves plots as .png files in data/plots
    for feat in features.columns:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.hist([
            features[target == 1][feat].values,
            features[target == 2][feat].values,
            features[target == 0][feat].values
        ])
        ax.set_xlabel(' '.join(feat.split('_')).capitalize())
        ax.set_ylabel('Number of observations')
        fig.savefig(eda_plot_path + "/" + feat + "_plot.png")
        logger.info("Plot saved for " + feat)
