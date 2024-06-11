from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='DataPipelineJobs',  # Replace with your package's name
    version='0.1',  # The version of your package
    packages=find_packages(),  # Automatically find all packages and subpackages
    install_requires=[required],
    python_requires='>=3.9',  # Minimum version requirement of the package
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },
)
