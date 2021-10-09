# stuiplot

Script for plotting [s-tui](https://github.com/amanusk/s-tui) logs.

## Usage

```
$ stuiplot --help
usage: stuiplot [-h] [--figure-path FIGURE_PATH] [--align-threshold ALIGN_THRESHOLD] [--minutes MINUTES] log [log ...]

Read s-tui csv log files & plot CPU frequency, temperature, &
utilization percentage as a function of time. All values shown are
means over all CPU cores.

positional arguments:
  log                   path to s-tui log file

optional arguments:
  -h, --help            show this help message and exit
  --figure-path FIGURE_PATH
                        if given, don't show the figure but write it to this file
  --align-threshold ALIGN_THRESHOLD
                        CPU utilization threshold for aligning the data on the time axis
  --minutes MINUTES     amount of time to show
```

## Installation

Install from PyPI with `pip install truhanen.stuiplot` and from sources with
`pip install .`.
