# [Sound With Action](http://www.roboticsproceedings.org/rss16/p002.pdf)
![example](./img/dataset.gif)

Project Website: https://dhiraj100892.github.io/swoosh/
## System Dependanaices
- ffmpeg
```buildoutcfg
sudo apt-get install ffmpeg
```

## Python dependancies
```buildoutcfg
pip install -r requirement.txt
```

## DATA

#### Note:
Provide global path while running the python script in argument

### Download compressed data
```buildoutcfg
python download_data.py -d path_to_store_data -t type_of_data[small,complete]
```

### Uncompress the downloaded data
```buildoutcfg
python uncompress_data.py -dp path_to_store_uncmpressed_data -zp path_to_downloaded_data --rgb --data --depth --audio
```

### Create interaction dataset from uncompressed raw episodes
```buildoutcfg
python create_audio_dataset.py -d path_to_uncompressed_data -a path_to_store_dataset
```

### visualize the interaction dataset
- refer to [IPython Notebook](vis_interaction_dataset.ipynb)

