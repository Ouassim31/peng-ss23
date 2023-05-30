from setuptools import setup,find_packages

setup(
    name='google-oauth',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'pycountry_convert',
        'google-auth-oauthlib',
        'google-api-python-client',
    ],
)