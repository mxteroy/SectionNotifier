from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

#Spring 2020 = 202011
#Fall 2019 = 201931

#spring = 1; summer = 2; fall = 3
#last digit remains the same (means College Station campus)

year = 202011
subject = {
    'MATH': [
        304
    ]
}

option = webdriver.ChromeOptions()
#option.add_argument("-incognito")

option.add_argument("user-data-dir=selenium") #save cookies

driver = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=option)

driver.get("https://howdy.tamu.edu/uPortal/normal/render.uP")

#Wait 10 seconds for page to load before throwing exception

timeout = 10

try:
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH,"//a[@class='btn-group btn btn-lg btn-aggie']")))

except TimeoutException:
    print("Element was not found. Page may not have loaded!")
    driver.quit()


#find_elements_by_xpath return an array of selenium objects.

title_elements = driver.find_elements_by_xpath("//a[@class='btn-group btn btn-lg btn-aggie']")[0]
title_elements.click()

time.sleep(3)

#LOGIN TO CAS
text_area = driver.find_element_by_id('username')

login = open('login.txt', 'r')
loginInfo = login.read().splitlines()
username = loginInfo[0]
text_area.send_keys(username)

nextBtn = driver.find_elements_by_xpath("//button[@class='thinking-anim']")[0]
nextBtn.click()

time.sleep(3)
text_area = driver.find_element_by_id('password')

password = loginInfo[1]
text_area.send_keys(password)

nextBtn = driver.find_elements_by_xpath("//button[@class='thinking-anim']")[0]
nextBtn.click()

time.sleep(3)

driver.get('https://compassxe-ssb.tamu.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=registration')

driver.find_element_by_id('registerLink').click()

semesterDropdown = driver.find_element_by_id('select2-chosen-1')
semesterDropdown.click()

time.sleep(3)
driver.find_element_by_id(str(year)).click()

driver.find_element_by_id("term-go").click()

time.sleep(5)
driver.find_element_by_id('s2id_autogen8').send_keys('MATH')

time.sleep(3)
driver.find_element_by_id('MATH').click()

driver.find_element_by_id('txt_courseNumber').send_keys('304')

driver.find_element_by_id('search-go').click()


time.sleep(3)

container = driver.find_elements_by_xpath('//td[@data-id="517578" and @data-property="status"]')
available = container[0].find_elements_by_xpath('.//span[@dir="ltr"]')[2]


if int(available.text) > 0:
    print("Available!")
else:
    print("Not available!")