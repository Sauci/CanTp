import os
from pycantp.ffi_builder import ffi_builder
from setuptools import setup

name = 'pycantp'
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), name, 'input')

ffi_builder.compile(tmpdir=path)

setup(author='Guillaume Sottas',
      author_email='guillaumesottas@gmail.com',
      description='AUTOSAR CanTp',
      ext_modules=[ffi_builder.distutils_extension()],
      include_package_data=True,
      install_requires=['cffi==1.12.3',
                        'mock==2.0.0',
                        'pycparser==2.19'],
      name=name,
      packages=[name],
      url='https://github.com/Sauci/CanTp',
      version='0.11.1',
      zip_safe=False)
