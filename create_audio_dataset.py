#!/usr/bin/env python

import os
import argparse
import multiprocessing
import copy

import numpy as np
from datetime import datetime
import pickle as pkl
import soundfile as sf

RGB_DIR = 'rgb'
DEPTH_DIR = 'depth'
DATA_DIR = 'data'
AUDIO_DIR = 'audio'
BASE_DATE = np.array([2019, 5, 1, 0, 0, 0, 0])

def make_dir(folder):
    if not os.path.exists(folder):
        print('Making directory: {}'.format(folder))
        os.makedirs(folder)
    else:
        print('Existing directory: {}'.format(folder))

def get_secs_from_file(file_name):
    date_str, ext = file_name.split('.')
    date_int = [int(i) for i in date_str.split('-')]
    file_datetime = datetime(*date_int)
    base_datetime = datetime(*BASE_DATE)
    file_seconds = (file_datetime - base_datetime).total_seconds()
    return file_seconds

def load_dir(img_dir):
    try:
        files = os.listdir(img_dir)
    except:
        return {}
    files = os.listdir(img_dir)
    files.sort(key = get_secs_from_file)
    total_time = get_secs_from_file(files[-1]) - get_secs_from_file(files[0])
    file_times = [get_secs_from_file(i) for i in files]
    n_imgs = len(files)
    return {'files' : files,
            'file_times' : np.array(file_times),
            'total_time' : total_time,
            'n': n_imgs,
            }

def load_data_dir(data_dir):
    '''
    This is assuming the newer data_dir format that has only one pickle file called data.pkl
    '''
    data_pkl_file = os.path.join(data_dir, 'data.pkl')
    exp_data = pkl.load(open(data_pkl_file, 'rb'), encoding='latin1')
    files = list(exp_data.keys())
    files.sort(key = get_secs_from_file)
    total_time = get_secs_from_file(files[-1]) - get_secs_from_file(files[0])
    file_times = [get_secs_from_file(i) for i in files]
    n = len(files)
    return {'files' : files,
            'file_times' : np.array(file_times),
            'total_time' : total_time,
            'n': n,
            'data': copy.deepcopy(exp_data),
            }

def find_closest(query_time, time_list, start_index=0):
    '''
    time_list should be a sorted numpy array
    '''
    diff_list = np.abs(time_list - query_time)
    last_val = len(diff_list)
    search_range = last_val - start_index
    closest_index = 0
    closest_value = np.inf
    for search_index in range(search_range):
        real_index = search_index + start_index
        if diff_list[real_index] < closest_value:
            closest_index = real_index
            closest_value = diff_list[real_index]
        elif diff_list[real_index] > closest_value:
            break
    return (closest_index, closest_value)

def sync_dirs(dir_a, dir_b):
    '''
    dir_a will remain constant. dir_b files will be synced to dir_a.
    '''
    if not dir_b:
        return {}
    dir_ba_files = []
    dir_b_time_list = dir_b['file_times']
    prev_index = 0
    for ind, file_time in enumerate(dir_a['file_times']):
        b_index, b_value = find_closest(file_time, dir_b_time_list, prev_index)
        dir_ba_files.append(dir_b['files'][b_index])
        prev_index = b_index
    dir_ba = copy.deepcopy(dir_b)
    dir_ba['files'] = dir_ba_files
    dir_ba['file_times'] = [get_secs_from_file(i) for i in dir_ba_files]
    dir_ba['total_time'] = get_secs_from_file(dir_ba_files[-1]) - get_secs_from_file(dir_ba_files[0])
    dir_ba['n'] = len(dir_ba_files)
    return dir_ba

def create_audio_experiment(exp_path, audio_exp_path, args):
    rgb_dir = os.path.join(exp_path, RGB_DIR)
    depth_dir = os.path.join(exp_path, DEPTH_DIR)
    data_dir = os.path.join(exp_path, DATA_DIR)
    audio_dir = os.path.join(exp_path, AUDIO_DIR)

    rgb_files = load_dir(rgb_dir)
    depth_files = load_dir(depth_dir)
    data_files = load_data_dir(data_dir)
    audio_files = load_dir(audio_dir)

    root_files = rgb_files
    rgb_synced_files = copy.deepcopy(rgb_files)
    depth_synced_files = sync_dirs(root_files, depth_files)
    data_synced_files = sync_dirs(root_files, data_files)
    data_synced_files['data'] = data_files['data']
    audio_synced_files = sync_dirs(root_files, audio_files)

    audio_file = audio_synced_files['files'][0]
    audio_start_time = audio_synced_files['file_times'][0]


    audio_full_file = os.path.join(audio_dir, audio_file)
    print('Loading audio file: {}'.format(audio_full_file))
    audio_data, audio_samplerate = sf.read(audio_full_file)

    audio_eps = args.audio_eps
    event_h_len = args.event_h_len
    audio_da = np.abs(audio_data).max(1)
    audio_da_idx = np.where(audio_da>audio_eps)[0]
    exp_no = 0
    prev_time = -np.inf
    for idx in audio_da_idx:
        idx_time = audio_start_time + float(idx)/audio_samplerate
        idx_st = idx_time - event_h_len
        idx_en = idx_time + event_h_len
        audio_st = int((idx_st-audio_start_time)*audio_samplerate)
        audio_en = int((idx_en-audio_start_time)*audio_samplerate)
        if audio_st<=prev_time:
            continue
        prev_time = audio_en
        rgb_st_idx, _ = find_closest(idx_st, rgb_synced_files['file_times'])
        rgb_en_idx, _ = find_closest(idx_en, rgb_synced_files['file_times'], rgb_st_idx)
        exp_dir = os.path.join(audio_exp_path, str(exp_no))
        rgb_exp_dir = os.path.join(exp_dir, 'rgb')
        data_exp_path = os.path.join(exp_dir, 'audio_data.pkl')
        make_dir(rgb_exp_dir)
        exp_data = []
        for rgb_rel_idx in range(rgb_en_idx-rgb_st_idx+1):
            rgb_idx = rgb_rel_idx + rgb_st_idx
            src_img = os.path.join(rgb_dir, rgb_synced_files['files'][rgb_idx])
            dest_img = os.path.join(rgb_exp_dir, rgb_synced_files['files'][rgb_idx])
            os.symlink(src_img, dest_img)
            data_fname = data_synced_files['files'][rgb_idx]
            data_info = data_synced_files['data'][data_fname]
            exp_data.append(data_info)
        audio_exp_data = {
                'audio': audio_data[audio_st:audio_en],
                'data': exp_data,
                'audio_samplerate': audio_samplerate
                }
        pkl.dump(audio_exp_data, open(data_exp_path,'wb'))
        exp_no += 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_dir", type=str,
            help='tray data directory')
    parser.add_argument("-a", "--audio_dir", type=str,
            help='audio dataset directory')
    parser.add_argument("-np", "--n_proc", type=int, default=1,
            help='Number of prcoesses')
    parser.add_argument("-ae", "--audio_eps", type=float, default=0.1,
            help='Audio thresholding value 0-1')
    parser.add_argument("-ehl", "--event_h_len", type=float, default=2.0,
            help='Half length of storing event')
    # parser.add_argument('--rgb', help='copy RGB',
    #     action='store_true')
    # parser.add_argument('--data', help='copy data',
    #     action='store_true')
    # parser.add_argument('--depth', help='copy depth',
    #     action='store_true')
    # parser.add_argument('--symlink', help='symlink or copy',
    #     action='store_true')
    args, unknown = parser.parse_known_args()
    pool = multiprocessing.Pool(processes=args.n_proc)

    tray_data_dir = args.data_dir
    audio_tray_data_dir = args.audio_dir

    make_dir(audio_tray_data_dir)

    object_list = os.listdir(tray_data_dir)
    for obj in object_list:
        object_path = os.path.join(tray_data_dir, obj)
        audio_object_path = os.path.join(audio_tray_data_dir, obj)
        make_dir(audio_object_path)
        exp_list = os.listdir(object_path)
        for exp in exp_list:
            exp_path = os.path.join(object_path, exp)
            audio_exp_path = os.path.join(audio_object_path, exp)
            #create_audio_experiment(exp_path, audio_exp_path, args)

            pool.apply_async(create_audio_experiment, args=(exp_path, audio_exp_path, args,))

    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
