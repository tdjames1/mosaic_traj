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

    parser.add_argument('--step', type=int, default=None,
                        help='''Step value to be plotted''')

    parser.add_argument('--cluster-name', type=str, default=None,
                        help='''Cluster variable name''')

    parser.add_argument('--cluster-values', type=float, nargs='+', default=None,
                        help='''Cluster values to be plotted''')

    parser.add_argument('--reverse-yaxis', action='store_true', default=False,
                        help='''Reverse order of values on plot's y axis''')

    pa = parser.parse_args()

    # Check if file exists
    if pa.path and not os.path.exists(pa.path):
        raise ValueError(f"Path {pa.path} does not exist\n")

    # Check if output directory exists
    if pa.out_dir and not os.path.isdir(pa.out_dir):
        raise ValueError(f"Path {pa.out_dir} is not a directory \n")

    return pa


def plot_hm(path,
            out_dir,
            start_date=None,
            end_date=None,
            attr=None,
            step=None,
            cluster_name=None,
            cluster_values=None,
            reverse_yaxis=False):

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
    if cluster_values:
        data = data.set_index(data.index.set_levels(cluster_values, level='CLUSTER'))
    data = data.set_index(data.index.set_names({
        'CLUSTER': cluster_name if cluster_name else 'Cluster',
        'READ'   : 'Release time',
    }))
    if step is not None:
        data = data[data.index.isin([step], level='STEP')]

    fig, ax = plt.subplots(nrows=nattr, figsize=(6,3*nattr), tight_layout=True)
    if nattr > 1:
        for i, a in enumerate(ax):
            if reverse_yaxis:
                a.invert_yaxis()
            plot_data(data, attr_names[i], ax=a)
    else:
        if reverse_yaxis:
            ax.invert_yaxis()
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
    idx, cols, _ = data.index.names
    dfp = data.pivot_table(index=idx, columns=cols,
                           values=var, aggfunc='mean')
    if any(map(lambda x: x < 2, dfp.shape)):
        raise ValueError("Expecting at least 2 clusters / reads")
    ctr = ax.contourf(dfp.columns, dfp.index, dfp)
    cbar = plt.gcf().colorbar(ctr, ax=ax)
    cbar.ax.set_ylabel(var)
    ax.set(xlabel=cols, ylabel=idx)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')


def main():
    args = parse_args()
    plot_hm(**vars(args))


if __name__ == '__main__':
    main()
