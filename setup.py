from distutils.core import setup

setup(name='cyclic_data',
      version='1.0',
      description='Analysis and plotting of cyclic data',
      author='Knut Andreas Meyer',
      author_email='knutam@gmail.com',
      url='https://cyclic-after-pdef-r260.readthedocs.io/en/latest/',
      packages=['cyclic_data', 
                'cyclic_data.hdf5_data',
                'cyclic_data.filter',
                'cyclic_data.plot',
                'cyclic_data.yield'],
     )
