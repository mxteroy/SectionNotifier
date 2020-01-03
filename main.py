from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import os
import json

from twilio.rest import Client

#Spring 2020 = 202011
#Fall 2019 = 201931

#spring = 1; summer = 2; fall = 3
#last digit remains the same (means College Station campus)

def main():
    date = 202011

    with open("src/data.json","r") as f:
        d = f.read()

    data= json.loads(d)

    workingData = {}

    for phoneNo in data:
        workingData[phoneNo] = data[phoneNo]["classes"]

    print(workingData)

    #-----------start webdriver---------------
    chrome_options = webdriver.ChromeOptions()
    #option.add_argument("-incognito")

    chrome_options.add_argument("user-data-dir=selenium") #save cookies

    driver = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=chrome_options)

    driver.get("https://howdy.tamu.edu/uPortal/normal/render.uP")

    #Wait 10 seconds for page to load before throwing exception

    timeout = 10

    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH,"//a[@class='btn-group btn btn-lg btn-aggie']")))

    except TimeoutException:
        print("Element was not found. Page may not have loaded!")
        driver.quit()

    #find_elements_by_xpath return an array of selenium objects.

    driver.find_elements_by_xpath("//a[@class='btn-group btn btn-lg btn-aggie']")[0].click()

    time.sleep(3)

    #LOGIN TO CAS
    text_area = driver.find_element_by_id('username')

    login = open('src/login.txt', 'r')
    loginInfo = login.read().splitlines()
    username = loginInfo[0]
    text_area.send_keys(username)

    driver.find_elements_by_xpath("//button[@class='thinking-anim']")[0].click()

    time.sleep(3)
    password = loginInfo[1]
    driver.find_element_by_id('password').send_keys(password)

    driver.find_elements_by_xpath("//button[@class='thinking-anim']")[0].click()

    time.sleep(5)

    driver.get('https://compassxe-ssb.tamu.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=registration')

    driver.find_element_by_id('registerLink').click()

    driver.find_element_by_id('select2-chosen-1').click()

    time.sleep(3)
    driver.find_element_by_id(str(date)).click()
    time.sleep(3)
    driver.find_element_by_id("term-go").click()

    time.sleep(5)

    def getAvailability(subject, courseNo, CRN):
        
        driver.find_element_by_id('s2id_autogen8').send_keys(Keys.BACKSPACE)
        driver.find_element_by_id('s2id_autogen8').send_keys(Keys.BACKSPACE)
        driver.find_element_by_id('s2id_autogen8').send_keys(subject)

        time.sleep(3)
        driver.find_element_by_id(subject).click()

        driver.find_element_by_id('txt_courseNumber').clear()
        driver.find_element_by_id('txt_courseNumber').send_keys(courseNo)

        driver.find_element_by_id('search-go').click()

        time.sleep(3)

        dataTypeNo = driver.find_element_by_xpath('//td[contains(text(), "'+ CRN + '") ]').get_attribute('data-id')
        print(dataTypeNo)
        container = driver.find_elements_by_xpath('//td[@data-id="' + dataTypeNo + '" and @data-property="status"]')
        availability = container[0].find_elements_by_xpath('.//span[@dir="ltr"]')[2].text

        driver.find_element_by_id('search-again-button').click()
        
        if int(availability) > 0:
            return subject + " " + courseNo + " CRN: " + CRN + " is available! Open Spots: " + availability
        else:
            return ''


    client = Client(loginInfo[2], loginInfo[3])
    for num in workingData:
        message = 'Courses you want are open!\n'
        foundOpen = 0
        for courseInfo in workingData[num]:
            if getAvailability(courseInfo[0], courseInfo[1], courseInfo[2]):
                message = message + '- ' + getAvailability(courseInfo[0], courseInfo[1], courseInfo[2]) + '\n'
                foundOpen += 1
        
        #if foundOpen:
        message = client.messages.create(to=num, from_="+17739662304",
                                    body="Section Notifier Test. Sorry Kim")


if __name__ == '__main__':
    main()