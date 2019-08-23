from setuptools import setup

setup(
    name='generalflair',
    packages=['FlairBot', 'FlairBotMgmt'],
    include_package_data=True,
    install_requires=[
        'flask',
        'SpazUtils',
        'sentry-sdk[flask]==0.10.2',
        'markdown',
        'psycopg2-binary'
    ],
)

