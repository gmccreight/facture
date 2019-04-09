from distutils.core import setup

setup(
    name='Facture',
    version='0.1.0',
    author='Gordon McCreight',
    author_email='gordon@mccreight.com',
    packages=['facture', 'facture.test'],
    scripts=['bin/facture'],
    url='http://pypi.python.org/pypi/Facture/',
    license='LICENSE.txt',
    description='Factories that create fixtures',
    long_description=open('README.rst').read(),
    install_requires=[],
)
