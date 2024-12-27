# Vizura


![Vizura Logo](https://raw.githubusercontent.com/ash-sha/vizura/refs/heads/main/logo.png)

![Build Status](https://img.shields.io/github/workflow/status/ash-sha/vizura/Python%20CI?label=build)
![PyPI Version](https://img.shields.io/pypi/v/vizura?logo=pypi)
![License](https://img.shields.io/pypi/l/vizura?logo=open-source)

Welcome to the **Vizura** package, a comprehensive tool for analyzing and visualizing basic statistics.

**Vizura** is a data analysis and visualization tool developed using Python and Streamlit. It provides valuable insights into datasets by generating summary statistics and offering interactive visualizations.

## Installation

To install Vizura, execute the following command:

```bash
pip install git+https://github.com/ash-sha/vizura.git #on Project Root directory
````
or  use the standard installation via PyPI:
```
pip install vizura
```

## Usage Example

```python
import vizura
# Refer https://dash.plotly.com for run_server parameters
# Example usage of vizura
data = ...  # Load your dataset

#refer dash docs for run_server parameters

app = numerical(data) # Generates a dashboard displaying summary statistics for numerical columns in the dataset.
app.run_server(port=8000) # can add port number of choice, but not identical


app = categorical(data) # Displays a dashboard of summary statistics for categorical columns.
app.run_server(port=8001) # can add port number of choice, but not identical 

calculate_correlations(data) # Computes correlations between filtered numerical columns using Pearson, Kendall, and Spearman methods.

plot_correlation(data) # Visualizes the correlation matrices for Pearson, Kendall, and Spearman.
```

###  Preview


![Video Thumbnail](https://raw.githubusercontent.com/ash-sha/Vizura/refs/heads/main/thumbnail.png)


For a live demo and example statistics, you can explore the demo at: [https://vizura.streamlit.app](https://vizura.streamlit.app)

## Contributing

We welcome contributions to improve **Vizura**! To contribute:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to your branch (`git push origin feature-name`)
6. Create a pull request