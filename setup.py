from setuptools import setup

_readme = 'README.md'

with open(_readme, 'r', encoding='utf-8') as f:
    long_description = f.read()

_release = 'RELEASE'

with open(_release, 'r') as f:
    _version = f.readline().split()[0]

_extras_path = 'extras'
with open(_extras_path+'/.env', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('PACKAGE='):
            _package = line.splitlines()[0].split('=')[1].lower()
        if line.startswith('URL='):
            _url = line.splitlines()[0].split('=')[1].lower()
        if line.startswith('AUTHORS='):
            _authors = line.splitlines()[0].split('=')[1].lower()
        if line.startswith('DESCR='):
            _descr = line.splitlines()[0].split('=')[1].lower()
        if line.startswith('CORR_AUTHOR='):
            _corr_author = line.splitlines()[0].split('=')[1].lower()

setup(
    name                          = _package,
    version                       = _version,
    author                        = _authors,
    author_email                  = _corr_author,
    description                   = _descr,
    long_description              = long_description,
    long_description_content_type = 'text/markdown',
    url                           = _url,
    packages                      = [_package],
    package_dir                   = {_package: _package},
    include_package_data          = True,
    # install_requires              = required,
    test_suite                    = 'pytest',
    license                       = 'MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires               = '>=3.5',
)
