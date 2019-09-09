from setuptools import setup

setup(
    name='generalflair',
    packages=['FlairBot', 'FlairBotMgmt'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-login',
        'flask-sqlalchemy',
        'flask-markdown',
        'jinja2',
        'sqlalchemy',
        'SpazUtils',
        'sentry-sdk[flask]==0.10.2',
        'psycopg2-binary',
        'werkzeug',
        'sshtunnel',
        'datadog', 'praw'
    ],
)

