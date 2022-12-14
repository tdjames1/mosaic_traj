#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Plot timeseries output from ROTRAJ trajectory model

This module was developed by CEMAC as part of the ACRoBEAR
project.

.. module:: plot_ts
   :synopsis: Plot time series from trajectory data

.. moduleauthor:: Tamora D. James <t.d.james1@leeds.ac.uk>, CEMAC (UoL)

:copyright: © 2022 University of Leeds.
:license: BSD 3-clause (see LICENSE)

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
from .read_traj import read_data


def parse_args():
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter)

    parser.add_argument('path', type=str,
                        help='''Path to trajectory data''')

    parser.add_argument('out_dir', type=str,
                        help='''Path to output directory''')

    parser.add_argument('--start-date', type=str,
                        metavar='YYYY-MM-DD',
                        help='''Start date  in ISO format YYYY-MM-DD''')

    parser.add_argument('--end-date', type=str,
                        metavar='YYYY-MM-DD',
                        help='''End date (inclusive) in ISO format YYYY-MM-DD''')

    parser.add_argument('--attr', type=str, default=None,
                        help='''Attribute to be plotted''')

    pa = parser.parse_args()

    # Check if file exists
    if pa.path and not os.path.exists(pa.path):
        raise ValueError(f"Path {pa.path} does not exist\n")

    # Check if output directory exists
    if pa.out_dir and not os.path.isdir(pa.out_dir):
        raise ValueError(f"Path {pa.out_dir} is not a directory \n")

    return pa


def plot_ts(path, out_dir, start_date=None, end_date=None, attr=None):

    data, metadata = read_data(path, start_date, end_date)

    nattr = metadata[0]['number of attributes']
    attr_names = metadata[0]['attribute names']

    if attr is not None:
        index = [i for i, s in enumerate(attr_names) if attr in s]
        if len(index):
            nattr = len(index)
            attr_names = [attr_names[j] for j in index]

    dates = [dt.datetime.strptime(md['trajectory base time'],
                                  '%Y%m%d%H').strftime('%Y%m%d')
             for md in metadata]
    if len(dates) > 1:
        dates = dates[0::len(dates)-1]

    data = pd.concat(data)
    data = data.set_index(data.index.set_names({
        'READ': 'Release time',
    }))

    fig, ax = plt.subplots(nrows=nattr, figsize=(6,3*nattr), tight_layout=True)
    _, idx, _ = data.index.names
    dfp = data.pivot_table(index=idx, values=attr_names, aggfunc='mean')
    dfp.plot(ax=ax, rot=45, subplots=True, legend=None)
    if nattr > 1:
        for i, a in enumerate(ax.flat):
            a.set(ylabel=dfp.columns[i])
    else:
        ax.set(ylabel=dfp.columns[0])

    title = ' to '.join(dates)
    fig.suptitle(title)

    suffix = 'summary' if attr is None else attr.replace(' ', '_')
    file_name = '-'.join(dates) + '_' + suffix + '.png'
    if out_dir is not None:
        file_name = os.path.join(out_dir, file_name)

    plt.savefig(file_name)
    plt.close()


def main():
    args = parse_args()
    plot_ts(**vars(args))


if __name__ == '__main__':
    main()
