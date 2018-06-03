from datetime import datetime
import os
import argparse
parser = argparse.ArgumentParser(description='Copy with converting video name.')
parser.add_argument('-f', '--folder',
                    help='an integer for the accumulator')

args = parser.parse_args()
DATE_FORMAT1 = '%Y-%m-%d-%H-%M-%S'
DATE_FORMAT2 = 'yanosik_%d-%m-%Y %H_%M_%S.mp4'
DATE_FORMAT_FOR_FOLDER = '%Y-%m-%d'
STORAGE = "F:\DCIM"
full_path = r"C:\Users\kuba\Desktop\sensor data\temp"
DEST_PATH = r"C:\Users\kuba\Desktop\sensor data"
folder_name = "videos_2018-05-16"
#full_path = os.path.join(STORAGE, args.folder)
for file in os.listdir(full_path):
    #date_created = datetime.fromtimestamp(os.path.getctime(os.path.join(full_path,file))).strftime(DATE_FORMAT)
    #date_for_folder_name= datetime.fromtimestamp(os.path.getctime(os.path.join(full_path, file))).strftime(DATE_FORMAT_FOR_FOLDER)
   # folder_name = os.path.join(DEST_PATH, "videos_" + date_for_folder_name)
   # if not os.path.exists(folder_name):
    #    os.mkdir(folder_name)
    date_created = datetime.strptime(os.path.basename(file), DATE_FORMAT2).strftime(DATE_FORMAT1)
    new_file_name = "video_{date_created}.mp4".format(**locals())
    os.rename(os.path.join(full_path,file),
              os.path.join(DEST_PATH,folder_name, new_file_name))