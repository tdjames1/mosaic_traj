#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plot timeseries output from ROTRAJ trajectory model

This module was developed by CEMAC as part of the ACRoBEAR
Project.

.. module:: plot_ts
   :synopsis: Plot time series from trajectory data

.. moduleauthor:: Tamora D. James <t.d.james1@leeds.ac.uk>, CEMAC (UoL)

:copyright: © 2022 University of Leeds.
:license: BSD 3-clause (see LICENSE)


Example::
        plot_ts.py <file>

        <file> Path to file containing trajectory data

"""
# standard library imports
import os
import sys
import datetime as dt
import argparse
import math

# third party imports
import matplotlib
matplotlib.use('Agg')  # use Agg backend for matplotlib
import matplotlib.pyplot as plt

# local imports
from read_traj import read_traj


def parse_args():
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter)

    parser.add_argument('file', type=str,
                        metavar='file',
                        help='''Path to trajectory data''')

    pa = parser.parse_args()

    # Check if file exists
    if pa.file and not os.path.exists(pa.file):
        err_msg = "File {0} does not exist\n"
        err_msg = err_msg.format(pa.file)
        raise ValueError(err_msg)

    return (pa.file)


def main():

    rtraj_file = parse_args()

    data, metadata = read_traj(rtraj_file)

    ts = metadata['trajectory base time']
    nattr = metadata['number of attributes']

    fig, ax = plt.subplots(nrows=nattr, figsize=(6,12), tight_layout=True)

    summary = data.groupby(level=0).mean()

    summary[metadata['attribute names']].plot(ax=ax, subplots=True, rot=45)

    for a in ax.flat:
        a.set(xlabel='Release time', ylabel='Trajectory average')

    traj_dt = dt.datetime.strptime(ts, '%Y%m%d00')
    fig.suptitle(traj_dt.strftime('%Y%m%d'))

    filename = os.path.basename(rtraj_file)
    plt.savefig(filename + '_summary.png')
    plt.close()


if __name__ == '__main__':
    main()
