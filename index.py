# -*- coding: utf-8 -*-
from cv2 import cv2
from os import listdir
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml

# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
cp = c['positions']
numberOfScreenshots = c['numberOfScreenshots']
initialDelay = c['initialDelay']
timeBetweenActions = c['timeBetweenActions']
screenshotPosition = c['screenshotPosition']


def moveToWithRandomness(x, y, t):
    pyautogui.moveTo(x*cp["percentageX"], y*cp["percentageY"], t)


def remove_suffix(input_string, suffix):
    """Returns the input_string without the suffix"""

    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def load_images(dir_path='./targets/'):
    """ Programatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix

    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


def show(rectangles, img=None):
    """ Show an popup with rectangles showing the rectangles[(x, y, w, h),...]
        over img or a printSreen if no img provided. Useful for debugging"""

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


def clickBtn(img, timeout=3, threshold=0.9):
    """Search for img in the scree, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)
        if(len(matches) == 0):
            has_timed_out = time.time()-start > timeout
            continue
        x, y, w, h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        moveToWithRandomness(pos_click_x, pos_click_y, 1)
        pyautogui.click()
        return True

    return False


def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        img = sct_img[:, :, :3]
        return img


def positions(target, threshold=0.9, img=None):
    if img is None:
        img = printSreen()

    print(img)
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

    return rectangles


def nextPage():
    if(page == 1):
        clickBtn(images['nextpage'])
    else:
        pyautogui.click()


def saveScreenshot():
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {"top": screenshotPosition["top"], "left": screenshotPosition["left"],
                   "width": screenshotPosition["width"], "height": screenshotPosition["height"]}
        output = "screenshots/page"+str(page)+".png".format(**monitor)

        # Grab the data
        sct_img = sct.grab(monitor)

        # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        print(output)


def main():
    """Main execution setup and loop"""
    # ==Setup==
    global images, page
    images = load_images()
    page = 1
    time.sleep(initialDelay)
    while page <= numberOfScreenshots:
        saveScreenshot()
        time.sleep(timeBetweenActions)
        nextPage()
        page = page+1
        time.sleep(timeBetweenActions)
        sys.stdout.flush()


if __name__ == '__main__':
    main()
