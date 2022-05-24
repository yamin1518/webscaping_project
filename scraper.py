from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
import requests
import io
from PIL import Image
import time 
import os 
import boto3 



class Scraper: 

    
    def __init__(self):
        
        PATH = "/Users/yamz/Desktop/chromedriver"
        self.driver = webdriver.Chrome(PATH)
        self.s3C = boto3.client('s3')
        

    def navigate(self):
        self.driver.get('https://www.google.co.uk/imghp?hl=en&ogbl')


        time.sleep(2) 
        accept_cookies_button = self.driver.find_element_by_xpath('//*[@id="L2AGLb"]')
        accept_cookies_button.click()

        search_bar = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
        search_bar.click()
        search_bar.send_keys("happy person")
        time.sleep(2)
        search_bar.send_keys(Keys.RETURN)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

    def get_images(self):

        num_images=10
        image_link = set()
        miss = 0 

        while len(image_link) + miss < num_images:
            thumbnails= self.driver.find_elements(By.CLASS_NAME, "Q4LuWd")

            for img in thumbnails[len(image_link) + miss : num_images]:
                try: 
                    img.click()
                    time.sleep(2)
                except:
                    continue

                images = self.driver.find_elements(By.CLASS_NAME, "n3VNCb")


                for image in images: 
                    if image.get_attribute('src') in image_link:
                        num_images +=1
                        miss +=1
                        break
                    if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                        image_link.add(image.get_attribute('src'))
                        print(f"Found {len(image_link)}")

        return image_link

    def download(self, download_path, url, file_path):
        
        try: 
            image_content = requests.get(url).content
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file)
            file_path = download_path + file_path


            with open (file_path, "wb") as f:
                image.save(f,"JPEG")

            print("success")
        except Exception as e:
            print("Failed -", e)
   
    def run(self):
        url = self.get_images()

        for i, url in enumerate(url):
            self.download("/Users/yamz/Desktop/webscraper project/happy/", url, str(i) + ".jpg")
        
        
    


    def uploadDirectory(self):
        path = '/Users/yamz/Desktop/webscraper project/happy'
        bucketname = 'happy-project-aic'
        for root,dirs,files in os.walk(path):
            for file in files:
                self.s3C.upload_file(os.path.join(root,file),bucketname,file)

if __name__ == '__main__':
    scraper = Scraper()
    scraper.navigate()
    scraper.run()
    scraper.uploadDirectory()
    



