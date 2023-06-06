#!/usr/bin/env python3
"""
Author : Emmanuel Gonzalez 
Date   : 2021-08-08
Purpose: TGI extraction of plot clipped images (drone and gantry)
"""

import argparse
import os
import sys
import rasterio
import numpy as np
import glob
import matplotlib.pyplot as plt
import cv2
import tifffile as tifi
import pandas as pd
import geopandas as gpd
import multiprocessing
import re
from datetime import datetime


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='TGI extraction',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dir',
                        metavar='dir',
                        help='Directory containing plot clipped TIFF images.')

    parser.add_argument('-o',
                        '--outdir',
                        help='Output directory.',
                        metavar='str',
                        type=str,
                        default='tgi_extraction_out')

    parser.add_argument('-f',
                        '--fieldbook',
                        help='Fieldbook for the season used to append treatment.',
                        metavar='str',
                        type=str)

    return parser.parse_args()


# --------------------------------------------------
def get_paths(directory):

    ortho_list = []

    for root, dirs, files in os.walk(directory):
        for name in files:
            if '.tif' in name:
                ortho_list.append(os.path.join(root, name))

    if not ortho_list:

        raise Exception(f'ERROR: No compatible images found in {directory}.')


    print(f'Images to process: {len(ortho_list)}')

    return ortho_list


# --------------------------------------------------
def create_tgi(r_band, g_band, b_band):
    
    tgi = (g_band.astype(float)-(0.39*r_band.astype(float))-(0.61*b_band.astype(float)))

    return tgi


# --------------------------------------------------
def get_stats(img):
    
    img = img[~np.isnan(img)]

    mean = np.mean(img) #- 273.15
    median = np.percentile(img, 50)

    q1 = np.percentile(img, 25)
    q3 = np.percentile(img, 75)

    var = np.var(img)
    sd = np.std(img)

    return mean, median, q1, q3, var, sd


# --------------------------------------------------
def collect_tgi(plot):
    
    green_dict = {}
    cnt = 0
    
    cnt += 1

    img = tifi.imread(plot)
    r, g, b, _ = cv2.split(img)

    tgi = create_tgi(r_band=r, g_band=g, b_band=b)

    tgi[tgi < 0] = np.nan

    mean, median, q1, q3, var, sd = get_stats(tgi)
    plot_num = plot.split('/')[-2]
    test = plot.split('/')[-1].split('_')[:3]
    # date = '-'.join(test)

    green_dict[cnt] = {
        'date': date,
        'plot': plot_num,
        'mean_tgi': mean,
        'median_tgi': median,
        'q1_tgi': q1,
        'q3_tgi': q3,
        'var_tgi': var,
        'sd_tgi': sd
    }
    
    df = pd.DataFrame.from_dict(green_dict, orient='index')
    
    return df


# --------------------------------------------------
def add_fieldbook_data(df, fb_df):
    
    fb_df.columns = fb_df.columns.str.lower()
    fb_df = fb_df.set_index('plot')#.drop(drop_list, axis=1)
    out_df = fb_df.join(df)
    
    return out_df


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    try:
        match = re.search(r'\d{4}-\d{2}-\d{2}', args.dir)
        global date
        date = datetime.strptime(match.group(), '%Y-%m-%d').date()
    
    except:
        print('Error: Cannot find scan/flight date. Make sure input directory has a date in the following format YYYY-MM-DD.')

    plot_list = get_paths(args.dir)
    df = pd.DataFrame()

    with multiprocessing.Pool(multiprocessing.cpu_count()-1) as p:

        tgi_df = p.map(collect_tgi, plot_list)
        df = df.append(tgi_df)

    df = df.set_index('plot')

    if args.fieldbook: 

        fb_df = pd.read_csv(args.fieldbook, dtype='str')
        df = add_fieldbook_data(df, fb_df)

    df = df.loc[:, ~df.columns.str.contains('named:')]
    df.to_csv(os.path.join(args.outdir, f'{date}_tgi_extraction.csv'))


# --------------------------------------------------
if __name__ == '__main__':
    main()
