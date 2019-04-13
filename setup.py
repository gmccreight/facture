from distutils.core import setup

setup(
    name='Facture',
    version='0.1.1',
    author='Gordon McCreight',
    author_email='gordon@mccreight.com',
    packages=['facture'],
    url='http://pypi.python.org/pypi/Facture/',
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
