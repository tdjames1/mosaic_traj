#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plot output from ROTRAJ trajectory model

This module was developed by CEMAC as part of the ACRoBEAR
Project.

.. module:: plot_traj
   :synopsis: Plot trajectory data

.. moduleauthor:: Tamora D. James <t.d.james1@leeds.ac.uk>, CEMAC (UoL)

:copyright: © 2022 University of Leeds.
:license: GPL 3.0 (see LICENSE)


Example::
        plot_traj.py <file> --track <track_file>

        <file> Path to file containing trajectory data

        <track_file> Path to CSV containing ship track data

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
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# local imports
from read_traj import read_traj


def parse_args():
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter)

    parser.add_argument('traj', type=str,
                        metavar='trajectory file',
                        help='''Path to trajectory data''')

    parser.add_argument('--track', type=str,
                        metavar='track file',
                        help='''Path to ship track data''')

    pa = parser.parse_args()

    # Check if file exists
    if pa.traj and not os.path.exists(pa.traj):
        err_msg = "File {0} does not exist\n"
        err_msg = err_msg.format(pa.traj)
        raise ValueError(err_msg)

    # Check if track file exists
    if pa.track and not os.path.exists(pa.track):
        err_msg = "File {0} does not exist\n"
        err_msg = err_msg.format(pa.track)
        raise ValueError(err_msg)

    return (pa.traj, pa.track)


def main():

    rtraj_file, track_file = parse_args()

    data, metadata = read_traj(rtraj_file)

    filename = os.path.basename(rtraj_file)
    timestamp = metadata['trajectory base time']
    traj_dt = dt.datetime.strptime(timestamp, '%Y%m%d00')

    fig, ax = plt.subplots(figsize=(9,9), subplot_kw=dict(projection=ccrs.Orthographic(0, 90)))
    ax.coastlines(zorder=3)
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.gridlines()

    freq = 15
    periods = math.floor(len(data.groupby(level=0))/freq)
    dt_index = pd.date_range(traj_dt.strftime('%Y%m%d'), periods=periods, freq=str(freq)+"min")

    for ts in dt_index:
        try:
            traj = data.loc[ts]
        except KeyError:
            # timestamp not available
            continue
        # Get first index where P > 0 and first index where P > 0 and
        # P < 980 and plot traj between these points
        ind0 = traj[traj['P (MB)'] > 0].index[0]
        sel = traj[(traj['P (MB)'] > 0) & (traj['P (MB)'] < 980)]
        if len(sel) > 0:
            ind1 = sel.index[0]
            traj_sub = traj.loc[ind0:ind1]
        else:
            traj_sub = traj.loc[ind0:]
        plt.plot(traj_sub.LON, traj_sub.LAT,
                 color='blue', alpha=0.5,
                 transform=ccrs.PlateCarree(),
                 )

    if track_file is not None:
        track_data = pd.read_csv(track_file, index_col='timestamp')
        track_data.columns = [x.lower() for x in track_data.columns]
        track_sub = track_data[::60]
        plt.plot(track_sub.longitude, track_sub.latitude,
                 color='black', alpha=1.0, linewidth=0, marker='o', markersize=2,
                 transform=ccrs.PlateCarree(),
                 )

    # Set map extent
    ax.set_extent([-180, 180, 60, 90], ccrs.PlateCarree())

    plt.title(traj_dt.strftime('%Y%m%d'))
    plt.savefig(filename + '.png')
    plt.close()


if __name__ == '__main__':
    main()
