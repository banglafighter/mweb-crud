from setuptools import setup, find_packages
import os
import pathlib

CURRENT_DIR = pathlib.Path(__file__).parent
README = (CURRENT_DIR / "README.md").read_text()

env = os.environ.get('source')


def get_dependencies():
    dependency = [
        "marshmallow==4.0.0",
        "marshmallow-sqlalchemy==1.4.2",
        "apispec==6.8.2"
    ]

    if env and env == "code":
        return dependency

    return dependency + ["mw-common"]


setup(
    name='mweb-crud',
    version='0.0.1',
    url='https://github.com/banglafighter/mweb-crud',
    license='Apache 2.0',
    author='Bangla Fighter',
    author_email='banglafighter.com@gmail.com',
    description='Helps to easily perform Create, Read, Update, & Delete operations for REST-API and server-side rendering data processing, and can generate OpenAPI.',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=get_dependencies(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ]
)
