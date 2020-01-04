from setuptools import setup

setup(
    name='cffi-xxh3',
    version='0.0.0',
    author='nathants',
    author_email='me@nathants.com',
    url='http://github.com/nathants/cffi-xxh3/',
    packages=['xxh3'],
    install_requires=['cffi>=1.0.0'],
    cffi_modules=["xxh3/__init__.py:ffibuilder"],
    setup_requires=['cffi>=1.0.0'],
)
