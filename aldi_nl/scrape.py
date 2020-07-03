from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import json
import requests
import pyodbc


def save_image(url, filename):
    response = requests.get(url)
    file = open('path' + filename, "wb")
    print('File: ' + filename + ' saved')
    file.write(response.content)
    file.close()


def product_exist(cursor, product):

    cursor.execute('SELECT productID, productName, priceWithTax FROM Aldi.dbo.Product WHERE productID = ' + product['productID'])
    row = cursor.fetchone()
    if row is None:
        return False
    return row


def insert_new_product(conn, cursor, product_data):

    cursor.execute('INSERT INTO Aldi.dbo.Product( productID, productName, brand, ownedBrand, priceWithTax, quantity,  primaryCategory, subCategory1, subCategory2, filename)'
                   'VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   product_data['productID'], product_data['productName'], product_data['brand'], product_data['ownedBrand'],
                   product_data['priceWithTax'], product_data['quantity'], product_data['primaryCategory'],
                   product_data['subCategory1'], product_data['subCategory2'], product_data['filename'])

    conn.commit()


def insert_scraped_data(connection, cursor, products):

    inserted_products = 0
    updated_products = 0

    for product in products:
        save_image(product['image_url'], product['filename'])
        # firstly we need to check if the product already exists
        result = product_exist(cursor, product)
        if result:
            # if product exist in the database then we need to check if price changed
            if float(result[2]) != float(product['priceWithTax']) and result[1] == product['productName'] and result[0] == product['productID']:
                # this block of code updates the price value in case it has changed
                print('Price has changed for ' + product['productName'])
                print('Before: ' + str(result[1]) + '. After: ' + str(product['priceWithTax']))
                cursor.execute('UPDATE Aldi.dbo.Product SET priceWithTax = ' + str(product['priceWithTax']) + ' WHERE productID = ' + str(product['productID']))
                updated_products += 1
        else:
            # if product doesn't exist we insert it into the database
            insert_new_product(connection, cursor, product)
            inserted_products += 1

    print('Inserted new products: ' + str(inserted_products))
    print('Updated products: ' + str(updated_products))


def configure_driver():
    # Add additional Options to the webdriver
    firefox_options = Options()
    # add the argument and make the browser Headless.
    firefox_options.add_argument("--headless")
    # Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
    driver = webdriver.Firefox(executable_path="path to webdriver", options=firefox_options)
    return driver


def get_first_level_of(driver, url, category):

    driver.get(url)

    try:
        WebDriverWait(driver, 30).until(lambda s: s.find_element_by_xpath("//span[.='Producten']").is_displayed())
    except TimeoutException:
        print("Producten not found")
        return None

    driver.find_element_by_xpath("//span[.='Producten']/..").click()

    if '.' in category:
        categories = category.split('.')
        try:
            driver.find_element_by_xpath('//span[@class="icon icon--arrow-right"]/../../a[contains(., "' + categories[0] + '")]').click()
            element = driver.find_element_by_id('mCSB_2_container')
            anchors = element.find_elements_by_tag_name('a')
            for i in range(1, len(anchors)):
                if anchors[i].text.__contains__(categories[1]):
                    return anchors[i].get_attribute('href')
        except NoSuchElementException:
            return None
    else:
        try:
            element = driver.find_element_by_xpath('//li[@class="mod-main-navigation__item"]//a[contains(., "' + category + '")]')
            return element.get_attribute('href')
        except NoSuchElementException:
            return None


def get_subcategory_of(driver, category_url, category_name):

    driver.get(category_url)

    try:
        WebDriverWait(driver, 30).until(lambda s: s.find_element_by_xpath('//div[@data-t-name="ContentTile"]').is_displayed())
    except TimeoutException:
        return None

    try:
        url = driver.find_element_by_xpath('//div[@data-t-name="ContentTile"]//h4[contains(., "' + category_name + '")]/../../../a').get_attribute('href')
        return url
    except NoSuchElementException:
        return None


def get_products(driver, urls):

    products = []
    for url in urls:
        driver.get(url)
        # wait for the element to load
        try:
            WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath('//div[contains(@class, "mod mod-article-tile mod-article-tile--tertiary")]').is_displayed())
        except TimeoutException:
            print("TimeoutException: Element not found at " + url + ' Maybe full path is missing. Please check the link.')

        try:
            parent = driver.find_element_by_xpath('//div[contains(@class, "row mod-tiles__items")]')
            elements = parent.find_elements_by_xpath('//div[contains(@class, "mod mod-article-tile mod-article-tile--tertiary")]')

            for element in elements:
                product_image_url = element.find_element_by_xpath('./div/img').get_attribute('srcset')
                product_image_url = 'https://www.aldi.nl' + re.split(r'\.png', product_image_url)[0] + '.png'
                productID = element.get_attribute('id').split('-')[-1]
                json_data = json.loads(element.get_attribute('data-article'))
                productInfo = json_data['productInfo']
                productCategory = json_data['productCategory']
                productName = productInfo['productName']
                brand = productInfo['brand']
                ownedBrand = productInfo['ownedBrand']
                priceWithTax = productInfo['priceWithTax']
                quantity = productInfo['quantity']
                primaryCategory = productCategory['primaryCategory']
                subCategory1 = productCategory['subCategory1']
                subCategory2 = productCategory['subCategory2']
                products.append({'productID': productID, 'productName': productName, 'brand': brand, 'ownedBrand': ownedBrand, 'priceWithTax': priceWithTax,
                                 'quantity': quantity, 'primaryCategory': primaryCategory, 'subCategory1': subCategory1, 'subCategory2': subCategory2, 'image_url': product_image_url, 'filename': str(productID) + '.png'})
        except NoSuchElementException:
            print('No product found in: ' + url + '\nMaybe xpath is wrong.')

    print('Found {0} products'.format(len(products)))
    return products


def main():

    driver = configure_driver()
    urls = []
    with open('products.txt', 'r') as file:
        lines = file.readlines()

        print('Getting categories...')
        for line in lines:
            levels = line.strip('\n').split('||')
            first_subcategories = levels[0]
            other_subcategories = levels[1]

            first_level_url = get_first_level_of(driver, 'https://www.aldi.nl', first_subcategories)
            if first_level_url and other_subcategories != '':
                other_subcategories = other_subcategories.split('.')
                url = get_subcategory_of(driver, first_level_url, other_subcategories[0])
                if len(other_subcategories) > 1 and url:
                    last_url = ''
                    for other_subcats in other_subcategories[1:]:
                        url = get_subcategory_of(driver, url, other_subcats)
                        if url is None:
                            break
                        else:
                            last_url = url
                    urls.append(last_url)
                else:
                    urls.append(url)
            else:
                if first_level_url:
                    urls.append(first_level_url)
                else:
                    print('Nothing found for: ' + line)
    print('Found ' + str(len(urls)) + ' categories')
    products = get_products(driver, urls)
    driver.close()
    connection = pyodbc.connect('Driver={SQL Server};Server=Server Name;Database=Aldi;Trusted_Connection=yes;')
    cursor = connection.cursor()
    print('Updating database...')
    insert_scraped_data(connection, cursor, products)
    print('Finished.')


main()
