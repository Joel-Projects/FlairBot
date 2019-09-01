from setuptools import setup

setup(
    name='generalflair',
    packages=['FlairBot', 'FlairBotMgmt'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-login',
        'SpazUtils',
        'sentry-sdk[flask]==0.10.2',
        'psycopg2-binary',
        'jinja2',
        'sqlalchemy',
        'flask-sqlalchemy',
        'werkzeug', 'sshtunnel', 'datadog'
    ],
)

