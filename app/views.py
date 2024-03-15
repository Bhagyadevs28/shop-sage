from django.shortcuts import render
from .models.Product import Product
from django.http import JsonResponse
from .priceComparator import PriceComparator
import urllib.parse

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import re
import time
import json
from roboflow import Roboflow
import cv2
import ctypes
import os

result = []

def test(request):
    if request.method=="POST":
        url = 'https://www.makemytrip.com/flight/search?itinerary=BOM-DEL-22/11/2023&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&ccde=IN&lang=eng'
        # url = 'https://www.makemytrip.com/flight/search?itinerary=BKK-BLR-23/11/2023&tripType=O&paxType=A-1_C-0_I-0&intl=true&cabinClass=E&ccde=IN&lang=eng'
        # print(request.data)
        print(request.POST)
        
        data = request.POST
        # print(data)
        # return render(request, 'dummy.html',{'data':request.body})

        driverPath = 'D:\\projects\\python\\ShopSage\\app\\browser\\chromedriver.exe'

        # Set Chrome options
        chrome_options = Options()
        # self.chrome_options.add_argument('--headless')
        chrome_options.binary_location = 'D:\\projects\\python\\ShopSage\\app\\browser\\chrome.exe'
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disk-cache-dir=E:\projects\priceComparator\cache")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        
        # Set the path to the ChromeDriver executable
        webdriver_service = Service(driverPath)
        # Create a new Chrome instance
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        
        driver.get(url)
        driver.implicitly_wait(500)
        
        WebDriverWait(driver, 20)
        # .until(EC.presence_of_element_located(locator))
        driver.close()
        return JsonResponse({'data':data})

def prepareFlightsPics(source,dest,date):
    url = f'https://www.makemytrip.com/flight/search?itinerary={source}-{dest}-{date}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&ccde=IN&lang=eng'
    # url = 'https://www.makemytrip.com/flight/search?itinerary=BKK-BLR-23/11/2023&tripType=O&paxType=A-1_C-0_I-0&intl=true&cabinClass=E&ccde=IN&lang=eng'
    print(source,dest,date)
    print(url)
     # Use Edge browser
    driver = webdriver.Edge()

    # Maximize the browser window to make it full-screen
    driver.maximize_window()

    driver.get(url)
    
    # Set up a WebDriverWait with a timeout (in seconds)
    wait = WebDriverWait(driver, 30)

    # Define the regex pattern you're looking for
    pattern = r'flight'

    # Use WebDriverWait to wait until the element is present with the specified regex pattern
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/p/span')))
    # span_element = wait.until(EC.visibility_of_element_located(
    #     (By.XPATH, f"//span[contains(text(), '{pattern}')]")))

    try:
        # ok_button = WebDriverWait(driver, 100).until(
        #     EC.visibility_of_element_located(
        #         (By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div/div[3]/button'))
        # )
        btnPattern = r'OK'
        # ok_button = WebDriverWait(driver, 100).until(EC.visibility_of_element_located((By.XPATH, f"//button[contains(text(), 'OK','i')]]")))
        ok_button = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//button[contains(translate(text(), 'OK', 'ok'), 'ok')]]")))

        print("******* OK button found ******")
        # Assuming there is a button with text "OK" associated with the div, locate and click it
        # ok_button = div_element.find_element(
        #     By.XPATH, "./following-sibling::button[text()='OK']")
        ok_button.click()
    except Exception:
        print("******* OK button not found ******")
        pass
    # return
    # Get the total height of the webpage
    total_height = driver.execute_script(
        "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

    screen_height = driver.get_window_size()['height']
    iterations = total_height//screen_height
    
    # scroll through the page and take screenshots
    for i in range(iterations + 1):
        # Scroll down the webpage
        sloc = i * screen_height
        eloc = (i + 1) * screen_height
        driver.execute_script(f'window.scrollTo({sloc}, {eloc});')

        # Wait for a brief moment to allow content to load (you may need to adjust the duration)
        time.sleep(2)

        # Save the screenshot
        driver.save_screenshot(f"log/test_{i}.png")
    # Close the browser
    driver.quit()
    no_of_pics = iterations
    return no_of_pics

def prepareProductsPics(productName):
    websiteArr = [
        {
            'name': 'amazon india',
            'url': "https://www.amazon.in"
        },
        {
            'name': 'ebay',
            'url': "https://www.ebay.com/"
        },
        {
            'name': 'flipkart',
            'url': "https://www.flipkart.com/"
        }
    ]
     # Use Edge browser
    driver = webdriver.Edge()

    # Maximize the browser window to make it full-screen
    driver.maximize_window()

    imgNo = 0
    for website in websiteArr:
        driver.get(website['url'])
        max_retries = 3
        retries = 0
        delay = 1
        

        flag = 0
        while retries < max_retries:
            try:
                pattern = re.compile(r'search',re.IGNORECASE) # the regular expression pattern
                input_elements = driver.find_elements(By.TAG_NAME,'input')
                # Iterate over the input elements
                for input_element in input_elements:
                    # Check if the placeholder attribute matches the pattern
                    placeholder = input_element.get_attribute('placeholder')
                    
                    if placeholder and pattern.match(placeholder):
                        print("found search box : "+placeholder)
                        
                        # using enter key to submit the form and goto search result page
                        input_element.send_keys(productName + Keys.ENTER)
                        print('searching for product')
                        WebDriverWait(driver, 5)
                        flag = 1
                        break
                # If the operation succeeds, exit the loop
                if flag:
                    retries = max_retries
                    
            except StaleElementReferenceException:
                    # If the element becomes stale, increment retries and wait before retrying
                    retries += 1
                    time.sleep(delay)
        if not flag:
            print('no input search box found')
            return
        
        prepare(productName)
        # Get the total height of the webpage
        total_height = driver.execute_script(
            "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

        screen_height = driver.get_window_size()['height']
        iterations = total_height//screen_height
        
        # scroll through the page and take screenshots
        for i in range(iterations + 1):
            # Scroll down the webpage
            sloc = i * screen_height
            eloc = (i + 1) * screen_height
            driver.execute_script(f'window.scrollTo({sloc}, {eloc});')

            # Wait for a brief moment to allow content to load (you may need to adjust the duration)
            time.sleep(2)

            # Save the screenshot
            driver.save_screenshot(f"log/test_{imgNo}.png")
            imgNo+=1
        
    return imgNo

def predict_from_pic(picPath):
# def predict_from_pic(no):
    VERSION = 7
    rf = Roboflow(api_key="Q0yexfUhhIiHyRVmtvHa")
    project = rf.workspace("anandu-p-r-aum2x").project("object-extraction")
    model = project.version(VERSION).model

    # infer on a local image
    prediction = model.predict(picPath, confidence=60,overlap=30)
    
    # visualize your prediction
    prediction.save(f'log/prediction.jpg')
    
    data = prediction.json()['predictions']
    # Save data to a JSON file
    with open("log/data.json", "w") as json_file:
        json.dump(data, json_file)


def getData(request):
    global result
    # Example of retrieving records
    # all_objects = Person.objects.all()
    # print(all_objects)
    # data = {'data':"1231",'athlete_list':[{'name':"hussain bolt"},{'name':"hussain bolt"}],'objects':all_objects}
    # return render(request, 'dummy.html',data)
    
    if request.method=="POST":
        print()
        print()
        print()
        
    
    if request.method=="POST":
        # print(request.body)
        data = request.body
        
        print(request.POST)
        # Decode bytes to string
        # str_data = data.decode('utf-8')

        # Parse query string
        # parsed_data = urllib.parse.parse_qs(str_data)
        # print(parsed_data)
        # print('Post request received')
        category = request.POST["category"]
        
        dataRetreivalMethod = request.POST["scrapMethod"]
        searchKeyword = request.POST["search"]

        if dataRetreivalMethod == 'yolo':
            picNos = 0
            # if searched for flights
            if category == "flights":
                # getting flight details from form submitted
                source = request.POST['source']
                dest = request.POST['dest']
                date = request.POST['date']
                # formating date
                date = '/'.join(date.split('-')[::-1])
                
                # getting flight details
                picNos = prepareFlightsPics(source,dest,date)
                print("\nSuccessfully got flight details\n")
            
            # if searched for products
            else:
                picNos = prepareProductsPics(searchKeyword)
                pass
            # return JsonResponse({'success':True})
            
            # for predicting objects in image
            for no in range(picNos):
                predict_from_pic(f'log/test_{no}.png')
                print(f'\nPredicting image - {no}')
                
                # for showing labled images
                # predictedImg = cv2.imread(f'log/prediction.jpg')
                # cv2.imshow('Prediction',predictedImg)
                # press 'n' to goto next image
                # if cv2.waitKey(0)==ord('n'):
                #     cv2.destroyWindow('Prediction')
                # press 'q' to exit
                # elif cv2.waitKey(0)==ord('q'):
                #     cv2.destroyWindow('Prediction')
                #     break
            return JsonResponse({'result':result})
        
        else :
            # print(category)
            # print(searchKeyword)
            priceComparator = PriceComparator()
            priceComparator.setCategory(category)
            result = priceComparator.startScrapping(product=searchKeyword)
            
            for element in result:
                name = element['name']
                price = element['price']
                imageUrl = element['imageUrl']
                redirectLink = element['redirectLink']
                websiteName = element['websiteName']
                obj = Product.objects.create(websiteName=websiteName, redirectLink=redirectLink, name=name, price=price, imageUrl=imageUrl)
                
            return JsonResponse({'result':result})


def viewData(request):
    # obj = Person(name='John', age=25, city='New York')
    # obj.save()
    all_objects = Product.objects.all()
    print(all_objects)
    return JsonResponse({'success':True})

def prepare(pName):
    global result
    result = PriceComparator(headless=True).startScrapping(product=pName)
    for element in result:
        name = element['name']
        price = element['price']
        imageUrl = element['imageUrl']
        redirectLink = element['redirectLink']
        websiteName = element['websiteName']
        obj = Product.objects.create(websiteName=websiteName, redirectLink=redirectLink, name=name, price=price, imageUrl=imageUrl)
             

def index(request):
    all_objects = Product.objects.all()
    print(all_objects)
    return render(request, 'index.html')

def loadData(request):
    all_objects = Product.objects.all().reverse()
    result = list(all_objects.values())
    return JsonResponse({'result':result})