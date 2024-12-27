from setuptools import setup, find_packages

setup(
    name="vizura",
    version="0.1.23",
    packages=find_packages(),
    install_requires=[
        "dash",
        "dash_bootstrap_components",
        "dash_core_components",
        "dash_html_components",
        "matplotlib",
        "numpy",
        "pandas",
        "plotly",
        "scikit_learn",
        "scipy",
        "seaborn",
        "setuptools>=70.0.0",
        "streamlit",
    ],
    author="Aswath Shakthi",
    author_email="aswathshakthi@outlook.com",
    description="Tool for Data Analysis",
    long_description=open('README.md').read() if open('README.md').read() else "",
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    python_requires='>=3.6',
    project_urls={
        "Demo": "https://vizura.streamlit.app",
        "Source": "https://github.com/ash-sha/vizura",
    }
)