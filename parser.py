import time
import os
import logging
from functools import wraps
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium_stealth import stealth
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("parser.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def time_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"Вызываемая функция: '{func.__name__}' | Время выполнения: {execution_time:.2f} сек.")
        return result
    return wrapper

class Parser:
    @time_logger
    def __init__(self, link):
        self.link = link
        
        ua = UserAgent()
        current_user_agent = ua.random
        
        logging.info(f"Используемый User-Agent: {current_user_agent}")

        # Настройки браузера Chrome
        options = Options()
        options.add_argument(f"user-agent={current_user_agent}")
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=options)
        
        stealth(self.driver,
                languages=["ru-RU", "ru"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        self.driver.get(self.link)
        self.info_list = []
        self.links_list = [] 
        self.date_dict = {}

    @time_logger
    def get_links_on_page(self):
        elements = self.driver.find_elements(By.CLASS_NAME, 'anons-name')
        for element in elements:
            link = element.find_element(By.TAG_NAME, 'a')
            self.links_list.append(link.get_attribute('href'))

    @time_logger
    def go_to_the_next_page(self):
        clickable_element = WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div[2]/div[2]/div/div[4]/div[3]/div[4]/div/a[4]"))
        )
        self.driver.execute_script("arguments[0].click();", clickable_element)

    @time_logger
    def get_info(self):
        for link in self.links_list:
            self.driver.get(link)
            time.sleep(5)
            self.info_list.append('Цена')
            tabble_list = self.driver.find_elements(By.CLASS_NAME, 'characteristic-name')
            print(tabble_list)
            for table in tabble_list:
                self.info_list.append(table.text)
            print(self.info_list)
            time.sleep(5)

        for link in self.links_list:
            price = self.driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/section/div/div/span[1]').text.strip()
            self.info_list.append(price)
           
            self.driver.get(link)
            print(link)
                
            time.sleep(2)
            tabble_list = self.driver.find_elements(By.CSS_SELECTOR, 'div.characteristic-value span')
            for table in tabble_list:
                self.info_list.append(table.text)

            time.sleep(2)

    @time_logger
    def creating_csv_file(self):
        for i in range(0 , len(self.info_list)-1):
            if (i < (len(self.info_list)/2)):
                self.date_dict.update({self.info_list[i] : [self.info_list[i+(int(len(self.info_list)/2))]]})
                if self.info_list[i] == 'Высота, мм:':
                    df_1 = pd.DataFrame(self.date_dict)
                    print(df_1)
                    df_1.to_csv("var.csv", index=False,  mode="a", sep=",", header=not os.path.isfile("var.csv"))
        print(self.date_dict)