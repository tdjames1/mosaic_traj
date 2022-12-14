#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Plot trajectory output from ROTRAJ trajectory model

This module was developed by CEMAC as part of the ACRoBEAR
project.

.. module:: plot_traj
   :synopsis: Plot trajectory data

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
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# local imports
from .read_traj import read_traj, read_data


def parse_args():
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter)

    parser.add_argument('path', type=str,
                        help='''Path to trajectory data''')

    parser.add_argument('--track', type=str,
                        help='''Path to ship track data''')

    parser.add_argument('--out', type=str,
                        help='''Path to output directory''')

    parser.add_argument('--start', type=str,
                        metavar='YYYY-MM-DD',
                        help='''Start date in ISO format YYYY-MM-DD''')

    parser.add_argument('--end', type=str,
                        metavar='YYYY-MM-DD',
                        help='''End date (inclusive) in ISO format YYYY-MM-DD''')

    parser.add_argument('--freq', type=int, default=15,
                        help='''Frequency at which to plot trajectories''')

    parser.add_argument('--days', type=int, default=5,
                        help='''Number of days over which to plot trajectories''')

    pa = parser.parse_args()

    # Check if path exists
    if pa.path and not os.path.exists(pa.path):
        err_msg = "Path {0} does not exist\n".format(pa.path)
        raise ValueError(err_msg)

    # Check if track file exists
    if pa.track and not os.path.exists(pa.track):
        err_msg = "File {0} does not exist\n".format(pa.track)
        raise ValueError(err_msg)

    # Check if output directory exists
    if pa.out and not os.path.isdir(pa.out):
        err_msg = "Path {0} is not a directory \n".format(pa.out)
        raise ValueError(err_msg)

    return pa


def plot_traj(path, out_dir, track_file=None, start_date=None, end_date=None, freq=15, days=5):

    data, metadata = read_data(path, start_date, end_date)

    fig, ax = plt.subplots(figsize=(9,9),
                           subplot_kw=dict(projection=ccrs.Orthographic(0, 90)))
    ax.coastlines(zorder=3)
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.gridlines()

    nday = len(data)
    depth = 4
    alpha = [math.exp(-x*depth/nday) for x in reversed(range(nday))]
    traj_hours = days*24
    dates = []
    traj_dt = None
    for i, df in enumerate(data):
        timestamp = metadata[i]['trajectory base time']
        traj_dt = dt.datetime.strptime(timestamp, '%Y%m%d%H')
        if i == 0:
            dates.append(traj_dt.strftime('%Y%m%d'))

        nclust = metadata[i]['number of clusters']
        if nclust > 1:
            raise NotImplementedError("Plotting multiple clusters not yet implemented")

        # Drop clustering level
        df = df.droplevel('CLUSTER')

        nread = len(df.groupby("READ"))
        periods = math.floor(nread/freq) if nread > freq else 1

        dt_index = pd.date_range(traj_dt.strftime('%Y%m%d %H:%M:%S'),
                                 periods=periods, freq=f"{freq}min")

        for ts in dt_index:
            try:
                traj = df.loc[ts]
            except KeyError:
                # timestamp not available
                continue

            # Get subset of data where P is non-negative and P > 980
            # and length of trajectory is less than specified number
            # of days
            ind0 = traj[traj['P (MB)'] > 0].index[0]
            ind1 = traj[traj['HOURS'] < -traj_hours].index[0]
            out_of_range = traj[(traj['P (MB)'] > 0) & (traj['P (MB)'] < 980)]
            if len(out_of_range) > 0:
                ind1 = min(ind1, out_of_range.index[0])

            # Plot trajectory between these points
            traj = traj.loc[ind0:ind1]
            plt.plot((traj.LON + 180) % 360 - 180, traj.LAT,
                     color='purple', alpha=alpha[i],
                     transform=ccrs.PlateCarree(),
                     )

    if i > 0:
        dates.append(traj_dt.strftime('%Y%m%d'))

    if track_file is not None:
        track_data = pd.read_csv(track_file, index_col='timestamp')
        track_data.columns = [x.lower() for x in track_data.columns]
        track_sub = track_data[::60]
        plt.plot(track_sub.longitude, track_sub.latitude,
                 color='black', alpha=1.0, linewidth=0, marker='o', markersize=1,
                 transform=ccrs.PlateCarree(),
                 )

    # Set map extent
    ax.set_extent([-180, 180, 60, 90], ccrs.PlateCarree())

    title = ' to '.join(dates)
    plt.title(title)

    file_name = '-'.join(dates) + '.png'
    if out_dir is not None:
        file_name = os.path.join(out_dir, file_name)

    plt.savefig(file_name)
    plt.close()


def main():

    args = parse_args()
    plot_traj(args.path,
              out_dir=args.out,
              track_file=args.track,
              start_date=args.start,
              end_date=args.end,
              freq=args.freq,
              days=args.days)


if __name__ == '__main__':
    main()
