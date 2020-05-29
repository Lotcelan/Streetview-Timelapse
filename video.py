import numpy as np
import glob, os, re, cv2

path = "" #Same as your save path in main.py
export_path = "./" #Export path of the video, "./" means video.py's current directory
export_name = "streetview_timelapse" #Name of the video file
FPS = 10 #Must be a number, amount of images per second (Tip : between 5 and 15 it'll be ok, after that the video can get really bad if there are too many left/rights...)

img_array = []

for filename in sorted(glob.glob(str(path) + "*.png"), key=lambda x:float(re.findall("(\d+)",x)[0])): #We're using the number in the names to sort them

    file_size = os.path.getsize(filename)
    if int(file_size) > 25000: #You'll ofently see 11 / 14 Ko files, wich are fails, so we get rid of them
        print("Processing {}. [SIZE] = {}".format(filename, file_size))
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)

    else:
        print("Image is probably bad :( : {} | {}".format(filename, file_size)) #The image is a fail



out = cv2.VideoWriter(export_path + export_name + ".avi",cv2.VideoWriter_fourcc(*'DIVX'), 10, size)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()
