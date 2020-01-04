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
    credentials = open('C:\\Users\\xarae\\Documents\\Projects\\SectionNotifier\\credentials.txt', 'r')
    credentialsInfo = credentials.read().splitlines()

    username = credentialsInfo[0]
    password = credentialsInfo[1]
    twilioSID = credentialsInfo[2]
    twilioAUTH = credentialsInfo[3]
    dataPath = credentialsInfo[4]
    chromeDriverPath = credentialsInfo[5]
    seleniumPath = credentialsInfo[6]
    
    date = 202011

    #----------open data JSON----------------
    with open(dataPath,"r") as f:
        d = f.read()

    data= json.loads(d)

    #----------convert JSON to dictionary----
    workingData = {}

    for phoneNo in data:
        workingData[phoneNo] = data[phoneNo]["classes"]

    print(workingData)

    #-----------start webdriver---------------
    chrome_options = webdriver.ChromeOptions()
    #option.add_argument("-incognito")

    chrome_options.add_argument("user-data-dir=" + seleniumPath) #save cookies
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(executable_path=chromeDriverPath, chrome_options=chrome_options)

    driver.get("https://howdy.tamu.edu/uPortal/normal/render.uP")

    time.sleep(10)

    #-----------check if logged in------------------

    if len(driver.find_elements_by_xpath("//a[@class='btn-group btn btn-lg btn-aggie']")) > 0:
        driver.find_elements_by_xpath("//a[@class='btn-group btn btn-lg btn-aggie']")[0].click()

        time.sleep(3)

        #LOGIN TO CAS
        text_area = driver.find_element_by_id('username')

        text_area.send_keys(username)

        driver.find_elements_by_xpath("//button[@class='thinking-anim']")[0].click()

        time.sleep(3)
        
        driver.find_element_by_id('password').send_keys(password)

        driver.find_elements_by_xpath("//button[@class='thinking-anim']")[0].click()

        time.sleep(5)

        driver.get('https://compassxe-ssb.tamu.edu/StudentRegistrationSsb/ssb/classRegistration/classRegistration')

        try:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,"//a[@id='registerLink']")))
        except TimeoutException:
            print("Could not find element with id='registerLink'")
            driver.quit()

        time.sleep(2)
        driver.find_element_by_id('registerLink').click()

        driver.find_element_by_id('select2-chosen-1').click()

        time.sleep(3)
        driver.find_element_by_id(str(date)).click()
        time.sleep(3)
        driver.find_element_by_id("term-go").click()
    else:
        print("Element of class='btn-group btn btn-lg btn-aggie' was not found. Page may not have loaded or already logged in!")
        driver.get('https://compassxe-ssb.tamu.edu/StudentRegistrationSsb/ssb/classRegistration/classRegistration')


    #Go to registration page

    
    time.sleep(5)

    #-------------starting page at find classes page------------

    def getAvailability(subject, courseNo, CRN):
        
        driver.find_element_by_id('s2id_autogen8').send_keys(Keys.BACKSPACE)
        driver.find_element_by_id('s2id_autogen8').send_keys(Keys.BACKSPACE)
        driver.find_element_by_id('s2id_autogen8').send_keys(subject)

        time.sleep(3)
        driver.find_element_by_id(subject).click()

        driver.find_element_by_id('txt_courseNumber').clear()
        driver.find_element_by_id('txt_courseNumber').send_keys(courseNo)

        driver.find_element_by_id('search-go').click()

        time.sleep(5)

        #value="200"
        if driver.find_element_by_xpath('//option[@value="200"]').get_attribute('selected') is None:
            driver.find_element_by_xpath('//option[@value="200"]').click()
            time.sleep(4)

        dataTypeNo = driver.find_element_by_xpath('//td[contains(text(), "'+ CRN + '") ]').get_attribute('data-id')
        print(dataTypeNo)
        container = driver.find_elements_by_xpath('//td[@data-id="' + dataTypeNo + '" and @data-property="status"]')
        availability = container[0].find_elements_by_xpath('.//span[@dir="ltr"]')[2].text

        driver.find_element_by_id('search-again-button').click()
        print(subject + " " + courseNo + " CRN: " + CRN + " Open Spots: " + availability)
        
        if int(availability) > 0:
            return subject + " " + courseNo + " CRN: " + CRN + " is available! Open Spots: " + availability
        else:
            return ''


    client = Client(twilioSID, twilioAUTH)
    for num in workingData:
        message = 'Courses you want are open!\n'
        foundOpen = 0
        for courseInfo in workingData[num]:
            if getAvailability(courseInfo[0], courseInfo[1], courseInfo[2]):
                message = message + '- ' + getAvailability(courseInfo[0], courseInfo[1], courseInfo[2]) + '\n'
                foundOpen += 1
        
        if foundOpen:
            print(message)
            message = client.messages.create(to=num, from_="+17739662304", body=message)

    driver.quit()


if __name__ == '__main__':
    main()