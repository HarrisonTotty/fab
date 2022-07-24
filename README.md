![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/HarrisonTotty/fab?include_prereleases&style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/HarrisonTotty/fab?style=flat-square)
![Read the Docs](https://img.shields.io/readthedocs/fablib?style=flat-square)

# Flesh and Blood TCG Analysis Environment

A Python library and [Jupyter Lab](https://jupyter.org/) environment for
analysis of the Flesh and Blood trading card game. Card data powered by
[flesh-cube/flesh-and-blood-cards](https://github.com/flesh-cube/flesh-and-blood-cards).


## Getting Started

In short, there are basically two ways you can start using `fab`: either
downloading and installing the latest release `.whl` via `pip`, _or_ building
and running the containerized Jupyter Lab environment.

To learn more about working with the library, check out the [Getting
Started](notebooks/getting-started.ipynb) notebook or the [Online API
Documentation](https://fablib.readthedocs.io/en/latest/).

### Installing Locally

Ensure that you have Python 3.9+ and `pip` installed and then run:

```bash
export VERSION=0.3.0
curl "https://github.com/HarrisonTotty/fab/releases/download/v${VERSION}/fab-${VERSION}-py3-none-any.whl" -o fab.whl
pip install fab.whl
```

### Building Locally

Ensure that you have Python 3.9+ installed, along with
[poetry](https://python-poetry.org/) and then run:

```bash
# Clone the repository.
git clone https://github.com/HarrisonTotty/fab.git && cd fab

# Build the wheel package.
poetry install && poetry build

# Install the wheel package.
pip install dist/*.whl
```

### Building & Running Container Image

Note that you'll need `docker` installed.

```bash
# Clone the repository.
git clone https://github.com/HarrisonTotty/fab.git && cd fab

# Build and execute the container environment.
./build-env.sh && ./run-env.sh
```

(then navigate to `http://127.0.0.1:8888/lab`)


## Project Status

This project is still really early in development. It's code is mostly based on
a personal finance platform I wrote called
[tcat](https://github.com/HarrisonTotty/tcat) and is pretty opinionated. However
if you want to contribute to the project, feel free to reach out to me. I
imagine contribution requirements will morph as/if the project gets bigger.
