from setuptools import setup


def readme() -> str:
    with open('README.md') as f:
        return f.read()


def requirements() -> list[str]:
    with open('requirements.txt') as f:
        return [
            line.strip()
            for line in f if line.strip() != ''
        ]


setup(
    name='eoglib',
    version='0.2.0-beta',
    description='Eye movement processing library',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications',
        'Intended Audience :: Education',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Programming Language :: Python :: 3.9',
    ],
    url='http://github.com/idertator/eoglib',
    author='Roberto Antonio Becerra García',
    author_email='idertator@gmail.com',
    license='GPLv3',
    packages=[
        'eoglib',
        'eoglib.identification',
        'eoglib.io',
        'eoglib.models',
    ],
    install_requires=requirements(),
    zip_safe=False
)
