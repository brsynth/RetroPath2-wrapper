import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

with open("retropath2/requirements.txt", 'r') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="retrorules",
    version="1.1.9",
    author="Thomas Duigou, Melchior du Lac, Joan Hérisson",
    author_email="joan.herisson@univ-evry.fr",
    description="RetroPath2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brsynth/RetroRules",
    packages=['retropath2'],
    package_dir={'retropath2': 'retropath2'},
    install_requires=required,
    include_package_data=True,
    test_suite = 'discover_tests',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
