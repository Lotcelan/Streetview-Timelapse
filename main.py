# Resources :
# https://www.google.fr/maps/            https://github.com/schnerd/chrome-headless-screenshots       http://web.archive.org/web/20110903160743/http://mapki.com/wiki/Google_Map_Parameters#Street_View          https://stackoverflow.com/questions/387942/google-street-view-url
# https://stackoverflow.com/questions/16326143/google-maps-directions-api-equivalent-url

#-------------------- DISCLAIMER / INFO--------------
#   This project was made for fun and isn't
#   optimized AT ALL. Feel free to contact me
#   for questions/improvments.
#   Also we are not responsible for any damage
#   you can cause with this (computer crashing,
#   IP ban from google, etc...).
#   Finally we are aware of some bugs, we guess
#   that they come from the threading or chrome's
#   headless mode, and we did'nt find a solution.
#   What that it means is that threads can go endless
#   and you'll have to kill the program to end it.
#   Also run "taskkill /f /im chrome.exe" after running
#   this program (look at yout task manager :))
#----------------------------------------------------

#-------------------- HOW TO USE --------------------
#   Change the values below to mactch what you want.
#   Once the images are rendered, you can transform
#   those images into a video with video.py.
#   There you just have to link your images directory
#   and it will create a video !
#----------------------------------------------------

import subprocess, time, requests, json, math, logging #Subprocess : Chrome command | time : time | requests/json : itinerary API | math : maths | logging : logging
from concurrent.futures import ThreadPoolExecutor #Threading

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning("Started")



#-------------------- CHANGE THIS -------------------

save_path = "" #Insert your path (full path, not relative) to save images USING FORWARD SLASHES (E.g : C:/Users/Username/Desktop/images/)
chrome_path = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe" #Path to google chrome.exe
key = "" #Get your MapQuest key : https://developer.mapquest.com/user/me/apps

fromPlace = "" #The starting point : Address City Country
toPlace = "" #The ending point : Address City Country

MAX_THREAD = 8 #Change this (Tip : from 5 to 15 it's ok, after that your PC will lag, a lot)
VIRTUAL_TIME_BUDGET = 10000 #We found that it was the best time, but if you get blank/black images change this

#----------------------------------------------------

def get_image(path, url, size="1920,1080"):
    logging.warning("Processing : [File name] = {}; [Size] = {}; [URL] = {} !".format(path, size, url))
    #It uses chrome headless mode to take screenshots
    exec_query = subprocess.run([str(chrome_path), "--headless", "--disable-gpu", "--window-size=" + str(size), "--screenshot=" + str(save_path) + str(path), str(url), "--virtual-time-budget="+str(VIRTUAL_TIME_BUDGET)])
    print("Query done.")


def make_url(coords, layer="c", map_ar="11", rot="0", tilt="0", zoom="0", pitch="0"):
    return "https://maps.google.com/maps?q=&layer={}&cbll={},{}&cbp={},{},{},{},{}".format(layer, coords[0], coords[1],map_ar, rot, tilt, zoom, pitch)


def getangle(ptA, ptB):
    #To get the angle (rotation) between two points to face the next point
    vector_c = (ptB[0] - ptA[0], ptB[1] - ptA[1])
    r = math.degrees(  math.atan2(vector_c[1],vector_c[0]))
    return r



def main():
    coords = []
    #Api for itinerary
    url = "http://www.mapquestapi.com/directions/v2/route?key={}&from={}&to={}&fullShape=true&shapeFormat=raw".format(key, fromPlace, toPlace)
    r = requests.get(url)
    result = r.json()

    logging.warning("Response of route api : \n{}".format(result))

    print("Amount of points : {}".format(len(result["route"]["shape"]["shapePoints"])))

    for i in range(0, len(result["route"]["shape"]["shapePoints"]), 2):
        #for debugging : print("Len : {} - Processing : {} and {}".format(len(result["route"]["shape"]["shapePoints"]),result["route"]["shape"]["shapePoints"][i], result["route"]["shape"]["shapePoints"][i + 1]))
        coords.append((result["route"]["shape"]["shapePoints"][i], result["route"]["shape"]["shapePoints"][i + 1]))
    #Creates a list of tuples of coordinates (look at the API's doc to understand the result)

    logging.warning("Coords :\n{}".format(coords))
    index = 0 #For names
    pool = ThreadPoolExecutor(max_workers=MAX_THREAD) #To avoid crashing your PC by spamming threads

    angle_mode = "smooth" #CHANGE THIS (if you want) It can either be smooth or sharp

    if angle_mode == "smooth":
        
        for i in range(1, len(coords) - 1):

            angle = getangle(coords[i - 1], coords[i + 1]) #Gets angle between the actual point and the next one
            pool.submit(get_image, "test_directionNice_" + str(index) + "_rot=" + str(angle) + ".png",make_url(coords[i], rot=str(angle)))
            index += 1

    elif angle_mode == "sharp":

            for i in range(len(coords) - 1):

                angle = getangle(coords[i], coords[i + 1]) #Gets angle between the actual point and the next one
                pool.submit(get_image, "test_directionNice_" + str(index) + "_rot=" + str(angle) + ".png",make_url(coords[i], rot=str(angle)))
                index += 1
            

    pool.shutdown(wait=True)


if __name__ == "__main__":
    main() #Start !
