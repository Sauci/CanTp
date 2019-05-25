import os
from pycantp.ffi_builder import ffi_builder
from setuptools import find_packages, setup

name = 'pycantp'

ffi_builder.compile(tmpdir=os.path.join(os.path.dirname(os.path.realpath(__file__)), name, 'input'))

setup(author='Guillaume Sottas',
      author_email='guillaumesottas@gmail.com',
      description='AUTOSAR CanTp',
      entry_points={
          'console_scripts': ['cantp=cli:main']
      },
      ext_modules=[ffi_builder.distutils_extension()],
      include_package_data=True,
      install_requires=['cffi==1.12.3',
                        'jsonschema==3.0.1',
                        'mock==2.0.0',
                        'pycparser==2.19',
                        'pystache==0.5.4'],
      name=name,
      packages=find_packages(),
      url='https://github.com/Sauci/CanTp',
      version='0.11.1',
      zip_safe=False)
