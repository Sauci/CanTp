from setuptools import find_packages, setup

name = 'can_tp'

setup(author='Guillaume Sottas',
      author_email='guillaumesottas@gmail.com',
      description='AUTOSAR CAN Transport Protocol code generator',
      entry_points={
          'console_scripts': ['{0}={0}.__main__:main'.format(name)]
      },
      include_package_data=True,
      install_requires=['jsonschema==3.0.1',
                        'pystache==0.5.4'],
      name=name,
      packages=find_packages(),
      url='https://github.com/Sauci/CanTp',
      version='0.0.1',
      zip_safe=False)
