from pycantp.ffi_builder import ffi_builder
from setuptools import setup

# ffi_builder.compile()

setup(author='Guillaume Sottas',
      author_email='guillaumesottas@gmail.com',
      description='AUTOSAR CanTp',
      include_package_data=True,
      install_requires=['cffi', 'mock'],
      name='pycantp',
      ext_modules=[ffi_builder.distutils_extension()],
      packages=['pycantp'],
      url='https://github.com/Sauci/CanTp',
      version='0.11.1',
      zip_safe=False)
