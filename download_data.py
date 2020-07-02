#!/usr/bin/env python

import os
import argparse

SMALL_DATASET = {'https://www.dropbox.com/sh/suckp4yrg8ho8ia/AACBYF58wDRU6N7lSQJ-kC0aa?dl=0' :'small_data.zip'}
COMPLETE_DATASET = {'https://www.dropbox.com/sh/msdj5z5cr6n3nnr/AABeGNRU-pnW2CZrRT29Ydc2a?dl=0' : 'ycb_object.zip',
                    'https://www.dropbox.com/sh/6u5w0dyzxjc1z2r/AAAwmfUK5EPjWmWvYOBFaWISa?dl=0' : 'ycb_object_2.zip',
                    'https://www.dropbox.com/sh/e8783xdw09ve32g/AAAoitXDFAWLN_TREp_ReAjTa?dl=0' : 'random.zip',
                    'https://www.dropbox.com/sh/yek8y09slxydifh/AACPveWqSGuGzp_UtIqVS2Cqa?dl=0' : 'random_1.zip',
                    'https://www.dropbox.com/sh/yek8y09slxydifh/AACPveWqSGuGzp_UtIqVS2Cqa?dl=0' : 'random_3.zip'}


def download_data(path, data_type):
    if data_type == 'small':
        data_link = SMALL_DATASET
    elif data_type == 'complete':
        data_link = COMPLETE_DATASET
    else:
        raise ValueError('type should be either "small" or "complete"')

    # make dir
    os.makedirs(path)

    # download data
    for link in data_link:
        cmd = 'wget {} -O {}'.format(link, os.path.join(path, data_link[link]))
        print("\nrunning cmd : {}".format(cmd))
        os.system(cmd)

    # unzip data
    for link in data_link:
        cmd = "unzip {} -d {}".format(os.path.join(path, data_link[link]), path)
        print("\nrunning cmd : {}".format(cmd))
        os.system(cmd)

    # remove zip file
    for link in data_link:
        cmd = "rm {}".format(os.path.join(path, data_link[link]))
        print("\nrunning cmd : {}".format(cmd))
        os.system(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_dir", type=str,
                        help='path for store data')
    parser.add_argument("-t", "--type", type=str, default='small',
                        help='type of data to be downloaded ["small", "complete"]')
    args, unknown = parser.parse_known_args()
    download_data(args.data_dir, args.type)


if __name__ == '__main__':
    main()