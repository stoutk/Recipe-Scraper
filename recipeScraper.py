"""
Author: Kenneth Stout
Course: CS361 Oregon State University F23
Name: recipeScraper.py
Description: This program scrapes recipes from SimplyRecipes.com using a searchKey read from a file,
    searchKey.txt. For each recipe found on the website, a link to the recipe, the name of the recipe, 
    and a link to an image of the recipe are collected. The scraped data is written to a csv file for
    use by other applications.
Developed using: Windows 11 Home, Python 3.11.4, Selenium 4.15.2, Webdriver-Manager 4.0.1
Useful links and references:
    https://www.youtube.com/watch?v=pcGqraAgMto
    https://www.youtube.com/watch?v=y8CiSwDnQSU
    https://medium.com/analytics-vidhya/python-selenium-web-scraping-in-eight-steps-7d33b263f399
    https://stackoverflow.com/questions/9567069/checking-if-an-element-exists-with-python-selenium
    https://www.softwaretestingmaterial.com/stale-element-reference-exception-selenium-webdriver/
"""

import os
import time
import csv
from pathlib import Path
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

#input: an instance of a webdriver and an xpath to search for
#output: true if an element is found at the xpath, else false
def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

#input: an instance of a webdriver and a class to search for
#output: true if an element of class elementClass is found, else false
def check_exists_by_class(driver, elementClass):
    try:
        driver.find_element(By.CLASS_NAME, elementClass)
    except NoSuchElementException:
        return False
    return True

#input: an instance of a webdriver and integer indices to look up recipe cards
#output: the recipe name, link, and image (strings) found at the indices
def copy_recipe(driver, x, y):
    name = ""
    link = ""
    image = ""

    try:
        card = driver.find_element(By.XPATH, f'//*[@id="card-list__item_{x}-0{"" if y == 0 else ("-"+str(y))}"]')
        name = card.find_element(By.CLASS_NAME, 'card__underline').text
        link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')
        image = card.find_element(By.TAG_NAME, 'img').get_attribute('data-src')
    except StaleElementReferenceException:
        driver.refresh()

    return name, link, image

#input: a search key string to look up recipes for
#output: writes recipe names, links, and image links to a .csv file 
def main(searchKey):
    print(f'Searching SimplyRecipes.com for {searchKey}')

    #for parsing recipe cards 
    numRecipes = 0
    recipeName = ""
    recipeLink = ""
    recipeImageLink = ""

    #to write to CSV
    with open('recipes.csv', 'w', newline='', encoding='utf-8') as csvfile:
        recipeWriter = csv.writer(csvfile, dialect='excel')
        
        #search simplyrecipes using the search key
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get("https://www.simplyrecipes.com/search")
        searchbox = driver.find_element(By.ID, "search-form-input")
        searchbox.send_keys(searchKey)
        searchbox.send_keys(Keys.RETURN)

        #parse the search results, if any
        if(check_exists_by_xpath(driver, f'//*[@id="no-search-results_1-0"]')):
            print("The search term did not return any results.")
        else:
            #emulated do while loop to go through search results
            while(True):
                #at time of development, search results are displayed in two lists of 12 cards on SimplyRecipe
                for x in range(1, 3):
                    for y in range(12):
                        if check_exists_by_xpath(driver, f'//*[@id="meta-text--recipe_{x}-0{"" if y == 0 else ("-"+str(y))}"]'):
                            numRecipes += 1
                            recipeName, recipeLink, recipeImageLink = copy_recipe(driver, x, y)
                            recipeWriter.writerow([recipeName, recipeLink, recipeImageLink])

                #page navigation here
                if(check_exists_by_class(driver, "pagination__item-link--next")):
                    nextPage = driver.find_element(By.CLASS_NAME, "pagination__item-link--next")
                    nextPage.click()
                    continue
                else:
                    break

        driver.close()
        driver.quit()
    
    print (f'{numRecipes} recipes were found. The search results have been written to ./recipes.csv')

#Script to run main as a process that waits for searchKey.txt to execute
while True:
    path = Path('./searchKey.txt')
    
    if path.is_file():
        file = open(path, "r")
        searchKey = file.readline()
        file.close()
        os.remove(path)

        main(searchKey)
    else:
        time.sleep(1)

    