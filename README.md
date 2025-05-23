# qeg-nv-control

A class-based pythonic interface for controlling optical
defects (in diamond) using Quantum Machines hardware. These tools
enable easy loading and saving of experimental data, along with
all configuration settings used when the experiment was originally
run.

This should allow seamless looping through many different experiments,
including adaptive recalibration and easy integration with other
control software, such as qudi.

## Install Instructions

Ensure all requirements are installed from `requirements.txt`. To more
easily change default settings of things like the configuration files,
it is recomended to install this package in editable mode.

To install this package in developer mode, open a terminal in this
directory, and activate your python environment (`<=3.12 && >= 3.7`)
of choosing, and then run
`py setup.py develop`
followed by
`pip install -e .`

## Formatting conventions

Please try to use a linter. We prefer `python-black`, which can be set
to auto-format on save with a VSCode extension, or something similar in
your favorite IDE.
