#!/usr/bin/env python
import shutil
import os
import pickle
import argparse
import multiprocessing

def make_dir(folder):
    if not os.path.exists(folder):
        print('Making directory: {}'.format(folder))
        os.makedirs(folder)
    else:
        print('Existing directory: {}'.format(folder))

def uncompress_audio(src, dest, copy_flag=False):
    if copy_flag==True:
        if os.path.exists(dest):
            return
        make_dir(dest)
        af_name = os.listdir(src)[-1].split('.')[0].split('_')[0]
        af = af_name+'.wav'
        af_mp3_list = [af_name+'_{}.mp3'.format(a) for a in range(4)]
        ## Order is somehow interchanged
        os.system('ffmpeg -i {} -i {} -i {} -i {} -filter_complex "[0:a][1:a][2:a][3:a]join=inputs=4:channel_layout=4.0[a]" -map "[a]" {}'.format(
        os.path.join(src,af_mp3_list[2]),
        os.path.join(src,af_mp3_list[0]),
        os.path.join(src,af_mp3_list[1]),
        os.path.join(src,af_mp3_list[3]),
        os.path.join(dest,af)
        ))

def uncompress_data(src, dest, copy_flag=False):
    if copy_flag==True:
        if os.path.exists(dest):
            return
        make_dir(dest)
        shutil.rmtree(dest)
        shutil.copytree(src, dest)

def uncompress_images(src, dest, extension='png', frame_rate=30, copy_flag=False):
    if copy_flag==True:
        if os.path.exists(dest):
            return
        make_dir(dest)
        frame_correspondence = pickle.load(open(os.path.join(src,'correspondence.pkl'), "rb"))
        vid_image_dir = os.path.join(dest)
        make_dir(vid_image_dir)
        os.system('ffmpeg -i {} -q:v 1 -qmin 1 -qmax 1 {}/file%07d.{}'.format(
            os.path.join(src,'video.mp4'),
            vid_image_dir,
            extension,
            ))
        for index in range(len(frame_correspondence)):
            frame_path = os.path.join(vid_image_dir, frame_correspondence[index][0])
            image_path = os.path.join(vid_image_dir, frame_correspondence[index][1])
            os.rename(frame_path, image_path)

def copy_experiment(zip_exp_path, exp_path, args):
    zip_rgb_dir = os.path.join(zip_exp_path, RGB_DIR)
    zip_depth_dir = os.path.join(zip_exp_path, DEPTH_DIR)
    zip_data_dir = os.path.join(zip_exp_path, DATA_DIR)
    zip_audio_dir = os.path.join(zip_exp_path, AUDIO_DIR)

    rgb_dir = os.path.join(exp_path, RGB_DIR)
    depth_dir = os.path.join(exp_path, DEPTH_DIR)
    data_dir = os.path.join(exp_path, DATA_DIR)
    audio_dir = os.path.join(exp_path, AUDIO_DIR)


    uncompress_audio(zip_audio_dir, audio_dir, copy_flag=args.audio)
    uncompress_data(zip_data_dir, data_dir, copy_flag=args.data)
    uncompress_images(zip_rgb_dir, rgb_dir, extension='jpg', copy_flag=args.rgb)
    uncompress_images(zip_depth_dir, depth_dir, extension='png', copy_flag=args.depth)

TRAY_DATA_PATH = '/home/lerrel/tray_data_exp_uncompressed'
ZIP_TRAY_DATA_PATH = '/home/lerrel/zip_tray_data'
RGB_DIR = 'rgb'
DEPTH_DIR = 'depth'
DATA_DIR = 'data'
AUDIO_DIR = 'audio'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dp", "--data_path", type=str, default=TRAY_DATA_PATH,
        help='Path to tray data to compress')
    parser.add_argument("-zp", "--zip_path", type=str, default=ZIP_TRAY_DATA_PATH,
        help='Path to compressed directory')
    parser.add_argument("-np", "--n_proc", type=int, default=1,
        help='Number of prcoesses')
    parser.add_argument('--rgb', help='unzip RGB',
        action='store_true')
    parser.add_argument('--data', help='unzip data',
        action='store_true')
    parser.add_argument('--depth', help='unzip depth',
        action='store_true')
    parser.add_argument('--audio', help='unzip audio',
        action='store_true')
    args, unknown = parser.parse_known_args()
    pool = multiprocessing.Pool(processes=args.n_proc)
    tray_data_path = args.data_path
    zip_tray_data_path = args.zip_path
    make_dir(tray_data_path)

    object_list = os.listdir(zip_tray_data_path)
    for obj in object_list:
        object_path = os.path.join(tray_data_path, obj)
        zip_object_path = os.path.join(zip_tray_data_path, obj)
        make_dir(object_path)
        exp_list = os.listdir(zip_object_path)
        for exp in exp_list:
            zip_exp_path = os.path.join(zip_object_path, exp)
            exp_path = os.path.join(object_path, exp.split('.')[0])

            pool.apply_async(copy_experiment, args=(zip_exp_path,exp_path,args,))
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
