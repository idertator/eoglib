from setuptools import setup
from typing import List


def readme() -> str:
    with open('README.md') as f:
        return f.read()


def requirements() -> List[str]:
    with open('requirements.txt') as f:
        return [
            line.strip()
            for line in f if line.strip() != ''
        ]


setup(
    name='eoglib',
    version='0.1',
    description='Eye movement processing library',
    long_description=readme(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha'
    ],
    url='http://github.com/idertator/eoglib',
    author='Roberto Antonio Becerra García',
    author_email='idertator@gmail.com',
    license='GPLv3',
    packages=[
        'eoglib',
        'eoglib.io',
    ],
    install_requires=requirements(),
    zip_safe=False
)
