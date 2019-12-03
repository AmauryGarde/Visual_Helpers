# import packages
import plotly.offline
import plotly.graph_objs as go
import numpy as np
import math


# Distribution bar creation
def create_dist(df, x_var, color, x_bar=None, interval_perc=0.1):
    """
    Function to create a bar distribution plot behind the scatter plots to acquire more information about the variables.

    :param df: pandas.DataFrame
        DataFrame containing all the x values to be used for plotting.
    :param x_var: string
        Name of the X axis variable to be plotted.
    :param x_bar: np.array(Default= None, has a value of there is a secondary y value to plot)
        Array containing the limits of all the intervals for the distribution bars and for the averages to be used for the scatter plot.
    :param color: dictionary
        Dictionary with the rgba value of the color to use for scatter.
    :param interval_perc: float (Default= 0.01)
        Size of the interval in percentage to be used for the distribution plots.
    :return trace, x_bar: plotly.graph_objs, np.array
        Plotly bar plot witht the distribution of the variable to be plotted.
        Array containing the limits of all the intervals for the distribution bars and for the averages to be used for the scatter plot.
    """
    if x_bar is None:
        # make interval
        temp = math.ceil(df[x_var].max() / 100)
        interval = interval_perc * temp

        # Create zones
        x_bar = np.arange(0, math.ceil(df[x_var].max() / 100) * 100 + temp, interval)

    # Divide by zones
    count = np.histogram(df[x_var], x_bar)[0]

    y_bar = (count * 100 / len(df)) * 0.01

    trace = go.Bar({
        'x': x_bar,
        'y': y_bar,
        'marker': color,
        'opacity': 0.3,
        'name': 'Dist. ' + str(x_var)
    })

    return trace, x_bar


# create a category column to sort and average
def cat_clients(df, x_var, x_bar):
    """
    Function that creates a columns to categories the values according to the distribution interval they lie in.

    :param df: pandas.DataFrame
        DataFrame containing all the x values to be used for plotting.
    :param x_var: string
        Name of the X axis variable to be plotted.
    :param x_bar: np.array
        Array containing the limits of all the intervals for the distribution bars and for the averages to be used for the scatter plot.
    :return df: pandas.DataFrame
        Returns the DataFrame with a 'cat' column to separate the variable values according to their respective intervals for the distribution bars.
    """
    criteria = []
    for i in range(len(x_bar) - 1):
        criteria.append(df[x_var].between(x_bar[i], x_bar[i + 1]))
    values = np.arange(0, len(x_bar) - 1)

    df['cat'] = np.select(criteria, values, 0)

    return df


# Set x and y of scatter to the average per interval
def avg_cats(df, x_var, y_var):
    df = df.sort_values(by=['pr_total'])

    x = df.groupby(['cat'])[x_var].mean()
    y = df.groupby(['cat'])[y_var].mean()
    return x, y


def create_scatter(x, y, var_name, color, axis_num=1):
    """

    :param x: Series
        Series of the different averages of the variable x to be scattered.
    :param y: Series
        Series of the different averages of the variable y to be scattered.
    :param var_name: string
        Name of the variable to be plotted.
    :param color: dictionary
        Dictionary with the rgba value of the color to use for scatter.
    :param axis_num: integer (Default=1)
        Adds number of the y axis for overlaying purposes if a secondary y variable is desired.
    :return trace: plotly.graph_objs
        Data of the Scatter plot for the x and y axis variables.
    """
    trace = go.Scatter(
        x=x,
        y=y,
        mode="lines+markers",
        marker=color,
        name=str(var_name),
        yaxis='y{}'.format(axis_num))
    return trace


def create_cat_plots(df, categorical_var, x_var, y_var, x_bar, color_used):
    """
    Function to create the scatter and distribution bar plots for the categorical variable if necessary.

    :param df: pandas.DataFrame
        DataFrame with the values of the categorical variable.
    :param categorical_var: string
        Name of the categorical variable desired.
    :param x_var: string
        Name of the X axis variable plotted.
    :param y_var: string
        Name of the Y axis variable plotted.
    :param x_bar: numpy.array
        Array containing the limits of all the intervals for the distribution bars and for the averages to be used for the scatter plot.
    :param color_used: list
        List of the indexes of the colors already used in the graph.
    :return trace_cat, color_used: lis, list
        List of the bar and scatter plot for the categorical variable to be plotted.
        List of the indexes of the colors already used in the graph - updated.
    """
    temp_cat_x = df.groupby([categorical_var, 'cat'])[x_var].mean()
    temp_cat_y = df.groupby([categorical_var, 'cat'])[y_var].mean()

    trace_cats = []
    for v in df[categorical_var].unique():
        temp_x = temp_cat_x[v]
        temp_y = temp_cat_y[v]

        count = np.histogram(df[df[categorical_var] == v][x_var], x_bar)[0]
        y_bar = (count * 100 / len(df)) * 0.01
        color, color_used = find_color(color_used)

        trace_cats += [create_scatter(temp_x, temp_y, v, color), go.Bar({
            'x': x_bar,
            'y': y_bar,
            'marker': color,
            'opacity': 0.3,
            'name': str(v)
        })]

    return trace_cats, color_used


def find_color(color_used):
    """
    Functions to set the colors used for the scatter and bar plots.
    :param color_used: list
        List of the indexes of the color schemes already used
    :return color, color_used: dict, list
        Dictionary of the rgba of the color to set to the plot at hand.
        List of the indexes of colors already used - updated with new color
    """
    AXA_colors = [(0, 0, 143, 0.8),
                  (252, 211, 133, 0.8),
                  (2, 113, 128, 0.8),
                  (225, 150, 170, 0.8),
                  (0, 174, 198, 0.8),
                  (145, 65, 70, 0.8),
                  (52, 60, 61, 0.8),
                  (181, 208, 238, 0.8)]

    temp = np.random.randint(0, 8)

    while temp in color_used:
        temp = np.random.randint(0, 8)

    color = dict(color='rgba' + str(AXA_colors[temp]))

    color_used.append(temp)

    return color, color_used


def create_figure(df, x_var, y_var, x_title, y_title, title, second_y_var=None, categorical_var=None, stack_bar=False):
    """
    Function that creates the final figure, appending all the data and layout together.

    :param df: pandas.DataFrame
        DataFrame with all the required variables and their respective values.
    :param x_var: string
        Name of the variable to map as the X
    :param y_var: string
        Name of the variable to map as the Y
    :param x_title: string
        Title for the X axis
    :param y_title: string
        Title for the Y axis
    :param title: string
        Title of the general graph which will also be used to save the figure
    :param second_y_var: string (Default=None)
        Name of the variable to map as the Y secondary if desired.
    :param categorical_var: string (Default=None)
        Name of the categorical variable that can also be mapped for comparison
    :param stack_bar: bool (Default=False)
        Sets distribution histograms as stacks
    :return: plotly.offline.plot
        Returns the plot as an html file in outputs and opens in the default browser
    """

    # memory of color used
    color_used = []

    # prepare color
    color, color_used = find_color(color_used)

    # prepare scatter and dist plots
    trace_bar, x_bar = create_dist(df, x_var, color)

    df = cat_clients(df, x_var, x_bar)
    x, y = avg_cats(df, x_var, y_var)

    trace_scatter = create_scatter(x, y, x_var, color)

    # set stack
    if stack_bar is True:
        bm = 'stack'
    else:
        bm = None

    # add all plots to data
    data = [trace_bar, trace_scatter]
    layout = dict(title=title,
                  xaxis=dict(title=x_title, showline=True),
                  yaxis=dict(title=y_title),
                  barmode=bm
                  )

    # create second y variable scatter if necessary
    if second_y_var is not None:
        x2, y2 = avg_cats(df, x_var, second_y_var)
        color2, color_used = find_color(color_used)
        trace_scatter2 = create_scatter(x2, y2, second_y_var, color2, 2)
        trace_bar2, x_bar = create_dist(df, second_y_var, color2, x_bar)
        data += [trace_scatter2, trace_bar2]
        layout['yaxis2'] = dict(title=second_y_var,
                                overlaying='y1',
                                side='right')

    # add categorical plots if not none
    if categorical_var is not None:
        trace_cats, color_used = create_cat_plots(df, categorical_var, x_var, y_var, x_bar, color_used)
        data += trace_cats

    return plotly.offline.plot({"data": data, "layout": layout},
                               filename=r"C:\Users\a-garde\PycharmProjects\Plotly-Graph\output_file\{}.html".format(
                                   title))
