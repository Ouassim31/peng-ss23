from setuptools import setup, find_packages

setup(
    name='myapp',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'google-api-python-client',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'requests',
        'cryptography',
        'pycountry-convert'

    ],
    
entry_points={
        'console_scripts': [
            'app = run:__main__',
        ],
    },
)
