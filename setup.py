from setuptools import setup, find_packages


with open('README.md', 'r') as f:
    README = f.read()


setup(name='ampdclient',
      version='0.0.1',
      description='asyncio-based client for mpd',
      long_description=README,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers"

          "License :: OSI Approved :: Apache Software License",

          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3.4",

          "Topic :: Multimedia :: Sound/Audio :: Players",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='Pierre Rust',
      author_email='pierre.rust@gmail.com',
      url='https://github.com/PierreRust/ampdclient',

      keywords=['mpd', 'asyncio'],
      install_requires=[],
      packages=find_packages()
      )
