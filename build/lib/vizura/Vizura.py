import warnings
warnings.filterwarnings("ignore")
import seaborn as sns
import re
import dash_core_components as dcc
import dash_html_components as html
from collections import Counter
import matplotlib.pyplot as plt
from scipy.stats import shapiro, kstest, anderson
import plotly.graph_objects as go
import scipy.stats as stats
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, Dash
import pandas as pd
import numpy as np
import plotly.express as px


def numerical(data):

    df = data.select_dtypes(include=['number'])

    # Dataset statistics
    overall_stats = {
        'Number of variables:': len(df.columns),
        'Number of observations:': len(df),
        'Total Missing Values:': df.isna().sum().sum(),
        'Total cell size:': df.size,
        'Percentage of missing values:': (df.isna().sum().sum()/df.size)*100,
        'Number of Duplicated rows:': df.duplicated().sum(),
        'Data Type Counts:': df.dtypes.value_counts(),
    }

    # Initialize the Dash app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # App layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Overall Dataset Statistics"),
                html.Div([
                    html.P([html.Span("Number of variables: ", style={'font-weight': 'normal'}), html.Span(f"{overall_stats['Number of variables:']}", style={'font-weight': 'bold'})]),
                    html.P([html.Span("Number of observations: ", style={'font-weight': 'normal'}), html.Span(f"{overall_stats['Number of observations:']}", style={'font-weight': 'bold'})]),
                    html.P([html.Span("Total Missing Values: ", style={'font-weight': 'normal'}), html.Span(f"{overall_stats['Total Missing Values:']}", style={'font-weight': 'bold'})]),
                    html.P([html.Span("Total cell size: ", style={'font-weight': 'normal'}), html.Span(f"{overall_stats['Total cell size:']}", style={'font-weight': 'bold'})]),
                    html.P([html.Span("Percentage of missing values: ", style={'font-weight': 'normal'}), html.Span(f"{overall_stats['Percentage of missing values:']:.2f}%", style={'font-weight': 'bold'})]),
                    html.P([html.Span("Number of Duplicated rows: ", style={'font-weight': 'normal'}), html.Span(f"{overall_stats['Number of Duplicated rows:']}", style={'font-weight': 'bold'})]),
                    html.P([html.Span("Data Type Counts: ", style={'font-weight': 'normal'}), html.Span(f"{overall_stats['Data Type Counts:']}", style={'font-weight': 'bold'})])
                ], className="mb-4"),

                dcc.Dropdown(
                    id='variable-dropdown',
                    options=[{'label': col, 'value': col} for col in df.columns],
                    value=df.columns[0],
                    clearable=False,
                    className="mb-4"
                )
            ], width=4),

            dbc.Col([
                html.Div(id='statistics-output', className="mb-4", style={'font-size': 'small'})
            ], width=8)
        ], style={'overflowY': 'scroll', 'maxHeight': '80vh'}),
        dbc.Row([
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(label='Violin Box Plot', tab_id='boxplot'),
                    dbc.Tab(label='Histogram', tab_id='histogram'),
                    dbc.Tab(label='QQ Plot', tab_id='QQplot'),
                    dbc.Tab(label='Tests', tab_id='tests'),
                ], id='tabs', active_tab='boxplot'),

                html.Div(id='tab-content')
            ], width=12)
        ])
    ], fluid=True, style={'overflowY': 'scroll', 'maxHeight': '100vh'})

    # Callback to update statistics and plots based on selected variable and tab
    @app.callback(
        [Output('statistics-output', 'children'),
         Output('tab-content', 'children')],
        [Input('variable-dropdown', 'value'),
         Input('tabs', 'active_tab')]
    )
    def update_output(selected_variable, active_tab):
        # Calculate statistics
        distinct_count = df[selected_variable].nunique()
        distinct_percent = distinct_count/len(df[selected_variable]) * 100
        missing_count = df[selected_variable].isna().sum()
        missing_percentage = (df[selected_variable].isna().sum()/len(df[selected_variable])) * 100
        zero_count = int((df[selected_variable] == 0).sum())
        zero_percent = (zero_count/len(df[selected_variable])) * 100
        neg_values = (df[selected_variable].values < 0).sum()
        neg_percent = (neg_values/len(df[selected_variable])) * 100
        min_value = df[selected_variable].min()
        percentiles = np.percentile(df[selected_variable], [5, 25, 50, 75, 95])
        percen_5, Q1, median, Q3, percen_95 = percentiles
        max_value = df[selected_variable].max()
        ranges = max_value - min_value
        IQR = Q3 - Q1
        variance = float(np.var(df[selected_variable], ddof=0))
        std = float(np.std(df[selected_variable], ddof=0))
        mean = float(np.mean(df[selected_variable]))
        z_scores = [(x - mean) / std for x in df[selected_variable]]
        outliers_z = len([x for x, z in zip(df[selected_variable], z_scores) if abs(z) > 3])
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers_I = len([x for x in df[selected_variable] if x < lower_bound or x > upper_bound])
        coeff_var = (std / mean) * 100
        kurt = stats.kurtosis(df[selected_variable])
        abs_dev = np.abs(df[selected_variable] - median)
        med_ad = abs_dev.median()
        skewness = stats.skew(df[selected_variable])
        sums = df[selected_variable].sum()

        # Normality Tests
        shapiro_stat, shapiro_p = shapiro(df[selected_variable])
        shapiro_result = "normally distributed" if shapiro_p > 0.05 else "not normally distributed"

        ks_stat, ks_p = kstest(df[selected_variable], 'norm')
        ks_result = "normally distributed" if ks_p > 0.05 else "not normally distributed"

        anderson_result = anderson(df[selected_variable], dist='norm')
        anderson_stat = anderson_result.statistic
        anderson_crit = anderson_result.critical_values
        anderson_result_text = "normally distributed" if anderson_stat < anderson_crit[2] else "not normally distributed"

        # Split statistics into two halves
        stats_list = [
            ("Distinct Count: ", f"{distinct_count:.2f}"),
            ("Distinct %: ", f"{distinct_percent:.2f}%"),
            ("Missing Count: ", f"{missing_count:.2f}"),
            ("Missing %: ", f"{missing_percentage:.2f}%"),
            ("Zero Count: ", f"{zero_count:.2f}"),
            ("Zero %: ", f"{zero_percent:.2f}%"),
            ("Negative Values: ", f"{neg_values:.2f}"),
            ("Negative %: ", f"{neg_percent:.2f}%"),
            ("Minimum Value: ", f"{min_value:.2f}"),
            ("5th Percentile: ", f"{percen_5:.2f}"),
            ("Q1: ", f"{Q1:.2f}"),
            ("Median: ", f"{median:.2f}"),
            ("Q3: ", f"{Q3:.2f}"),
            ("95th Percentile: ", f"{percen_95:.2f}"),
            ("Maximum Value: ", f"{max_value:.2f}"),
            ("Range: ", f"{ranges:.2f}"),
            ("IQR: ", f"{IQR:.2f}"),
            ("Variance: ", f"{variance:.2f}"),
            ("Standard Deviation: ", f"{std:.2f}"),
            ("Mean: ", f"{mean:.2f}"),
            ("Outliers (Z-Score) Count: ", f"{outliers_z}"),
            ("Outliers (IQR) Count: ", f"{outliers_I}"),
            ("Lower Bound: ", f"{lower_bound:.2f}"),
            ("Upper Bound: ", f"{upper_bound:.2f}"),
            ("Coefficient of Variation: ", f"{coeff_var:.2f}%"),
            ("Kurtosis: ", f"{kurt:.2f}"),
            ("Median Absolute Deviation: ", f"{med_ad:.2f}"),
            ("Skewness: ", f"{skewness:.2f}"),
            ("Sum: ", f"{sums:.2f}")
        ]

        half_index = len(stats_list) // 2
        first_half_stats = stats_list[:half_index]
        second_half_stats = stats_list[half_index:]

        stat = dbc.Row([
            dbc.Col([
                html.Div([
                    html.P([html.Span(name, style={'font-weight': 'normal'}), html.Span(value, style={'font-weight': 'bold'})])
                    for name, value in first_half_stats
                ])
            ], width=6),
            dbc.Col([
                html.Div([
                    html.P([html.Span(name, style={'font-weight': 'normal'}), html.Span(value, style={'font-weight': 'bold'})])
                    for name, value in second_half_stats
                ])
            ], width=6)
        ])

        # Generate the selected plot
        if active_tab == 'boxplot':
            fig = go.Figure()
            fig.add_trace(go.Violin(x=df[selected_variable], marker_color='indianred', box_visible=False, name=selected_variable, meanline_visible=True, points='all'))
            fig.add_trace(go.Box(x=df[selected_variable], marker_color='lightseagreen', boxpoints='suspectedoutliers', boxmean='sd', name=selected_variable))
        elif active_tab == 'histogram':
            fig = px.histogram(df[selected_variable], x=df[selected_variable], labels={'x': selected_variable}, histnorm='probability density')
        elif active_tab == 'QQplot':
            (qosm, qoth), (slope, intercept, r) = stats.probplot(df[selected_variable], dist="norm")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=qosm, y=qoth, mode='markers', name='Sample Quantiles'))
            fig.add_trace(go.Scatter(x=qosm, y=slope*qosm + intercept, mode='lines', name='Theoretical Quantiles'))
            fig.update_layout(title='Q-Q Plot', xaxis_title='Theoretical Quantiles', yaxis_title='Sample Quantiles', showlegend=True)
        elif active_tab == 'tests':
            fig = go.Figure()
            fig.add_trace(go.Table(
                header=dict(values=['Test', 'Statistic', 'p-value & critical Value', 'Result']),
                cells=dict(values=[
                    ['Shapiro-Wilk', 'Kolmogorov-Smirnov', 'Anderson-Darling'],
                    [f"{shapiro_stat:.4f}", f"{ks_stat:.4f}", f"{anderson_stat:.4f}"],
                    [f"{shapiro_p:.4f}", f"{ks_p:.4f}", f"{', '.join(map(str, anderson_crit))}"],
                    [shapiro_result, ks_result, anderson_result_text]
                ])
            ))
            fig.update_layout(title='Normality Tests')

        return stat, dcc.Graph(figure=fig)

    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True,port=1235)


def categorical(data):
    df = data.select_dtypes(include=['object','category'])

    # Initialize the Dash app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Dropdown options for categorical variables
    dropdown_options = [{'label': col, 'value': col} for col in df.select_dtypes(include=['object']).columns]

    # Define the app layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='variable-dropdown',
                    options=dropdown_options,
                    value=df.select_dtypes(include=['object']).columns[0],
                    clearable=False,
                    className="mb-4"
                )
            ], width=12)
        ]),

        dbc.Row([
            dbc.Col([
                html.H2("Text Variable Stats"),
                html.Div(id='analysis-output', className="mb-4")
            ], width=4),

            dbc.Col([
                html.H2("Top 10 Words and Special Characters"),
                html.Div(id='tables-output')
            ], width=4),

            dbc.Col([
                html.H2("Class Imbalance"),
                html.Div(id='imbalance-output')
            ], width=4)
        ], style={'overflowY': 'scroll', 'maxHeight': '80vh'})
    ], fluid=True, style={'overflowY': 'scroll', 'maxHeight': '100vh'})

    # Callback to update analysis, tables, and imbalance check based on selected variable
    @app.callback(
        [Output('analysis-output', 'children'),
         Output('tables-output', 'children'),
         Output('imbalance-output', 'children')],
        [Input('variable-dropdown', 'value')]
    )
    def update_output(selected_variable):
        data = df[selected_variable]

        # Calculate analysis statistics
        distinct_count_c = data.nunique()
        counteruc = Counter(data)
        unique_values_c = [item for item, count in counteruc.items() if count == 1]
        unique_count_c = len(unique_values_c)
        unique_percent_c = (len(unique_values_c) / len(data)) * 100
        missing_count_c = int(data.isna().sum())
        missing_percentage_c = (missing_count_c / len(data)) * 100

        len_mean = float(data.str.len().mean())
        len_sd = float(data.str.len().std())
        len_median = int(data.str.len().median())
        len_min = int(data.str.len().min())
        len_max = int(data.str.len().max())
        sample_one = data.sample(frac=0.5, random_state=42, replace=True)

        def percentile_value(sample_one, percentile):
            index = int((len(sample_one) - 1) * percentile)
            return sample_one.iloc[index]

        percentile_1st = sample_one.iloc[0]
        percentile_25th = percentile_value(sample_one, 0.25)
        percentile_50th = percentile_value(sample_one, 0.5)
        percentile_75th = percentile_value(sample_one, 0.75)
        percentile_last = sample_one.iloc[-1]

        # Analysis output
        analysis = html.Div([
            html.P([html.Span("Distinct Count: ", style={'font-weight': 'normal'}), html.Span(f"{distinct_count_c}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Unique Count: ", style={'font-weight': 'normal'}), html.Span(f"{unique_count_c}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Unique %: ", style={'font-weight': 'normal'}), html.Span(f"{unique_percent_c:.2f}%", style={'font-weight': 'bold'})]),
            html.P([html.Span("Missing Count: ", style={'font-weight': 'normal'}), html.Span(f"{missing_count_c}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Missing %: ", style={'font-weight': 'normal'}), html.Span(f"{missing_percentage_c:.2f}%", style={'font-weight': 'bold'})]),
            html.P([html.Span("Mean Length: ", style={'font-weight': 'normal'}), html.Span(f"{len_mean:.2f}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Standard Deviation: ", style={'font-weight': 'normal'}), html.Span(f"{len_sd:.2f}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Median Length: ", style={'font-weight': 'normal'}), html.Span(f"{len_median}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Min Length: ", style={'font-weight': 'normal'}), html.Span(f"{len_min}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Max Length: ", style={'font-weight': 'normal'}), html.Span(f"{len_max}", style={'font-weight': 'bold'})]),
            html.P([html.Span("1st Percentile: ", style={'font-weight': 'normal'}), html.Span(f"{percentile_1st}", style={'font-weight': 'bold'})]),
            html.P([html.Span("25th Percentile: ", style={'font-weight': 'normal'}), html.Span(f"{percentile_25th}", style={'font-weight': 'bold'})]),
            html.P([html.Span("50th Percentile: ", style={'font-weight': 'normal'}), html.Span(f"{percentile_50th}", style={'font-weight': 'bold'})]),
            html.P([html.Span("75th Percentile: ", style={'font-weight': 'normal'}), html.Span(f"{percentile_75th}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Last Percentile: ", style={'font-weight': 'normal'}), html.Span(f"{percentile_last}", style={'font-weight': 'bold'})]),
        ], className="mb-4")

        # Top 10 Words and Special Characters
        top_10_df = pd.DataFrame(Counter(re.findall(r'\b\w+\b', ' '.join(data).lower())).most_common(10), columns=['Word', 'Frequency'])
        special_char_df = pd.DataFrame(Counter(re.findall(r'[^\w\s]', ' '.join(data))).items(), columns=['Special Character', 'Frequency'])

        tables = html.Div([
            html.H4("Top 10 Most Frequent Words"),dbc.Table.from_dataframe(top_10_df, striped=True, bordered=True, hover=True),
            html.H4("Special Characters Frequency"),dbc.Table.from_dataframe(special_char_df, striped=True, bordered=True, hover=True) ], className="mb-4")

        # Class Imbalance Check
        class_counts = df[selected_variable].value_counts()
        majority_class_count = class_counts.max()
        minority_class_count = class_counts.min()
        imbalance_ratio = majority_class_count / minority_class_count
        threshold = 2  # You can adjust this threshold as needed
        is_imbalanced = imbalance_ratio > threshold

        imbalance_check = html.Div([
            html.P([html.Span("Class Counts: ", style={'font-weight': 'normal'}), html.Span(f"{class_counts.to_dict()}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Imbalance Ratio: ", style={'font-weight': 'normal'}), html.Span(f"{imbalance_ratio:.2f}", style={'font-weight': 'bold'})]),
            html.P([html.Span("Is the Data Imbalanced?: ", style={'font-weight': 'normal'}), html.Span(f"{'Yes' if is_imbalanced else 'No'}", style={'font-weight': 'bold'})]),
        ], className="mb-4")

        return analysis, tables, imbalance_check

    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True,port=1234)


def calculate_correlations(df):
    df = df.select_dtypes(include=[np.number])
    corr_methods = ['pearson', 'spearman', 'kendall']
    stats = ['Highest Positive Correlation', 'Highest Negative Correlation', 'Lowest Correlation', 'Mean Correlation']
    results = {method: {stat: None for stat in stats} for method in corr_methods}

    for method in corr_methods:
        corr_matrix = df.corr(method=method)
        np.fill_diagonal(corr_matrix.values, np.nan)  # Ignore self-correlation
        correlations = corr_matrix.unstack().dropna()

        results[method]['Highest Positive Correlation'] = correlations.max()
        results[method]['Highest Negative Correlation'] = correlations.min()
        results[method]['Lowest Correlation'] = correlations.abs().min()
        results[method]['Mean Correlation'] = correlations.mean()

    return pd.DataFrame(results)


def plot_correlation(df):
    df = df.select_dtypes(include=[np.number])
    corr_methods = ['pearson', 'spearman', 'kendall']

    for method in corr_methods:
        corr_matrix = df.corr(method=method)
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
        plt.title(f'{method.capitalize()} Correlation Matrix')
        plt.show()