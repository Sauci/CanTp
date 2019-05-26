from setuptools import find_packages, setup

name = 'can_tp_gen'

setup(author='Guillaume Sottas',
      author_email='guillaumesottas@gmail.com',
      description='AUTOSAR CAN transport layer code generator',
      entry_points={
          'console_scripts': ['{}=can_tp_gen:main'.format(name)]
      },
      install_requires=['jsonschema==3.0.1',
                        'pystache==0.5.4'],
      name=name,
      packages=find_packages(),
      url='https://github.com/Sauci/CanTp',
      version='0.11.1',
      zip_safe=False)
