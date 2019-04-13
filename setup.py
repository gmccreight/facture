from distutils.core import setup

setup(
    name='Facture Data',
    version='0.1.6',
    author='Gordon McCreight',
    author_email='gordon@mccreight.com',
    packages=['facture-data'],
    url='http://pypi.python.org/pypi/FactureData/',
    license='LICENSE.txt',
    description='Factories that create fixtures',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'facture = facture.__main__:main'
        ]
    }
)
