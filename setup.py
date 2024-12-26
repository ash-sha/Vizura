from setuptools import setup, find_packages

setup(
    name="Vizura",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib==3.10.0",
        "numpy==2.2.1",
        "pandas==2.2.3",
        "plotly==5.24.1",
        "scikit_learn==1.6.0",
        "scipy==1.14.1",
        "seaborn==0.13.2",
        "setuptools==68.2.0",
        "streamlit==1.41.1",
        "openpyxl"
    ],
    entry_points={
        'console_scripts': [
            'vizura=vizura.streamlit_app:main',
        ],
    },
    author="Aswath Shakthi",
    author_email="aswathshakthi@outlook.com",
    description="Tool for Data Analysis",
    long_description=open('README.md').read() if open('README.md').read() else "",
    long_description_content_type='text/markdown',
    url="https://github.com/ash-sha/vizura",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
