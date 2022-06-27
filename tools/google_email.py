import sys
import time
import random
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

def check_for_next_page(driver):
    try:
    #identify element
        driver.find_element(By.ID,"pnnext")
        return True
    #NoSuchElementException thrown if not present
    except NoSuchElementException:
        return  False

def extract_email(domain, text):
    email = re.findall(rf"[a-z0-9\.\-+_]+@{domain}+", text)

    return email

def run_crawler(domain):
    found_snippets= []
    query = f'intext:"@{domain}" intext:"email"'

    #erst die Optionen festlegen und dann Chromium starten
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-startup-window")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options) #festgelegte Optionen übergeben
    driver.implicitly_wait(0.5)
    #launch URL
    driver.get("https://www.google.com/")
    # Cookies zustimmen
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "L2AGLb"))).click()
    #identify search box
    m = driver.find_element(By.NAME, "q")
    #find_element_by_name("q")
    #enter search text
    m.send_keys(query)
    time.sleep(0.2)
    #perform Google search with Keys.ENTER
    m.send_keys(Keys.ENTER)

    '''[print(snippet) for snippet in found_snippets]'''

    #loop
    i=0
    while check_for_next_page(driver):
        #snippets sind die Vorschautexte unter den gefundenen Webseiten auf der Google-Suche
        snippets = driver.find_elements(By.CLASS_NAME, 'VwiC3b.yXK7lf.MUxGbd.yDYNvb.lyLwlc.lEBKkf') #die . müssen sein, im Google Quellcode steht das so: VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf und das sind alles einzelne Klassen
        #.text um auf den Text in den Snippets-Element in <span>-Elementen zugreifen zukönnen. 

        found_snippets.extend([snippet.text for snippet in snippets])

        time.sleep(random.uniform(3,20))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "pnnext"))).click()
        #es dürfen keine weiteren Texte drin sein, die werden sonst auch zu einem Listenelement verarbeitet
        #i+=1
        #print(f"bisher gecrawlte Seite: {i}")

    extraced_email = [extract_email(domain, snippet) for snippet in found_snippets if "@" in snippet]
    return extraced_email




if __name__ == '__main__':
    #domain = "unibw.de"
    domain = str(sys.argv[1])  
    print(run_crawler(domain))
 




