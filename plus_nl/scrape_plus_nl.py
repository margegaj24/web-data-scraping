from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import time
import pyodbc


def configure_driver():
	# Add additional Options to the webdriver
	firefox_options = Options()
	# add the argument and make the browser Headless.
	firefox_options.add_argument("--headless")
	# Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
	driver = webdriver.Firefox(executable_path="/home/mario/Downloads/geckodriver")  # , options=firefox_options)
	return driver


def save_image(url, filename):
	response = requests.get(url)
	file = open('path' + filename, "wb")
	print('File: ' + filename + ' saved')
	file.write(response.content)
	file.close()


def product_exist(cursor, product):

	cursor.execute('SELECT productId, productName, productPrice FROM PLus.dbo.Product WHERE productId = ' + product['id'])
	row = cursor.fetchone()
	if row is None:
		return False
	return row


def insert_new_product(conn, cursor, product_data):

	cursor.execute('INSERT INTO Plus.dbo.Product( productId, productName, brand, productPrice, quantity,  category, filename)'
				   'VALUES ( ?, ?, ?, ?, ?, ?, ?)',
				   product_data['id'], product_data['name'], product_data['brand'], product_data['price'],
				   product_data['quantity'], product_data['category'], product_data['filename'])

	conn.commit()

# ownedBrand


def insert_scraped_data(connection, cursor, products):

	inserted_products = 0
	updated_products = 0

	for product in products:
		save_image(product['url'], product['filename'])
		# firstly we need to check if the product already exists
		result = product_exist(cursor, product)
		if result:
			# if product exist in the database then we need to check if price changed
			if float(result[2]) != float(product['productPrice']) and result[1] == product['productName'] and result[0] == product['productId']:
				# this block of code updates the price value in case it has changed
				print('Price has changed for ' + product['productName'])
				print('Before: ' + str(result[1]) + '. After: ' + str(product['productPrice']))
				cursor.execute('UPDATE Plus.dbo.Product SET productPrice = ' + str(product['price']) + ' WHERE productId = ' + str(product['productId']))
				updated_products += 1
		else:
			# if product doesn't exist we insert it into the database
			insert_new_product(connection, cursor, product)
			inserted_products += 1

	print('Inserted new products: ' + str(inserted_products))
	print('Updated products: ' + str(updated_products))


def get_links(driver):

	links = []
	driver.get('https://www.plus.nl/')
	try:
		WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath('//button[text()="Producten"]').is_displayed())
		driver.find_element_by_xpath('//button[text()="Producten"]').click()
	except NoSuchElementException:
		print('Element not found.')
	except TimeoutException:
		print('Timeout Exception.')

	anchors = driver.find_elements_by_xpath('//nav[@class="category-nav"]//li[@class="category-menu__item category-menu__item--sub"]/a')
	for a in anchors:
		links.append(a.get_attribute('href'))
	domains = ['/'.join(link.split('/')[:-1]) for link in links]
	domains = list(set(domains))
	for domain in domains:
		if domain in links:
			links.remove(domain)
	print('Found ' + str(len(links)) + ' links')
	return links


def get_products(driver, urls):

	products = []
	for url in urls[:100]:
		driver.get(url)
		# wait for the element to load
		try:
			WebDriverWait(driver, 20).until(lambda s: s.find_element_by_xpath('//li[@class="ish-productList-item"]').is_displayed())
			nr_products = int(driver.find_elements_by_xpath('//div[@class="total-items-found"]')[0].text)
			nr_elements = len(driver.find_elements_by_xpath('//li[@class="ish-productList-item"]'))
			elements = []
			y = 100
			while nr_elements < nr_products:
				cHeight = driver.execute_script('return document.getElementById("showMoreProducts").clientHeight')
				elements = driver.find_elements_by_xpath('//li[@class="ish-productList-item"]')
				nr_elements = len(elements)
				driver.execute_script('window.scrollTo(0,' + str(y + 400) + ')')
				time.sleep(5)
				# print(elements)
				if cHeight > 0:
					driver.execute_script('document.getElementById("showMoreProducts").click()')
					# WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="showMoreProducts"]'))).click()
					time.sleep(5)
					driver.execute_script('window.scrollTo(0,' + str(y + 400) + ')')
				y += 400
			for element in elements:
				data = element.find_element_by_xpath('//div[@class="product-tile__info"]')
				productBrand = data.get_attribute('data-brand')
				if productBrand != '':
					productName = data.get_attribute('data-name').split(productBrand)[1].strip(' ')
				else:
					# print(url)
					productName = data.get_attribute('data-name')
					# print(productName)
				productPrice = data.get_attribute('data-price')
				productId = data.get_attribute('data-id')
				productCategory = data.get_attribute('data-category')
				productQuantity = data.get_attribute('data-quantity')
				productImageUrl = element.find_element_by_xpath('//img[@class="lazy"]').get_attribute('src')
				products.append({'name': productName, 'brand': productBrand, 'price': productPrice, 'id': productId, 'url': productImageUrl, 'category': productCategory,
								 'quantity': productQuantity, 'filename': productId + '.png'})
		except TimeoutException:
			print('Timeout at ' + url)
		except NoSuchElementException:
			print('No such element at ' + url)
	print('Found {0} products'.format(len(products)))
	return products


def main():

	driver = configure_driver()
	urls = get_links(driver)
	if urls:
		products = get_products(driver, urls)
		driver.close()
		connection = pyodbc.connect('Driver={SQL Server};Server=Server Name;Database=Plus;Trusted_Connection=yes;')
		cursor = connection.cursor()
		print('Updating database...')
		insert_scraped_data(connection, cursor, products)
		print('Finished.')


main()
