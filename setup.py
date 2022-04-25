from setuptools import setup, Extension
import numpy as np

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

SRC_DIR = "csdt_stl_converter"
PACKAGES = [SRC_DIR]

setup(name='csdt_stl_converter',
      version='1.2.0',
      install_requires=['csdt_stl_tools', 'opencv-python', 'numpy'],
      description="Converts images to stl files",
      long_description=readme(),
      long_description_content_type="text/markdown",
      author='Andrew Hunn',
      author_email='ahunn@umich.edu',
      url='https://github.com/CSDTs/Adinkra_extrusion_converter',
      license='MIT',
      packages=['csdt_stl_converter'],
      include_package_data=True,
      entry_points={
          'console_scripts':
          ['adinkra_converter=csdt_stl_converter.adinkra_converter:main']
      }
      )
