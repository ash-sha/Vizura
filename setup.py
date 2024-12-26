from setuptools import setup, find_packages

setup(
    name="Vizura",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "numpy",
        "pandas",
        "plotly",
        "scikit_learn",
        "scipy",
        "seaborn",
        "setuptools",
        "streamlit",
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
