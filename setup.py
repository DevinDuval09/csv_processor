
from setuptools import setup

setup(
        name='csv_processor',
        version='0.0.1',
        author='Devin Duval',
        author_email='DevinDuval09@gmail.com',
        package_dir={'':'.', '.':'.'},
        packages=[],
        package_data={"":['*.csv']},
        include_package_data=True,
        install_requires=[],
        entry_points={'console_scripts': []},
        )