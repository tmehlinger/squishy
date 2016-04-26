#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
import pip


with open('README.md') as fr:
    with open('CHANGELOG.md') as fc:
        long_description = '{}\n\n{}'.format(fr.read(), fc.read())


ver = sys.version_info[:2]

if (ver[0] == 2 and ver < (2, 6)) or (ver[0] == 3 and ver < (3, 3)):
    raise RuntimeError('unsupported Python version')

extras_require = {'gevent': ['gevent>=1.1.0']}

if ver[0] == 2:
    extras_require['futures'] = ['futures>=3.0.5']

requirements = pip.req.parse_requirements(
    'requirements.txt', session=pip.download.PipSession()
)
install_requires = [str(r.req) for r in requirements]


setup(
    name='squishy',
    version='0.0.1',
    description='A simple Amazon SQS consumer library.',
    long_description=long_description,
    author='Travis Mehlinger',
    author_email='tmehlinger@gmail.com',
    url='https://github.com/tmehlinger/squishy',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'squishy = squishy.cli:main',
        ],
    },
    install_requires=install_requires,
    extras_require=extras_require,
    license='BSD',
    keywords='squishy',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    zip_safe=False,
)
