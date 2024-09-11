import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from web_locators import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()


chrome_options.add_argument("--headless")


def find_word_before_target(text, target):
    pattern = r'\b(\w+)\b\s+\b{}\b'.format(re.escape(target))
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1)
    return None


def get_valid_number(price, string_appears):
    while True:
        user_input = input(f"{string_appears}")

        try:
            number = float(user_input)
        except ValueError:
            print("Invalid input! Please enter a valid number.")
            continue

        if price <= number <= 200000:
            return number
        else:
            print("The number must be between 0 and 200000. Please try again.")


def get_valid_pages_number():
    while True:
        user_input = input("Please enter how many pages to go through from 0-19 default: ")

        try:
            number = int(user_input)
        except ValueError:
            print("Invalid input! Please enter a valid number.")
            continue

        if 0 <= number <= 19:
            return number
        else:
            print("The number must be between 0 and 19. Please try again.")


chrome_driver_path = '/Users/shahardvora/monitoring-mobile-webui-automation/drivers/chromedriver'


def login_screen():
    option = 0
    first = False
    second = False
    try:
        while option != 1 or option != 2:
            option = input("Please enter the number of the site you wanna do the search: "
                           "\n1.www.landmodo.com."
                           "\n2.www.landsearch.com: \n")
            if option == '1':
                first = True
                break
            elif option == '2':
                second = True
                break
            else:
                print("Invalid number, please try again.")

        service = Service(executable_path=chrome_driver_path)
        driver_main = webdriver.Chrome(service=service, options=chrome_options)
        wait_main = WebDriverWait(driver_main, 30)

        if first:
            land_modo_search(driver=driver_main, wait=wait_main)
        elif second:
            land_search(driver=driver_main, wait=wait_main)
    except Exception:
        pass


def land_modo_search(driver, wait):
    global page_number, i, data_list, pages
    try:
        data_list = []
        ad_title_name_county = ""
        ad_complete_address = ""
        ad_description = ""
        ad_price = ""
        ad_acres = ""
        ad_apn = ""
        i = 0
        page_number = 0
        print("Enter to Landmodo website.")
        from_price = get_valid_number(0, "Please enter from price number between 0-200000: ")
        to_price = get_valid_number(from_price, f"Please enter to price number between {from_price}-200000: ")
        pages = get_valid_pages_number()
        driver.get(f"https://www.landmodo.com/properties?price={from_price}%3B{to_price}")

        for _ in range(pages):
            wait.until(EC.presence_of_element_located((By.XPATH, ads_list_title)))
            ad_list = driver.find_elements(By.XPATH, ads_list_title)
            counter = len(ad_list)
            for _ in range(counter):
                wait.until(EC.presence_of_element_located((By.XPATH, ads_list_title)))
                ad_list = driver.find_elements(By.XPATH, ads_list_title)
                print(f"Enter to {_ + 1} ad.")
                ad_list[i].click()

                try:
                    ad_title_name_county = driver.find_element(By.XPATH, ad_title_name_county_text).text
                    ad_apn = driver.find_element(By.XPATH, ad_apn_text).text
                    ad_complete_address = driver.find_element(By.XPATH, ad_complete_address_text).text
                    ad_price = driver.find_element(By.XPATH, ad_price_text).text
                    ad_acres = driver.find_element(By.XPATH, ad_acres_text).text
                    ad_description = driver.find_element(By.XPATH, ad_description_text).text
                except Exception:
                    pass

                try:
                    county_search_string = ad_title_name_county + ad_complete_address + ad_description
                    county_found = find_word_before_target(county_search_string, "county")
                    print(f"Ad complete address: {ad_complete_address}."
                          f" Ad price: {ad_price}."
                          f" Ad acres: {ad_acres}."
                          f" Ad county: {county_found}."
                          f" Ad apn: {ad_apn}."
                          )
                    data = [ad_complete_address, ad_price, ad_acres, county_found, ad_apn]
                    data_list.append(data)
                except Exception:
                    print("Error in append.")

                driver.back()
                i += 1
            print(f"Go to page number {page_number + 1} .")
            page_number += 1
            i = 0
            driver.get(f"https://www.landmodo.com/properties?page={page_number}&price={from_price}%3B{to_price}")

    except Exception as e:
        print(f"Error occurred: i value: {i}, page number{page_number} from pages: {pages}: description: {e}.")

    finally:
        try:
            df = pd.DataFrame(data_list, columns=['Address', 'Price', 'Acres', 'County', 'APN'])
            output_file = 'final_data.xlsx'
            df.to_excel(output_file, index=False)
            driver.quit()
        except Exception as e:
            print(f"Error occurred during creating excel file, description: {e}")


def land_search(driver, wait):
    key_value_list = {'Price': '', 'County': '', 'Elevation': '', 'MLS Number': '', 'Property taxes': '',
                      'Coordinates': '', 'APN number': ''}
    data_list = []
    i = 0
    page_number = 0
    print("Enter to landsearch website.")
    driver.get("https://www.landsearch.com")
    wait.until(EC.presence_of_element_located((By.XPATH, land_search_text)))
    search_text = driver.find_element(By.XPATH, land_search_text)
    search_value = input("What you want to search: ")
    if search_value != '':
        search_text.send_keys(search_value)
        time.sleep(1)
        search_text.send_keys(Keys.RETURN)
    else:
        from_price = get_valid_number(0, "Please enter from price number between 0-200000: ")
        to_price = get_valid_number(from_price, f"Please enter to price number between {from_price}-200000: ")
        driver.get(f"https://www.landsearch.com/properties/filter/price[max]={to_price},price[min]={from_price}")
    pages = get_valid_pages_number()
    wait.until(EC.presence_of_element_located((By.XPATH, land_search_properties_found_text)))
    total_properties = driver.find_element(By.XPATH, land_search_properties_found_text).text
    print(f'Total properties: {total_properties}')
    try:
        for _ in range(pages):
            wait.until(EC.presence_of_element_located((By.XPATH, land_search_ad_list_picture)))
            land_titles = driver.find_elements(By.XPATH, land_search_ad_list_picture)
            counter = len(land_titles)
            for _ in range(counter):
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, land_search_ad_list_picture)))
                    land_titles = driver.find_elements(By.XPATH, land_search_ad_list_picture)
                    land_titles[i].click()
                    wait.until(EC.presence_of_element_located((By.XPATH, land_search_property_text)))
                    properties = driver.find_elements(By.XPATH, land_search_property_text)
                    try:
                        parcels = driver.find_elements(By.XPATH, land_search_parcels_text).text
                        key_value_list['APN number'] = parcels
                    except Exception:
                        print("There is no APN number for this ad.")

                    try:
                        for prop in properties:
                            if prop.text.split('\n')[0] == 'Price':
                                key_value_list['Price'] = prop.text.split('\n')[1]
                            elif prop.text.split('\n')[0] == 'County':
                                key_value_list['County'] = prop.text.split('\n')[1]
                            elif prop.text.split('\n')[0] == 'Elevation':
                                key_value_list['Elevation'] = prop.text.split('\n')[1]
                            elif prop.text.split('\n')[0] == 'MLS Number':
                                key_value_list['MLS Number'] = prop.text.split('\n')[1]
                            elif prop.text.split('\n')[0] == 'Property taxes':
                                key_value_list['Property taxes'] = prop.text.split('\n')[1]
                            elif prop.text.split('\n')[0] == 'Coordinates':
                                key_value_list['Coordinates'] = prop.text.split('\n')[1]
                    except Exception as e:
                        print(f"Error during inserting data to the list. {e}")

                    print(f'{i + 1}: {key_value_list}')
                    try:
                        data = [key_value_list['Price'], key_value_list['County'], key_value_list['Coordinates'],
                                key_value_list['Elevation'], key_value_list['MLS Number'],
                                key_value_list['Property taxes'], key_value_list['APN number']]
                        data_list.append(data)
                    except Exception as e:
                        print(f"Error in append data: {e}")
                    driver.back()
                    time.sleep(2)
                    i += 1
                except Exception:
                    pass
            page_number += 1
            i = 0
            if page_number < pages:
                print(f"Go to page number {page_number} .")
                driver.get(
                    f"https://www.landsearch.com/properties/filter/price[max]={to_price},price[min]={from_price}/p{page_number}")
            else:
                print("Search completed.")
    except Exception:
        pass

    finally:
        try:
            df = pd.DataFrame(data_list,
                              columns=['Price', 'County', 'Coordinates', 'Elevation', 'MLS Number', 'Property taxes',
                                       'APN number'])
            output_file = 'final_data_land_search.xlsx'
            df.to_excel(output_file, index=False)
            driver.quit()
        except Exception as e:
            print(f"Error occurred during creating excel file, description: {e}")


login_screen()
