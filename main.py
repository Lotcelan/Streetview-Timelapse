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
#   You can also use a tool such as Flowframes to smooth the video :D
#----------------------------------------------------

import subprocess, time, requests, json, math, logging, os #Subprocess : Chrome command | time : time | requests/json : itinerary API | math : maths | logging : logging
from concurrent.futures import ThreadPoolExecutor #Threading
from selenium import webdriver  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning("Started")



#-------------------- CHANGE THIS -------------------

save_path = "C:/Path/To/images/" #Insert your path (full path, not relative) to save images USING FORWARD SLASHES (E.g : C:/Users/Username/Desktop/images/)
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe" #Path to google chrome.exe
chrome_driver_path = "D:/Dev/Python/StreetViewClean/chromedriver.exe"
key = "" #Get your MapQuest key : https://developer.mapquest.com/user/me/apps

fromPlace = "" #The starting point : Address City Country
toPlace = "e" #The ending point : Address City Country

MAX_THREAD = 8 #Change this (Tip : from 5 to 15 it's ok, after that your PC will lag, a lot)
DELAY = 5 #We found that it was the best time, but if you get blank/black images change this

# Not implemented yet :
SAVE_FILE_NAME = "progress.save"
SAVE_PROGRESS = True # If set to true, will create a save file containing the last route and where all threads left off
USE_PROGRESS_IF_PRESENT = True # Will override the "fromPlace" and "toPlace" if a save file is present at the root directory of the python file

#----------------------------------------------------


def getNewDriver(chrome_path, chrome_driver_path, chrome_options):
    driver = webdriver.Chrome(
                executable_path=chrome_driver_path,
                chrome_options=chrome_options
                )
    return driver


def process_images(sub_coords, sub_id, starting_index, angle_mode, coords, size="1920,1080"):
    chrome_options = Options()  
    opts = ['--allow-running-insecure-content',
            '--ignore-certificate-errors',
            '--ignore-urlfetcher-cert-requests',
            '--reduce-security-for-testing',
            '--headless',
            '--window-size=' + size,
            '--disable-gpu',
            '--run-all-compositor-stages-before-draw'
            ]
    for i in opts:
        chrome_options.add_argument(i)
    chrome_options.binary_location = chrome_path
    driver = getNewDriver(chrome_path, chrome_driver_path, chrome_options)
    driver.get('https://maps.google.com')
    time.sleep(2)

    button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Tout accepter']")
    button.click()

    print(f"Thread {sub_id} ready !")
    
    name_idx = starting_index

    for i in range(len(sub_coords)):
        if angle_mode == "smooth":
            angle = 0
            if i == 0:
                if sub_id == 0:
                    # We're at the very beginning, so can not be "smooth"
                    angle = getangle(sub_coords[i], coords[i + 1]) #Gets angle between the actual point and the next one
                else:
                    # We can get the last of the previous sub list
                    angle = getangle(coords[starting_index - 1], sub_coords[i+1])
            elif i == len(sub_coords) - 1:
                if sub_id == MAX_THREADS-1:
                    # We're at the very end, do nothing (TODO : look toward objective)
                    pass
                else:
                    # We can get the first of the next sub list
                    angle = getangle(sub_coords[i-1], coords[staring_index + len(sub_coords)])
                    
            else:
                # General case
                angle = getangle(sub_coords[i-1], sub_coords[i+1])
            get_image(str(name_idx) + ".png", make_url(sub_coords[i], rot=str(angle)), driver)
            name_idx += 1
        # TODO : Sharp (but ugly so not doing now) 

    driver.execute_script("window.location.href = 'about:blank'")
    driver.quit()


def get_image(path, url, driver):
    logging.warning("Processing : [File name] = {}; [URL] = {} !".format(path, url))
    #It uses chrome headless mode to take screenshots
    try:
        success = False
        images_tries = 0
        logging.warning("Processing : [File name] = {}; [URL] = {} !".format(path, url))

        while success != True:
            driver.execute_script("window.location.href = '" + str(url) + "'")
            time.sleep(DELAY)
            driver.save_screenshot(save_path+path)
            file_size = os.path.getsize(save_path+path)

            if file_size <= 200000 and images_tries <= 5:
                os.remove(save_path+path)
                images_tries += 1
            else:
                
                success = True
        print("Query done.")
    except Exception as e:
        logging.warning("Got an error while processing Processing : [File name] = {}; [URL] = {} ! ===> {}".format(path, url, e))
    
    return

def make_url(coords, layer="c", map_ar="11", rot="0", tilt="0", zoom="0", pitch="0"):
    return "https://maps.google.com/maps?q=&layer={}&cbll={},{}&cbp={},{},{},{},{}".format(layer, coords[0], coords[1],map_ar, rot, tilt, zoom, pitch)


def getangle(ptA, ptB):
    #To get the angle (rotation) between two points to face the next point
    vector_c = (ptB[0] - ptA[0], ptB[1] - ptA[1])
    r = math.degrees(  math.atan2(vector_c[1],vector_c[0]))
    return r

def split_list_into_sublists(input_list, num_sublists):
    sublist_length = len(input_list) // num_sublists
    sublists = []
    starting_indices = []

    for i in range(0, len(input_list), sublist_length):
        sublist = input_list[i:i + sublist_length]
        sublists.append(sublist)
        starting_indices.append(i)

    # Ensure all elements are distributed among sublists
    while len(sublists) > num_sublists:
        last_sublist = sublists.pop()
        sublists[-1].extend(last_sublist)

    return sublists, starting_indices


def main():
    coords = []
    #Api for itinerary
    url = "https://www.mapquestapi.com/directions/v2/route?key={}&from={}&to={}&fullShape=true&shapeFormat=raw&avoids=Tunnel".format(key, fromPlace, toPlace)
    r = requests.get(url)
    result = r.json()

    logging.warning("Response of route api : \n{}".format(result))

    try:
        print("Amount of points : {}".format(len(result["route"]["shape"]["shapePoints"])//2))

        for i in range(0, len(result["route"]["shape"]["shapePoints"]), 2):
            #for debugging : print("Len : {} - Processing : {} and {}".format(len(result["route"]["shape"]["shapePoints"]),result["route"]["shape"]["shapePoints"][i], result["route"]["shape"]["shapePoints"][i + 1]))
            coords.append((result["route"]["shape"]["shapePoints"][i], result["route"]["shape"]["shapePoints"][i + 1]))
    #Creates a list of tuples of coordinates (look at the API's doc to understand the result)
    except Exception as e:
        logging.warning("Got an error : the route probably doesn't exist")
        print("y'a pas")
        print(e)
        return
    
    logging.warning("Coords :\n{}".format(coords))
    pool = ThreadPoolExecutor(max_workers=MAX_THREAD) #To avoid crashing your PC by spamming threads

    angle_mode = "smooth" #CHANGE THIS (if you want) It can either be smooth or sharp

    sublists, starting_indices = split_list_into_sublists(coords, MAX_THREAD)

    i = 0
    for (sub_coords, start_idx) in zip(sublists, starting_indices):
        pool.submit(process_images, sub_coords, i, start_idx, angle_mode, coords)
        i += 1

    pool.shutdown(wait=True)


if __name__ == "__main__":
    main() #Start !
