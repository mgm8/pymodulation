<h1 align="center">
    <a href="https://mgm8.github.io/pymodulation/"><img src="docs/img/logo.jpg" alt="PyModulation" width="50%"></a>
</h1>

<a href="https://pypi.org/project/pymodulation/">
    <img src="https://img.shields.io/pypi/v/pymodulation?style=for-the-badge">
</a>
<a href="https://pypi.org/project/pymodulation/">
    <img src="https://img.shields.io/pypi/pyversions/pymodulation?style=for-the-badge">
</a>
<a href="https://github.com/mgm8/pymodulation/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/mgm8/pymodulation?style=for-the-badge">
</a>
<a href="https://github.com/mgm8/pymodulation/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/mgm8/pymodulation/test.yml?style=for-the-badge">
</a>

## Overview

PyModulation is a Python library that implements a collection of digital modulation and demodulation techniques with a strong focus on Software-Defined Radio (SDR) applications. The library is designed to provide a simple, consistent, and extensible interface for working with different modulation schemes, enabling rapid development, testing, and prototyping of wireless communication systems.

The main objective of PyModulation is to allow the direct use of supported modulation techniques with SDR hardware, while remaining flexible enough to be used in simulations, offline signal processing, and educational contexts. By abstracting common modulation tasks, the library helps users focus on system design and experimentation rather than low-level signal handling.

PyModulation is suitable for a wide range of applications, including SDR-based transmitters and receivers, communication protocol prototyping, academic research, and teaching digital communications concepts. Its modular architecture makes it easy to extend with new modulation schemes and integrate with existing Python-based SDR and signal-processing toolchains.

The following modulations are currently supported:

* GFSK/GMSK

## Dependencies

* NumPy
* SciPy

## Installing

This library can be installed directly from the source files:

* ```python setup.py install```

## Documentation

The documentation page is available [here](https://mgm8.github.io/pymodulation/). Instructions to build the documentation page are described below.

Contributing instructions are also available [here](https://github.com/mgm8/pyngham/blob/main/CONTRIBUTING.md).

### Dependencies

* [Sphinx](https://pypi.org/project/Sphinx/)

### Building the Documentation

The documentation pages can be built with Sphinx by running the following command inside the ``docs`` folder:

* ```make html```

## License

This project is licensed under LGPLv3 license.
