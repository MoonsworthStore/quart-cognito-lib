from setuptools import setup
from os import path

pwd = lambda f: path.join(path.abspath(path.dirname(__file__)), f)

setup(
    name='quart_cognito_lib',
    description="A Quart extension that supports protecting routes with AWS Cognito following OAuth 2.1 best practices.",
    author='mblackgeo',
    author_email='18327836+mblackgeo@users.noreply.github.com',
    url='https://github.com/mblackgeo/flask-cognito-lib',
    version='1.6.1',
    packages=[
        'quart_cognito_lib',
        'quart_cognito_lib.services'
    ]
)