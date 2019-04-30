from pycantp.ffi_builder import ffi_builder
from setuptools import setup

# ffi_builder.compile()

setup(author='Guillaume Sottas',
      author_email='guillaumesottas@gmail.com',
      description='AUTOSAR CanTp',
      ext_modules=[ffi_builder.distutils_extension()],
      include_package_data=True,
      install_requires=['cffi==1.12.3',
                        'mock==2.0.0'],
      name='pycantp',
      packages=['pycantp'],
      url='https://github.com/Sauci/CanTp',
      version='0.11.1',
      zip_safe=False)
