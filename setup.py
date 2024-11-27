from setuptools import setup, find_packages

setup(
    name='DataReport',  # Replace with your package name
    version='0.1',
    author='Yash Singhal',  # Add your name
    author_email='yashskd1026@gmail.com',  
    description='A package for generating data analysis reports',
    packages=find_packages(),  # Automatically find all subpackages
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'fpdf'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  
)
