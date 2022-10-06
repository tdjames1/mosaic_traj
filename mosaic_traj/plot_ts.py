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

plot_ts.py <path> --start <start_date> --end <end_date> --out <plot_dir> --attr <attr>

<path> Path to trajectory data

<start_date> Start date in ISO format YYYY-MM-DD

<end_date> End date (inclusive) in ISO format YYYY-MM-DD

<plot_dir> Path to save plots

<attr> Attribute to plot

"""
# standard library imports
import os
import sys
import datetime as dt
import argparse
import math

# third party imports
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # use Agg backend for matplotlib
import matplotlib.pyplot as plt

# local imports
from .read_traj import read_traj, read_data


def parse_args():
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter)

    parser.add_argument('path', type=str,
                        metavar='path',
                        help='''Path to trajectory data''')

    parser.add_argument('--out', type=str,
                        metavar='output directory',
                        help='''Path to output directory''')

    parser.add_argument('--start', type=str,
                        metavar='start date',
                        help='''Start date''')

    parser.add_argument('--end', type=str,
                        metavar='end date',
                        help='''End date''')

    parser.add_argument('--attr', type=str,
                        metavar='attribute', default=None,
                        help='''Attribute''')

    pa = parser.parse_args()

    # Check if file exists
    if pa.path and not os.path.exists(pa.path):
        err_msg = "Path {0} does not exist\n".format(pa.path)
        raise ValueError(err_msg)

    # Check if output directory exists
    if pa.out and not os.path.isdir(pa.out):
        err_msg = "Path {0} is not a directory \n".format(pa.out)
        raise ValueError(err_msg)

    return (pa.path, pa.out, pa.start, pa.end, pa.attr)


def main():

    rtraj_path, out_dir, start, end, attr = parse_args()

    traj_data = []
    if start is not None:
        traj_data = read_data(rtraj_path, start, end)
    else:
        data, metadata = read_traj(rtraj_path)
        traj_data.append((data, metadata))

    nattr = traj_data[0][1]['number of attributes']
    attr_names = traj_data[0][1]['attribute names']

    if attr is not None:
        index = [i for i, s in enumerate(attr_names) if attr in s]
        if len(index):
            nattr = len(index)
            attr_names = [attr_names[j] for j in index]

    fig, ax = plt.subplots(nrows=nattr, figsize=(6,3*nattr), tight_layout=True)

    dates = []
    traj_dt = None
    for i, (data, metadata) in enumerate(traj_data):
        timestamp = metadata['trajectory base time']
        traj_dt = dt.datetime.strptime(timestamp, '%Y%m%d00')
        if i == 0:
            dates.append(traj_dt.strftime('%Y%m%d'))

    if i > 0:
        dates.append(traj_dt.strftime('%Y%m%d'))

    plot_data = [x[0] for x in traj_data]
    plot_data = pd.concat(plot_data)

    summary = plot_data.groupby(level=0).mean()

    summary[attr_names].plot(ax=ax, subplots=True, rot=45)

    if nattr > 1:
        for a in ax.flat:
            a.set(xlabel='Release time', ylabel='Trajectory average')
    else:
        ax.set(xlabel='Release time', ylabel='Trajectory average')

    title = ' to '.join(dates)
    fig.suptitle(title)

    suffix = 'summary' if attr is None else attr.replace(' ', '_')
    file_name = '-'.join(dates) + '_' + suffix + '.png'
    if out_dir is not None:
        file_name = os.path.join(out_dir, file_name)

    plt.savefig(file_name)
    plt.close()


if __name__ == '__main__':
    main()
