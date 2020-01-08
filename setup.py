from distutils.core import setup

setup(
    name='facturedata',
    version='0.2.01',
    author='Gordon McCreight',
    author_email='gordon@mccreight.com',
    packages=['facturedata'],
    url='http://pypi.python.org/pypi/facturedata/',
    license='LICENSE.txt',
    description='Factories that create fixtures',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'facture = facturedata.__main__:main'
        ]
    }
)
