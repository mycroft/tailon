from setuptools import setup
import os

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def _read_reqs(relpath):
    fullpath = os.path.join(os.path.dirname(__file__), relpath)
    with open(fullpath) as f:
        return [s.strip() for s in f.readlines()
                if (s.strip() and not s.startswith("#"))]

_TESTS_REQUIREMENTS_TXT = _read_reqs("requirements-dev.txt")
_TEST_REQUIRE = [l for l in _TESTS_REQUIREMENTS_TXT if "://" not in l]

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers',
]

requirements = [
    'tornado>=4.0.0, <5.0.0',
    'tornado-http-auth>=1.0.0',
    'sockjs-tornado>=1.0.0',
    'PyYAML>=3.11',
]

kw = {
    'name':             'tailon',
    'version':          '1.3.0-criteo.7',
    'description':      'Webapp for looking at and searching through log files',
    'long_description': open('README.rst').read(),
    'author':           'Georgi Valkov',
    'author_email':     'georgi.t.valkov@gmail.com',
    'license':          'Revised BSD License',
    'url':              'https://github.com/gvalkov/tailon',
    'keywords':         'log monitoring tail',
    'packages':         ['tailon'],
    'classifiers':      classifiers,
    'install_requires': requirements,
    'tests_require':    _TEST_REQUIRE,
    'setup_requires':   ['pytest-runner'],
    'include_package_data': True,
    'zip_safe': False,
    'entry_points': {
        'console_scripts': [
            'tailon = tailon.main:main',
        ]
    },
}

if __name__ == '__main__':
    setup(**kw)
