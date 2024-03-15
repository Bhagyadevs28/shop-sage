import re
import time
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from roboflow import Roboflow
import cv2
import ctypes


def get_screen_resolution():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def get_test_pic():
    url = 'https://www.makemytrip.com/flight/search?itinerary=BOM-DEL-02/02/2024&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&ccde=IN&lang=eng'

    # Use Edge browser
    driver = webdriver.Edge()

    # Maximize the browser window to make it full-screen
    driver.maximize_window()

    driver.get(url)

    # You don't need an implicit wait here, as WebDriverWait will handle the waiting for you

    # Set up a WebDriverWait with a timeout (in seconds)
    wait = WebDriverWait(driver, 20)

    # Define the regex pattern you're looking for
    pattern = r'flight'

    # Use WebDriverWait to wait until the element is present with the specified regex pattern
    span_element = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//span[contains(text(), '{pattern}')]")))

    # Define the regex pattern
    regex_pattern = re.compile(r'Now Lock Prices & Pay Later', re.IGNORECASE)

    # Wait for the div with the specified regex pattern
    # div_element = WebDriverWait(driver, 100).until(
    #     EC.presence_of_element_located(
    #         (By.XPATH, f"//div[contains(text(), '{regex_pattern.pattern}')]"))
    # )
    ok_button = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'OK')]"))
    )

    # Assuming there is a button with text "OK" associated with the div, locate and click it
    # ok_button = div_element.find_element(
    #     By.XPATH, "./following-sibling::button[text()='OK']")
    if ok_button is not None:
        ok_button.click()

    # # Get the total height of the webpage
    total_height = driver.execute_script(
        "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
    # print(total_height)
    # Set the window size to the full height
    # driver.set_window_size(driver.get_window_position()['x'], 0)  # Set the width to the current width
    # driver.set_window_size(driver.get_window_size()['width'],total_height)

    # Wait for a brief moment to allow content to load
    # time.sleep(2)
    screen_height = driver.get_window_size()['height']
    iterations = total_height//screen_height
    print(iterations)
    # Iterate through the page and take screenshots
    for i in range(iterations + 1):
        # Scroll down the webpage
        sloc = i * screen_height
        eloc = (i + 1) * screen_height
        driver.execute_script(f'window.scrollTo({sloc}, {eloc});')

        # Wait for a brief moment to allow content to load (you may need to adjust the duration)
        time.sleep(2)

        # Save the screenshot
        driver.save_screenshot(f"log/test_{i}.png")

    # Reset the window size to its original dimensions
    # driver.set_window_size(driver.get_window_position()['x'], driver.get_window_position()['y'])
    # driver.set_window_size(driver.get_window_size()['width'], driver.get_window_size()['height'])

    # Write the page source to an HTML file
    with open('log/test.html', "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    # Close the browser
    driver.quit()


def predict_from_pic():
    VERSION = 7
    rf = Roboflow(api_key="Q0yexfUhhIiHyRVmtvHa")
    project = rf.workspace("anandu-p-r-aum2x").project("object-extraction")
    model = project.version(VERSION).model

    # infer on a local image
    data = model.predict("log/test_0.png", confidence=30,
                         overlap=30).json()['predictions']

    # Save data to a JSON file
    with open("log/data.json", "w") as json_file:
        json.dump(data, json_file)

    # print("\n")
    # for bbox in bboxs:
    #     print(bbox)
    # print("\n")

    # visualize your prediction
    model.predict("log/test_0.png", confidence=20, overlap=30).save("prediction.jpg")

    # infer on an image hosted elsewhere
    # print(model.predict("URL_OF_YOUR_IMAGE", hosted=True, confidence=40, overlap=30).json())

predict_from_pic()


# data = [{'x': 816, 'y': 607, 'width': 879, 'height': 74, 'confidence': 0.9664953351020813, 'class': 'flight', 'class_id': 0, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 813, 'y': 489, 'width': 877, 'height': 151, 'confidence': 0.9551639556884766, 'class': 'flight', 'class_id': 0, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 813, 'y': 312, 'width': 893, 'height': 187, 'confidence': 0.9333680868148804, 'class': 'flight', 'class_id': 0, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 757, 'y': 615, 'width': 168, 'height': 59, 'confidence': 0.8583022356033325, 'class': 'flightDuration', 'class_id': 5, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 1077, 'y': 608, 'width': 70, 'height': 46, 'confidence': 0.8299617767333984, 'class': 'flightPrice', 'class_id': 7, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 821, 'y': 165, 'width': 877, 'height': 96, 'confidence': 0.8257793188095093, 'class': 'flight', 'class_id': 0, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 921, 'y': 601, 'width': 51, 'height': 27, 'confidence': 0.8127356767654419, 'class': 'flightArrivalTime', 'class_id': 2, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 921, 'y': 443, 'width': 51, 'height': 25, 'confidence': 0.8074585795402527, 'class': 'flightArrivalTime', 'class_id': 2, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 1078, 'y': 453, 'width':
# 67, 'height': 45, 'confidence': 0.80356365442276, 'class': 'flightPrice', 'class_id': 7, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 921, 'y': 252, 'width': 51, 'height': 27, 'confidence': 0.7856325507164001, 'class': 'flightArrivalTime', 'class_id': 2, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 759, 'y': 459, 'width': 144, 'height': 59, 'confidence': 0.7604001760482788, 'class': 'flightDuration', 'class_id': 5, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 590, 'y': 252, 'width': 51, 'height': 25, 'confidence': 0.7362315654754639, 'class': 'flightDepartureTime', 'class_id': 4, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 758, 'y': 269, 'width': 146, 'height': 61, 'confidence': 0.6953635215759277, 'class': 'flightDuration', 'class_id': 5, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 1078, 'y': 261, 'width': 67, 'height': 45, 'confidence': 0.6765983700752258, 'class': 'flightPrice', 'class_id': 7, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 934, 'y': 136, 'width': 53, 'height': 25, 'confidence': 0.6711810231208801, 'class': 'flightArrivalTime', 'class_id': 2, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 445, 'y': 455, 'width': 133, 'height': 56, 'confidence': 0.6684551239013672, 'class': 'flightName', 'class_id': 6, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 587, 'y': 470, 'width': 47, 'height': 15, 'confidence': 0.6166021823883057, 'class': 'flightDeparturePlace', 'class_id': 3, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 590,
# 'y': 444, 'width': 51, 'height': 24, 'confidence': 0.6007795333862305, 'class': 'flightDepartureTime', 'class_id': 4, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 587, 'y': 279, 'width': 47, 'height': 16, 'confidence': 0.5973087549209595, 'class': 'flightDeparturePlace', 'class_id': 3, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 590, 'y': 601, 'width': 51, 'height': 25, 'confidence': 0.5662532448768616, 'class': 'flightArrivalTime', 'class_id': 2, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 1077, 'y': 143, 'width': 70, 'height': 45, 'confidence': 0.5612732768058777, 'class': 'flightPrice', 'class_id': 7, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 918, 'y': 279, 'width': 61, 'height': 20, 'confidence': 0.5189711451530457, 'class': 'flightArrivalPlace', 'class_id': 1, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 444, 'y': 265, 'width': 135, 'height': 60, 'confidence': 0.5121964812278748, 'class': 'flightName', 'class_id': 6, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 917, 'y': 470, 'width': 59, 'height': 17, 'confidence': 0.5080544948577881, 'class': 'flightArrivalPlace', 'class_id': 1, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 605, 'y': 136, 'width': 49, 'height': 24, 'confidence': 0.3583473563194275, 'class': 'flightDepartureTime', 'class_id': 4, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'class': 'flightPrice', 'class_id': 7, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 934, 'y': 136, 'width': 53, 'height': 25, 'confidence': 0.6711810231208801, 'class': 'flightArrivalTime', 'class_id': 2, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 445, 'y': 455, 'width': 133, 'height': 56, 'confidence': 0.6684551239013672, 'class': 'flightName', 'class_id': 6, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 587, 'y': 470, 'width': 47, 'height': 15, 'confidence': 0.6166021823883057, 'class': 'flightDeparturePlace', 'class_id': 3, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 590, 'y': 444, 'width': 51, 'height': 24, 'confidence': 0.6007795333862305, 'class': 'flightDepartureTime', 'class_id': 4, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 587, 'y': 279, 'width': 47, 'height': 16, 'confidence': 0.5973087549209595, 'class': 'flightDeparturePlace', 'class_id': 3, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 590, 'y': 601, 'width': 51, 'height': 25, 'confidence': 0.5662532448768616, 'class': 'flightArrivalTime', 'class_id': 2, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 1077, 'y': 143, 'width': 70, 'height': 45, 'confidence': 0.5612732768058777, 'class': 'flightPrice', 'class_id': 7, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 918, 'y': 279, 'width': 61, 'height': 20, 'confidence': 0.5189711451530457, 'class': 'flightArrivalPlace', 'class_id': 1, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 444, 'y': 265, 'width': 135, 'height': 60, 'confidence': 0.5121964812278748, 'class': 'flightName', 'class_id': 6, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 917, 'y': 470, 'width': 59, 'height': 17, 'confidence': 0.5080544948577881, 'class': 'flightArrivalPlace', 'class_id': 1, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}, {'x': 605, 'y': 136, 'width': 49, 'height': 24, 'confidence': 0.3583473563194275, 'class': 'flightDepartureTime', 'class_id': 4, 'image_path': 'log/test_0.png', 'prediction_type': 'ObjectDetectionModel'}],
# # Load the JSON string
# data = json.loads(json_string)

# # Prettify the JSON data
# data = json.dumps(data, indent=2, sort_keys=True)

# Print the prettified JSON
# print(data)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'image': {'width': '1318', 'height': '645'}}
# for bbox in data:
#     print(bbox)

def ploat_on_pic():
    # Read data from the JSON file
    with open("log/data.json", "r") as json_file:
        loaded_data = json.load(json_file)

    img = cv2.imread('prediction.jpg')
    
    #  # Get screen resolution
    # screen_width, screen_height = get_screen_resolution()

    # # Resize the image to the screen resolution
    # img = cv2.resize(img, (640, 640))
    
    while True:
        for bbox in loaded_data:
            if bbox['class'] == 'flight':
                x = bbox["x"] 
                y =  bbox["y"]
                # cv2.rectangle(img, (x,y), (x+bbox['width'], y+bbox['height']), (0, 0, 255), 1)
                # print(bbox)
        cv2.imshow("image", img)
        if ord('q') == cv2.waitKey(1):
            break


# ploat_on_pic()

# get_test_pic()

