"""
freon
----------------

Keeps your data fresh just as freon keeps your food fresh in the fridge.

"""

from setuptools import setup, find_packages


setup(
    name='freon',
    version='0.1.0',
    url='http://github.com/linkyndy/freon',
    license='MIT',
    author='Andrei Horak',
    author_email='linkyndy@gmail.com',
    description='Keep your data fresh',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    extras_require={
        'dev': [
            'redis',
            'msgpack',
            'pytest',
            'mock'
        ]
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
