import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from scipy import stats
import plotly.express as px
from scipy.stats import shapiro, kstest, anderson, pearsonr, kendalltau, spearmanr
from collections import Counter
import re
import streamlit as st
import pandas as pd
from sklearn.datasets import load_iris



def main():

    # Add logo

    st.logo("logo.png", size="large")

    # Sidebar option for uploading data
    st.sidebar.subheader("Upload Your Dataset")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx", "txt"])

    # Load dataset
    if uploaded_file is not None:
        # Try reading the file with common encodings
        try:
            if uploaded_file.name.endswith(".csv"):
                data = pd.read_csv(uploaded_file, encoding='utf-8')  # Default encoding
            elif uploaded_file.name.endswith(".xlsx"):
                data = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".txt"):
                data = pd.read_csv(uploaded_file, delimiter="\t", encoding='utf-8')
            st.sidebar.success("File uploaded successfully!")
        except UnicodeDecodeError:
            # Handle UnicodeDecodeError and try other encodings
            try:
                data = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
                st.sidebar.warning("File read with ISO-8859-1 encoding due to decoding error.")
            except Exception as e:
                st.sidebar.error(f"Error reading file: {e}")
    else:
        # Default dataset if no file is uploaded
        # Load Iris dataset as a preview
        st.sidebar.info("Using the Iris dataset as preview. Upload your own dataset to analyze.")
        iris = load_iris()
        data = pd.DataFrame(iris.data, columns=iris.feature_names)
        data['species'] = pd.Categorical.from_codes(iris.target, iris.target_names)

    # Display dataset preview

    st.subheader("Sample Dataset ")
    st.write(data.head())


    # Sidebar radio buttons to switch between Numerical and Categorical
    analysis_type = st.sidebar.radio("Choose Analysis Type", ["Numerical", "Categorical", "Glossary"])

    if analysis_type == "Numerical":
        # Select numerical columns
        df = data.select_dtypes(include=["number"])
        dty = data.dtypes.value_counts().reset_index().rename(columns={"index": "Type"})
        data_type_counts = ", ".join([f"{row['Type']}: {row['count']}" for _, row in dty.iterrows()])

        st.header("Numerical Analysis")
        st.subheader("Overall Statistics")

        # Overall Dataset Statistics
        overall_stats = {
            "Number of Variables": len(data.columns),
            "Number of Observations": len(data),
            "Total Missing Values": data.isna().sum().sum(),
            "Total Cell Size": data.size,
            "Missing Values %": str((data.isna().sum().sum() / data.size) * 100) + " %",
            "Number of Duplicated Rows": data.duplicated().sum(),
            "Data Type Counts":data_type_counts,
        }

        # Create two columns for display
        col1, col2 = st.columns(2)

        # Loop over the statistics and display in the two columns
        for idx, (stat, value) in enumerate(overall_stats.items()):
            if idx % 2 == 0:
                col1.markdown(f"**{stat}:** <span style='color:green; font-size:20px; font-weight:regular;'>{value}</span>",
                              unsafe_allow_html=True)
            else:
                col2.markdown(f"**{stat}:** <span style='color:green; font-size:20px; font-weight:regular;'>{value}</span>",
                              unsafe_allow_html=True)

        # Dropdown to select variable
        selected_variable = st.selectbox("Select a variable for detailed analysis", df.columns)

        # Check if data for the selected variable already exists in session_state
        if selected_variable:
            col_data = df[selected_variable]
            st.subheader(f"Analysis for {selected_variable}")

            # Check if data is already in session_state
            if selected_variable not in st.session_state:
                st.session_state[selected_variable] = {}

            if 'descriptive_stats' not in st.session_state[selected_variable]:
                with st.spinner("Calculating descriptive statistics..."):
                    descriptive_stats = {
                        "Distinct Count": f"{col_data.nunique():.2f}",
                        "Distinct %": f"{(col_data.nunique() / len(col_data)) * 100:.2f} %",
                        "Missing Count": col_data.isna().sum(),
                        "Missing %": str(col_data.isna().mean() * 100) + " %",
                        "Zero Count": (col_data == 0).sum(),
                        "Zero %": f"{((col_data == 0).sum() / len(col_data)) * 100:.2f} %",
                        "Negative Count": (col_data < 0).sum(),
                        "Negative %": f"{((col_data < 0).sum() / len(col_data)) * 100:.2f} %",
                        "Mean": f"{col_data.mean():.2f}",
                        "Minimum Value": f"{col_data.min():.2f}",
                        "5th Percentile": f"{col_data.quantile(0.05):.2f}",
                        "25th Percentile": f"{col_data.quantile(0.25):.2f}",
                        "50th Percentile (Median)": f"{col_data.median():.2f}",
                        "75th Percentile": f"{col_data.quantile(0.75):.2f}",
                        "95th Percentile": f"{col_data.quantile(0.95):.2f}",
                        "Maximum Value": f"{col_data.max():.2f}",
                        "Range": f"{(col_data.max() - col_data.min()):.2f}",
                        "Interquartile Range (IQR)": f"{(col_data.quantile(0.75) - col_data.quantile(0.25)):.2f}",
                        "Mode": col_data.mode().iloc[0] if not col_data.mode().empty else "N/A",
                        "Variance": f"{col_data.var():.2f}",
                        "Standard Deviation": f"{col_data.std():.2f}",
                        "Skewness": f"{col_data.skew():.2f}",
                        "Kurtosis": f"{col_data.kurtosis():.2f}",
                        "Outliers (Z-Score)": len(
                            [x for x, z in zip(col_data, [(x - col_data.mean()) / col_data.std() for x in col_data]) if
                             abs(z) > 3]),
                        "Outliers (IQR)": len([x for x in df[selected_variable] if x < col_data.quantile(0.25) - 1.5 * (
                                col_data.quantile(0.75) - col_data.quantile(0.25)) or x > col_data.quantile(0.75) + 1.5 * (
                                                       col_data.quantile(0.75) - col_data.quantile(0.25))]),
                        "Coefficient of Variation": f"{(col_data.std() / col_data.mean()) * 100:.2f}",
                        "Median Absolute Deviation": f"{np.median(np.abs(col_data - col_data.median())):.2f}",
                        "Sum of Values": f"{sum(col_data):.2f}",
                    }
                    st.session_state[selected_variable]['descriptive_stats'] = descriptive_stats

            # Display descriptive statistics in three columns
            st.markdown("### Descriptive Statistics")
            stats_list = list(st.session_state[selected_variable]['descriptive_stats'].items())
            stats_col1, stats_col2, stats_col3 = stats_list[:len(stats_list) // 3], stats_list[len(stats_list) // 3:2 * len(
                stats_list) // 3], stats_list[2 * len(stats_list) // 3:]

            # Create 3 columns
            col3, col4, col5 = st.columns(3)

            # Display stats in each column
            with col3:
                for stat, value in stats_col1:
                    st.markdown(f"**{stat}:** <span style='color:blue;'>{value}</span>", unsafe_allow_html=True)

            with col4:
                for stat, value in stats_col2:
                    st.markdown(f"**{stat}:** <span style='color:blue;'>{value}</span>", unsafe_allow_html=True)

            with col5:
                for stat, value in stats_col3:
                    st.markdown(f"**{stat}:** <span style='color:blue;'>{value}</span>", unsafe_allow_html=True)

            # Plot options
            st.subheader("Plots")
            plot_type = st.radio("Choose Plot Type", ["Violin Plot", "Histogram", "QQ Plot", "Normality Tests"])
            if plot_type == "Violin Plot":
                fig = go.Figure()
                fig.add_trace(
                    go.Violin(x=col_data, marker_color='indianred', box_visible=False, name=selected_variable,
                              meanline_visible=True, points='all'))
                fig.add_trace(
                    go.Box(x=col_data, marker_color='lightseagreen', boxpoints='suspectedoutliers', boxmean='sd',
                           name=selected_variable))
                st.plotly_chart(fig)


            elif plot_type == "Histogram":
                fig = px.histogram(x=col_data, labels={'x': selected_variable}, histnorm='probability density')
                fig.update_layout(bargap=0.05)
                st.plotly_chart(fig)


            elif plot_type == "QQ Plot":
                (qosm, qoth), (slope, intercept, r) = stats.probplot(col_data.values, dist="norm")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=qosm, y=qoth, mode='markers', name='Sample Quantiles', marker=dict(color='blue')))
                fig.add_trace(go.Scatter(x=qosm,y=slope * qosm + intercept,mode='lines',name='Theoretical Quantiles',line=dict(color='red', width=2)))
                fig.update_layout(title='Q-Q Plot',xaxis_title='Theoretical Quantiles',yaxis_title='Sample Quantiles',
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),height=600)
                st.plotly_chart(fig)

            elif plot_type == "Normality Tests":
                st.subheader("Normality Tests")

                # Perform the tests
                shapiro_stat, shapiro_p = shapiro(col_data)
                ks_stat, ks_p = kstest(col_data, 'norm')
                anderson_result = anderson(col_data, dist='norm')

                # Organize results into a DataFrame
                normality_results = {
                    "Test": ["Shapiro-Wilk Test", "Kolmogorov-Smirnov Test", "Anderson-Darling Test"],
                    "Statistics": [shapiro_stat, ks_stat, anderson_result.statistic],
                    "p-values / Critical Value": [shapiro_p, ks_p, anderson_result.critical_values],
                    "Result": [
                        "Normally Distributed" if shapiro_p > 0.05 else "Not Normally Distributed",
                        "Normally Distributed" if ks_p > 0.05 else "Not Normally Distributed",
                        "Normally Distributed" if anderson_result.statistic < anderson_result.critical_values[2] else "Not Normally Distributed"
                    ]
                }

                # Create DataFrame from the dictionary
                result_df = pd.DataFrame(normality_results)

                # Display the table
                st.table(result_df)

            # Correlation options
            st.subheader("Correlation Analysis")
            corr_method = st.radio("Choose Correlation Method", ["Pearson", "Kendall", "Spearman"])
            st.write("### Descriptions of the Correlation Methods:")

            # Provide descriptions of each method
            if corr_method == "Pearson":
                st.write("""
                **Pearson Correlation**: This measures the linear relationship between two continuous variables. It ranges from -1 to +1, where:
                - 1 means a perfect positive correlation
                - -1 means a perfect negative correlation
                - 0 means no linear correlation
                """)
            elif corr_method == "Kendall":
                st.write("""
                **Kendall Tau Correlation**: This measures the ordinal association between two variables. It evaluates the strength and direction of association, but unlike Pearson, it doesn't require the relationship to be linear.
                - The value ranges from -1 (strong negative association) to +1 (strong positive association).
                """)
            elif corr_method == "Spearman":
                st.write("""
                **Spearman's Rank Correlation**: This measures the monotonic relationship between two variables. It’s a non-parametric test, meaning it doesn’t assume a specific distribution of the data, and can detect both linear and non-linear associations.
                - The value ranges from -1 (strong negative correlation) to +1 (strong positive correlation).
                """)

            # Select columns for correlation calculation
            selected_columns = st.multiselect("Select two variables for correlation analysis", df.columns)

            corr_df = df[selected_columns]
            if not selected_columns:
                st.warning("Please select at least two columns to correlate with.")

            else:
                if corr_method == "Pearson":
                    corr_matrix = corr_df.corr(method="pearson")
                    plt.figure(figsize=(10, 8))
                    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
                    plt.title(f'{corr_method.capitalize()} Correlation Matrix')
                    st.pyplot(plt.gcf())

                elif corr_method == "Kendall":
                    corr_matrix = corr_df.corr(method=corr_method.lower())
                    plt.figure(figsize=(10, 8))
                    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
                    plt.title(f'{corr_method.capitalize()} Correlation Matrix')
                    st.pyplot(plt.gcf())

                elif corr_method == "Spearman":
                    corr_matrix = corr_df.corr(method=corr_method.lower())
                    plt.figure(figsize=(10, 8))
                    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)
                    plt.title(f'{corr_method.capitalize()} Correlation Matrix')
                    st.pyplot(plt.gcf())

    elif analysis_type == "Categorical":
        # Select categorical columns
        df = data.select_dtypes(include=["object", "category"])

        st.header("Categorical Analysis")

        # Dropdown to select variable
        selected_variable = st.selectbox("Select a variable for detailed analysis", df.columns)
        col_data = df[selected_variable]

        st.subheader(f"Analysis for {selected_variable}")

        # Descriptive statistics
        categorical_stats1 = {
            "Distinct Count": col_data.nunique(),
            "Missing Count": col_data.isna().sum(),
            "% Missing": str(col_data.isna().mean() * 100) + " %",
            "Unique Values Count": [item for item, count in Counter(col_data).items() if count == 1],
            "Unique Values Count %": str((len([item for item, count in Counter(col_data).items() if count == 1]) / len(
                col_data)) * 100) + " %",
            "Top (Most Frequent)": col_data.mode().iloc[0] if not col_data.mode().empty else "N/A",
            "Mean Length": round(float(col_data.str.len().mean()),2),
            "Length Std": round(float(col_data.str.len().std()),2),
            "Length Median": round(int(col_data.str.len().median()),2),
        }
        categorical_stats2 = {
            "Length Minimum": int(col_data.str.len().min()),
            "Length Maximum": int(col_data.str.len().max()),
            "Frequency of Top": col_data.value_counts().iloc[0] if not col_data.value_counts().empty else "N/A",
            "max_class": col_data.value_counts().idxmax(),
            "min_class": col_data.value_counts().idxmin(),
            "Majority Class": f"{col_data.value_counts().idxmax()} ({col_data.value_counts().max()} occurrences)",
            "Minority Class": f"{col_data.value_counts().idxmin()} ({col_data.value_counts().min()} occurrences)",
            "Imbalance Ratio (Max/Min)": round(col_data.value_counts().max() / col_data.value_counts().min() if col_data.nunique() > 1 else np.nan,2),
        }

        col6, col7 = st.columns(2)
        with col6:
            for stat, value in categorical_stats1.items():
                st.markdown(
                    f"**{stat}:** <span style='color:blue; font-size:20px; font-weight:regular;'>{value}</span>",
                    unsafe_allow_html=True)

        with col7:
            for stat, value in categorical_stats2.items():
                st.markdown(
                    f"**{stat}:** <span style='color:blue; font-size:20px; font-weight:regular;'>{value}</span>",
                    unsafe_allow_html=True)

        # Frequency analysis
        st.subheader("Frequency Analysis")
        freq_table = col_data.value_counts().reset_index().rename(
            columns={"index": "Category", selected_variable: "Count"})
        st.table(freq_table)

        st.subheader("Special Characters")
        special_chars = re.findall(r'[^\w\s]', ' '.join(col_data.dropna().astype(str)))
        char_counts = Counter(special_chars).most_common(10)
        st.table(pd.DataFrame(char_counts, columns=["Character", "Frequency"]))

    elif analysis_type == "Glossary":

        # Add glossary for terms
        st.header("Glossary of Terms")

        # Number of Variables
        st.subheader("Number of Variables")
        st.write("Explanation: This refers to the total number of columns in your dataset.")
        st.write(
            "Interpretation: The number of variables provides insight into the breadth of data being analyzed. More variables typically indicate more dimensions of data to explore.")

        # Number of Observations
        st.subheader("Number of Observations")
        st.write(
            "Explanation: This is the total number of rows in the dataset, where each row represents a unique data point.")
        st.write(
            "Interpretation: The number of observations indicates the size of your dataset. A larger number of observations can help ensure statistical reliability, but more data can also increase the time needed for analysis.")

        # Total Missing Values
        st.subheader("Total Missing Values")
        st.write("Explanation: The total number of missing (NaN) values in the dataset.")
        st.write(
            "Interpretation: High numbers of missing values may indicate problems with data collection or measurement. Too many missing values can distort analysis, so it's important to address them (e.g., through imputation or removal).")

        # Total Cell Size
        st.subheader("Total Cell Size")
        st.write(
            "Explanation: The total number of cells in the dataset, calculated as 'number of rows * number of columns'.")
        st.write(
            "Interpretation: This provides an understanding of the overall size of the dataset, helping you gauge the computational resources needed for analysis.")

        # Percentage of Missing Values
        st.subheader("Percentage of Missing Values")
        st.write("Explanation: The percentage of missing values relative to the total number of cells in the dataset.")
        st.write(
            "Interpretation: A high percentage of missing values suggests a need to address data quality issues. Generally, more than 5% missing data may require intervention like imputation or removal.")

        # Number of Duplicated Rows
        st.subheader("Number of Duplicated Rows")
        st.write("Explanation: The number of rows that are identical to other rows in the dataset.")
        st.write(
            "Interpretation: Duplicates can distort analysis by inflating results. It's important to check for duplicates and remove them if they are not meaningful.")

        # Mean
        st.subheader("Mean")
        st.write("Explanation: The average value of a column. It’s the sum of all values divided by the number of values.")
        st.write(
            "Interpretation: The mean gives you a central tendency, showing where most of the data is centered. However, the mean can be skewed by outliers, so it's not always a reliable measure of central tendency in the presence of extreme values.")

        # Minimum Value
        st.subheader("Minimum Value")
        st.write("Explanation: The smallest value in a column.")
        st.write(
            "Interpretation: The minimum gives insight into the lower end of your data. It's useful for identifying the range and seeing if there are unusually low values (outliers).")

        # Maximum Value
        st.subheader("Maximum Value")
        st.write("Explanation: The largest value in a column.")
        st.write(
            "Interpretation: The maximum indicates the upper bound of your data. Similar to the minimum, it can help identify if there are unusually high values (outliers).")

        # Standard Deviation
        st.subheader("Standard Deviation")
        st.write(
            "Explanation: A measure of how spread out the values are from the mean. It’s the square root of the variance.")
        st.write(
            "Interpretation: A high standard deviation means that the values in the column are more spread out, while a low standard deviation means they are closer to the mean.")

        # Skewness
        st.subheader("Skewness")
        st.write(
            "Explanation: A measure of the asymmetry of the data distribution. Positive skew means the right tail is longer, and negative skew means the left tail is longer.")
        st.write(
            "Interpretation: If skewness is near 0, the data is symmetrical. Positive skewness suggests that the data has a longer right tail, while negative skewness suggests a longer left tail. Extreme skewness can indicate that a transformation is needed.")

        # Kurtosis
        st.subheader("Kurtosis")
        st.write(
            "Explanation: A measure of the 'tailedness' of the data distribution. High kurtosis means that the data has heavy tails or more outliers, and low kurtosis means it has lighter tails.")
        st.write(
            "Interpretation: High kurtosis suggests that extreme values are more frequent than in a normal distribution. Low kurtosis suggests fewer extreme values.")

        # Mode
        st.subheader("Mode")
        st.write("Explanation: The most frequently occurring value in a column.")
        st.write(
            "Interpretation: The mode can help identify the most common value in the dataset. In some cases, the data might not have a mode (if no value repeats) or have multiple modes (bimodal or multimodal distributions).")

        # Variance
        st.subheader("Variance")
        st.write(
            "Explanation: A measure of the dispersion of the data, calculated as the average of the squared differences from the mean.")
        st.write(
            "Interpretation: Variance quantifies the spread of the data. A higher variance means the data points are more spread out from the mean, and a lower variance means they are closer.")

        # Interquartile Range (IQR)
        st.subheader("Interquartile Range (IQR)")
        st.write(
            "Explanation: The range between the 25th percentile (Q1) and the 75th percentile (Q3), representing the middle 50% of the data.")
        st.write(
            "Interpretation: The IQR is useful for identifying the range of typical values in your dataset. A large IQR suggests that the data is more spread out, while a small IQR suggests that it is more concentrated around the median.")

        # Outliers (Z-Score)
        st.subheader("Outliers (Z-Score)")
        st.write(
            "Explanation: Outliers are data points that lie far from the mean, typically more than 3 standard deviations away. The Z-score indicates how many standard deviations a value is from the mean.")
        st.write(
            "Interpretation: A Z-score greater than 3 or less than -3 indicates that the data point is an outlier. Outliers should be carefully examined to determine if they are errors or meaningful extreme values.")

        # Outliers (IQR)
        st.subheader("Outliers (IQR)")
        st.write(
            "Explanation: Outliers based on the Interquartile Range (IQR) method. A data point is considered an outlier if it lies below Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR.")
        st.write(
            "Interpretation: IQR-based outlier detection is more robust than the Z-score method, as it is less sensitive to extreme values. Outliers based on IQR are values that fall outside the typical range of the data.")

        # Coefficient of Variation
        st.subheader("Coefficient of Variation")
        st.write(
            "Explanation: A measure of relative variability, calculated as the ratio of the standard deviation to the mean, expressed as a percentage.")
        st.write(
            "Interpretation: The coefficient of variation is useful for comparing variability between datasets with different units or scales. A higher coefficient of variation means greater variability relative to the mean.")

        # Median Absolute Deviation
        st.subheader("Median Absolute Deviation")
        st.write(
            "Explanation: The median of the absolute deviations from the median. It’s a robust measure of the spread of the data.")
        st.write(
            "Interpretation: The median absolute deviation is less sensitive to outliers than the standard deviation and is useful for datasets with extreme values. A higher value indicates more dispersion in the data.")

        # Now add the tests section with similar format
        st.header("Glossary for Tests")

        # Shapiro-Wilk Test
        st.subheader("Shapiro-Wilk Test")
        st.write("Explanation: The Shapiro-Wilk test is used to check if a dataset follows a normal distribution.")
        st.write(
            "Interpretation: If the p-value is less than 0.05, the null hypothesis is rejected, suggesting the data is not normally distributed. If p-value > 0.05, the null hypothesis is not rejected, suggesting the data may follow a normal distribution.")

        # Kolmogorov-Smirnov Test
        st.subheader("Kolmogorov-Smirnov Test (KS Test)")
        st.write(
            "Explanation: The Kolmogorov-Smirnov test compares the distribution of a sample with a reference distribution (e.g., normal, uniform).")
        st.write(
            "Interpretation: If the p-value is less than 0.05, the sample does not follow the specified distribution. If p-value > 0.05, the sample may follow the specified distribution.")

        # Anderson-Darling Test
        st.subheader("Anderson-Darling Test")
        st.write(
            "Explanation: The Anderson-Darling test is a more sensitive test for normality compared to the Shapiro-Wilk test.")
        st.write(
            "Interpretation: If the p-value is less than 0.05, the data does not follow the normal distribution. If p-value > 0.05, the data may follow the normal distribution.")

if __name__ == "__main__":
    main()