#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Plot Hovmoller diagram from ROTRAJ trajectory model output

This module was developed by CEMAC as part of the ACRoBEAR
project.

.. module:: plot_hm
   :synopsis: Plot Hovmoller diagram from trajectory data

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
from .read_traj import read_traj, read_data


PRES = [985,975,950,925,900,875,850,825,800,775,750,700,650,600,550,500,450,400,350,300]


def parse_args():
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter)

    parser.add_argument('path', type=str,
                        help='''Path to trajectory data''')

    parser.add_argument('--out', type=str,
                        help='''Path to output directory''')

    parser.add_argument('--start', type=str,
                        metavar='YYYY-MM-DD',
                        help='''Start date  in ISO format YYYY-MM-DD''')

    parser.add_argument('--end', type=str,
                        metavar='YYYY-MM-DD',
                        help='''End date (inclusive) in ISO format YYYY-MM-DD''')

    parser.add_argument('--attr', type=str, default=None,
                        help='''Attribute to be plotted''')

    parser.add_argument('--step', type=int, default=None,
                        help='''Step value to be plotted''')

    pa = parser.parse_args()

    # Check if file exists
    if pa.path and not os.path.exists(pa.path):
        err_msg = "Path {0} does not exist\n".format(pa.path)
        raise ValueError(err_msg)

    # Check if output directory exists
    if pa.out and not os.path.isdir(pa.out):
        err_msg = "Path {0} is not a directory \n".format(pa.out)
        raise ValueError(err_msg)

    return pa


def plot_hm(path, out_dir=None, start_date=None, end_date=None, attr=None, step=None):

    data, metadata = read_data(path, start_date, end_date)

    nattr = metadata[0]['number of attributes']
    attr_names = metadata[0]['attribute names']
    nclust = metadata[0]['number of clusters']

    if attr is not None:
        index = [i for i, s in enumerate(attr_names) if attr in s]
        if len(index):
            nattr = len(index)
            attr_names = [attr_names[j] for j in index]
        else:
            raise ValueError(f"Attribute {attr} not found in {attr_names}")

    dates = []
    for md in metadata:
        timestamp = md['trajectory base time']
        traj_dt = dt.datetime.strptime(timestamp, '%Y%m%d%H')
        dates.append(traj_dt.strftime('%Y%m%d'))
    if len(dates) > 1:
        dates = dates[0::len(dates)-1]

    data = pd.concat(data)
    data = data.set_index(data.index.set_levels(PRES, level='CLUSTER'))
    if step is not None:
        data = data[data.index.isin([step], level='STEP')]

    fig, ax = plt.subplots(nrows=nattr, figsize=(6,3*nattr), tight_layout=True)
    if nattr > 1:
        for i, a in enumerate(ax):
            plot_data(data, attr_names[i], ax=a)
    else:
        plot_data(data, attr_names[0], ax=ax)

    title = ' to '.join(dates)
    fig.suptitle(title)

    suffix = '' if attr is None else '_' + attr.replace(' ', '_')
    suffix = suffix if step is None else suffix + f'_T-{step}'
    file_name = '-'.join(dates) + '_hm' + suffix + '.png'
    if out_dir is not None:
        file_name = os.path.join(out_dir, file_name)

    plt.savefig(file_name)
    plt.close()


def plot_data(data, var, ax):
    dfp = data.pivot_table(index='CLUSTER', columns='READ',
                           values=var, aggfunc='mean')
    ctr = ax.contourf(dfp.columns, dfp.index, dfp)
    cbar = plt.gcf().colorbar(ctr, ax=ax)
    cbar.ax.set_ylabel(var)
    ax.set(xlabel='Release time', ylabel='Pressure (hPa)')
    ax.invert_yaxis()


def main():
    args = parse_args()
    plot_hm(args.path,
            args.out,
            args.start,
            args.end,
            args.attr,
            args.step)


if __name__ == '__main__':
    main()
