from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urlparse

from PIL import Image
import pytesseract
import requests
import re

import json
import os
import time
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class PriceComparator:
    def __init__(self):
        self.flag = 0
        self.resultDivsArr = []
        self.products = []
        
        
        # path to the ChromeDriver executable
        # self.driverPath = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
        self.driverPath = 'D:\\projects\\python\\ShopSage\\app\\browser\\chromedriver.exe'

        # Set Chrome options
        self.chrome_options = Options()
        # self.chrome_options.add_argument('--headless')
        self.chrome_options.binary_location = 'D:\\projects\\python\\ShopSage\\app\\browser\\chrome.exe'
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument("--disk-cache-dir=E:\projects\priceComparator\cache")
        self.chrome_options.add_argument("--incognito")
        self.chrome_options.add_argument('--allow-running-insecure-content')
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        
        # Set the path to the ChromeDriver executable
        webdriver_service = Service(self.driverPath)
        # Create a new Chrome instance
        self.driver = webdriver.Chrome(service=webdriver_service, options=self.chrome_options)
        
        # intializing websites
        self.websiteArr = []
        self.all_websites = {
            "electronics":[
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
                ],
            'grocery':[
                    # {
                    #     'name':'bigbasket',
                    #     'url':'https://www.bigbasket.com/'
                    # },
                    {
                        'name': 'amazon india',
                        'url': "https://www.amazon.in"
                    },
                    # {
                    #     'name':'jiomart',
                    #     'url':'https://www.jiomart.com/'
                    # },
                    # {
                    #     'name':'blinkit',
                    #     'url':'https://blinkit.com/'
                    # },
                ],
            'hotels':[
                {
                    'name':'oyorooms',
                    'url':'https://www.oyorooms.com/'
                },
                
            ]
            }
        
    def setCategory(self,category):
        # if(category=="electronics"):
        self.websiteArr = self.all_websites[category]
    
    def __html_to_json(self,html):
        if html is None:
            print("No tag found")
            return None
        soup = BeautifulSoup(html, 'html.parser')
        json_data = {}
        self.__parse_element(soup, json_data)
        return json.dumps(json_data, indent=4)

    def __parse_element(self,element, json_data):
        json_data['tag'] = element.name
        json_data['text'] = element.text.strip()
        json_data['attrs'] = element.attrs
        json_data['children'] = []
        for child in element.children:
            if child.name:
                child_data = {}
                self.__parse_element(child, child_data)
                json_data['children'].append(child_data)


    def __find_element(self, locator):
        return WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(locator))

    '''
        Code for overcoming Bot verification
    '''
    def __bypassRecaptcha(self):
        form = self.form
        # print(form.find_elements(By.TAG_NAME, 'input')[3].get_attribute('type'))
        recaptchaImgurl = form.find_element(By.TAG_NAME, 'img').get_attribute('src')
        response = requests.get(recaptchaImgurl, stream=True)
        
        # Save the image locally
        with open("log/image/recaptchaImage.jpg", "wb") as file:
            file.write(response.content)
            
        # reading text from image
        recaptchaText = pytesseract.image_to_string('log/image/recaptchaImage.jpg')
        
        # finding input text field
        inputlocator = (By.CSS_SELECTOR, 'input[type="text"]')
        inputTextField = self.__find_element(inputlocator)
        
        # using enter key to submit the form
        inputTextField.send_keys(recaptchaText + Keys.ENTER)
        
        # waiting browser to load new page
        wait = WebDriverWait(self.driver, 10)
        
        # saving new response after recaptcha submission
        file_name = f"website_recaptcha_form_submit_response.html"
        file_path = os.path.join(os.getcwd()+"/log", file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.driver.page_source)
        
        
        print("rechecking recaptcha")
        # deattaching dom form
        wait.until(EC.staleness_of(self.form))
        
        # taking new dom value
        form = self.driver.find_element(By.TAG_NAME,'form')
        
        # checking if the received response is for again recaptcha
        if(re.match("^Type.*character.*image", form.text)):
            print('recaptcha website')
            self.form = form
            self.__bypassRecaptcha()
    
         
    def __findParentElement(self,element1,element2):
        if element1 is None or element2 is None or element1 == element2:
            return element1
        else:
            return self.__findParentElement(element1.parent,element2.parent)
    
    def __find_parent_with_images(self,element):
        if len(element.find_all('img'))>0:
            return element
        else:
            return self.__find_parent_with_images(element.parent)
    
    def __searchWebpage(self,product,websiteBaseUrl):
        max_retries = 3
        retries = 0
        delay = 1
        
        def find_span_tag(tag):
            # for pattern in patterns:
                if tag.name == 'span':
                    print(tag.text)
                if tag.name == 'span' and  re.search(pattern,tag.text,re.IGNORECASE):  
                    return tag

        while retries < max_retries:
            try:
                # finding input search box in home page 
                pattern = re.compile(r'search',re.IGNORECASE) # the regular expression pattern
                input_elements = self.driver.find_elements(By.TAG_NAME,'input')
                flag = 0
                # Iterate over the input elements
                for input_element in input_elements:
                    # Check if the placeholder attribute matches the pattern
                    placeholder = input_element.get_attribute('placeholder')
                    
                    if placeholder and pattern.match(placeholder):
                        print("found search box : "+placeholder)
                        print(input_element)
                        # using enter key to submit the form and goto search result page
                        print(self.driver.current_url)
                        input_element.send_keys(product + Keys.ENTER)
                        print('searching for product')
                        WebDriverWait(self.driver, 5)
                        # .until(find_span_tag)

                        
                        flag = 1
                        # print(input_element.get_attribute('value'))
                        
                        # # wait for any ajax request to complete
                        
                        self.driver.get(self.driver.current_url)
                        break;
                # If the operation succeeds, exit the loop
                if flag:
                    retries = max_retries
            
            except StaleElementReferenceException:
                # If the element becomes stale, increment retries and wait before retrying
                retries += 1
                time.sleep(delay)
            
        # # if flag:
        #     # time.sleep(10) # wait for result
            
        if not flag:
            print('no input search box found')
            return
        
        # self.driver.get("https://www.flipkart.com/search?q=Phone%20mobile&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off")
        with open('log/searchresult.html', "w", encoding="utf-8") as file:
            file.write(self.driver.page_source)
        
        #####################################################################
        
        # Create a BeautifulSoup object
        soup = BeautifulSoup(self.driver.page_source,'html.parser')

        '''
            below code is used to find search result
        '''
        # Define a filter function to find the div elements with specific text
        # pattern = r'result'|'OYOs in' # regex pattern
        pattern = r'(result | OYOs in)' # regex pattern
        
        # # print(soup.find('form').find('input'))
        
        # Find the div elements with 'result' text using the filter function
        div_elements = soup.find_all(find_span_tag) # Would retrun all matching tag 
        if len(div_elements)==0:
            print("Sorry, couldn't find results")
            return
        # finding product 
        productDivs = [x for x in self.__find_parent_with_images(div_elements[-1]) if x.find('img')]
        if len(productDivs)==0:
            productDivs = [x for x in self.__find_parent_with_images(div_elements[-1]) if x.find('img',recursive=True)]
        
        if len(productDivs)==0:
            print("Unable to find product details")
            return       
        self.resultDivsArr += productDivs
        
        print("Number of results : "+str(len(productDivs)))
        
        text = ''
        for div in productDivs:
            if div is NavigableString :print(div)
            text+=str(div)
        # saving to html file for inspection using append mode
        with open('log/imageDivs.html', "w", encoding="utf-8") as file:
            file.write(text)
        
        # extracting price,image url and redirection link
        pricePattern = re.compile(r"(₹\d+|\$\d+(\.\d{2})?)")
        dollarPattern = re.compile(r"\$\d+(\.\d{2})?")

        def get_website_name(url):
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if domain.startswith('www.'):
                domain = domain[4:]  # Remove 'www.' prefix
            website_name = domain.split('.')[0]
            return website_name
        
        products = []
        length = 10
        for div in productDivs:
            product = dict()
            #getting details of 10 products
            if isinstance(div, Tag) and len(products)<10:
                price = div.find(string=pricePattern)
                if price:
                    if dollarPattern.search(price):
                        price = price.split(" ")[0]
                        price = price[1:].split(',')
                        price= "".join(x for x in price if x)
                        price = float(price)*81
                    else:
                        price = price[1:].split(',')
                        price= "".join(x for x in price if x)
                        price = float(price)
                    product['price'] = price
                    product['name'] = div.find('img').get('alt').split(',')[0]
                    product['imageUrl'] = div.find('img').get('src')
                    url = div.find('a').get('href')
                    if re.match(r"^(https?://)?([a-zA-Z0-9-]+\.)*[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(\/.*)?$", url) is None:
                        url = websiteBaseUrl + url

                    product['redirectLink'] = url
                    
                    product['websiteName'] = get_website_name(url)
                    # print(product)
                    
                    products.append(product)
        
        # sorting products according to price
        self.products += sorted(products, key=lambda x: x.get('price', float('inf')))
             
    
    def startScrapping(self,product):
        # product = "Phone mobile"
        result = []
        for website in self.websiteArr:
            self.currentWebsite = website
            # fetch website from url
            self.driver.get(website['url'])
            

            # Save the HTML response to a file
            index = website['name']
            file_name = f"log/website_recaptcha_{index}.html"
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.driver.page_source)
                        
            # Wait for the website to be visible and enabled
            wait = WebDriverWait(self.driver, 10)
            # wait for form
            self.form = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'form')))
            if(re.match("^Type.*character.*image", self.form.text)):
                print('recaptcha website')
                self.__bypassRecaptcha() # will submit recaptcha untill redirected to normal website 
            
            print("Website's home found")
            webpageHome = self.driver.page_source # getting home page of website
            
            file_name = f"log/webpageHome.html"
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, "a+", encoding="utf-8") as file:
                file.write(webpageHome)
                
            # starting search
            print(f'Started searching... for {product}')
            self.__searchWebpage(product,website['url'])
                # print(element,end='\n\n')

        print("Total number of results : "+str(len(self.products)))
        self.driver.close()
        return self.products 
        
def main():
   
    priceComparator = PriceComparator()
    
    priceComparator.startScrapping("mobile")    
    
   
if  __name__ == '__main__':
    main()