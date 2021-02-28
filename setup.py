from distutils.core import setup

#  Generate requirement list from requirements.txt file
with open('requirements.txt', 'r') as fid:
    requirements = [line for line in fid if not line.strip().startswith('#')]

#  Call setup to make it installable by pip install .
setup(name='cyclic_data',
      version='1.0',
      description='Analysis and plotting of cyclic data',
      author='Knut Andreas Meyer',
      author_email='knutam@gmail.com',
      url='https://cyclic-after-pdef-r260.readthedocs.io/en/latest/',
      packages=['cyclic_data', 'cyclic_data.utils'],
      install_requires=requirements
     )
