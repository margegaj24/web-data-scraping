from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import datetime
import re
import base64
from bs4 import BeautifulSoup


def get_proxies_through_api_calls():
	urls = ['https://api.proxyscrape.com/?request=displayproxies&proxytype=http&anonymity=elite&ssl=yes',
			'https://api.proxyscrape.com/?request=displayproxies&proxytype=http&anonymity=anonymous&ssl=yes',
			'https://api.proxyscrape.com/?request=displayproxies&proxytype=http&anonymity=elite&ssl=no',
			'https://api.proxyscrape.com/?request=displayproxies&proxytype=http&anonymity=anonymous&ssl=no', 'https://www.proxy-list.download/api/v1/get?type=http&anon=elite',
			'https://www.proxy-list.download/api/v1/get?type=https&anon=elite', 'https://www.proxy-list.download/api/v1/get?type=http&anon=anonymous',
			'https://www.proxy-list.download/api/v1/get?type=https&anon=anonymous']

	proxies = []
	for url in urls:
		response = requests.get(url)
		if response.status_code == 200:
			ips = response.text.split('\\r\\n')
			if 'ssl=yes' in urls[0] or 'type=https' in urls[0]:
				for ip in ips:
					proxies.append({'https': 'https://' + ip})
			else:
				for ip in ips:
					proxies.append({'http': 'http://' + ip})
			print('Found ' + str(len(proxies)) + ' proxies at ' + url)
		else:
			print('Couldn\'t get proxies. Status code: ' + str(response.status_code) + ' at ' + url)
	return proxies


def configure_driver(headless=False):
	# Add additional Options to the webdriver
	if headless:
		firefox_options = Options()
		firefox_options.add_argument("--headless")
		return webdriver.Firefox(executable_path="/home/mario/Downloads/geckodriver", options=firefox_options)
	return webdriver.Firefox(executable_path="/home/mario/Downloads/geckodriver")


def get_proxies0():
	# this url is not working
	url = 'http://free-proxy.cz/en/proxylist/country/all/https/ping/all'
	response = requests.get(url)
	if response.status_code == 200:
		soup = BeautifulSoup(response.text)
		rows = soup.find_all('td', text=re.compile(r'.decode\("(.+)"\)'))
		ips = []
		for i in rows:
			encoded_ip = re.findall(r'decode\("(.+)"\)', str(i))[0]
			ips.append(base64.b64decode(encoded_ip).decode('utf-8'))
		ports = [element.text for element in soup.find_all('span', {'class': 'fport'}, text=re.compile(r'\d+'))]

		if len(ips) == len(ports):
			proxies = []
			for i in range(len(ips)):
				proxies.append({'https': 'https://' + ips[i] + ':' + ports[i]})
			return proxies
	else:
		exit('Status code: ' + str(response.status_code))


def get_proxies1():
	driver = configure_driver()
	driver.get('https://hidemy.name/en/proxy-list/?type=hs&anon=234#list')

	try:
		driver.execute_script('window.scrollTo(0, 1500)')
		WebDriverWait(driver, 30).until(lambda s: s.find_element_by_xpath('//div[@class="table_block"]').is_displayed())
	except TimeoutException:
		print("TimeoutException: Element not found")
		return None

	proxies = []
	next_page = True

	while next_page:
		rows = driver.find_elements_by_xpath('//div[@class="table_block"]//tbody/tr')
		for row in rows:
			data = row.text.split(' ')
			if 'HTTPS' in row.text:
				proxies.append({'https': 'https://' + data[0] + ':' + data[1]})
			elif 'HTTP' in row.text:
				proxies.append({'http': 'http://' + data[0] + ':' + data[1]})
			else:
				print('No http or https protocol')
		try:
			driver.find_element_by_xpath('//li[@class="next_array"]/a').click()
		except:
			print('Found: ' + str(len(proxies)) + ' proxies')
			next_page = False

	driver.close()
	return proxies


def get_proxies2():
	urls = ['https://free-proxy-list.net', 'https://www.sslproxies.org']
	proxies = []
	driver = configure_driver()

	for url in urls:

		driver.get(url)

		try:
			driver.execute_script('window.scrollTo(0, 1500)')
			WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath('//li[@class="paginate_button next"]').is_displayed())
		except TimeoutException:
			print('Element not found at ' + url)
			continue

		next_page = True

		while next_page:
			rows = driver.find_elements_by_xpath('//table[@id="proxylisttable"]/tbody/tr')
			for row in rows:
				data = row.text.split(' ')
				if data[6] == 'yes':
					proxies.append({'https': 'https://' + data[0] + ':' + data[1]})
				else:
					proxies.append({'http': 'http://' + data[0] + ':' + data[1]})

			try:
				driver.find_element_by_xpath('//li[@class="paginate_button next"]/a').click()
			except:
				print('Found: ' + str(len(proxies)) + ' proxies at ' + url)
				next_page = False

	driver.close()
	return proxies


def get_proxies3():

	driver = configure_driver()
	urls = ['http://spys.one/en/free-proxy-list/', 'http://spys.one/en/https-ssl-proxy/']
	proxies = []

	for url in urls:
		driver.get(url)

		try:
			driver.execute_script('window.scrollTo(0, 500)')
			WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath('//tr[@class="spy1xx"]').is_displayed())
		except TimeoutException:
			print("Element not found at " + url)

		rows = driver.find_elements_by_xpath('//tr[contains(@class, "spy1x")]')
		for row in rows:
			data = row.text.split(' ')
			if data[1] == 'HTTPS':
				proxies.append({'https': 'https://' + data[0]})
			elif data[1] == 'HTTP':
				proxies.append({'http': 'http://' + data[0]})
			else:
				print('other protocol')

		print('Found: ' + str(len(proxies)) + ' proxies at ' + url)

	driver.close()
	return proxies


def get_proxies4():

	driver = configure_driver()
	driver.get('https://openproxy.space/list')
	proxies = []

	try:
		driver.execute_script('window.scrollTo(0, 2000)')
		WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath('//section[@class="lists"]/a[@class="list http"]').is_displayed())
	except TimeoutException:
		print("TimeoutException: Element not found")
		return None

	elements = driver.find_element_by_xpath("//section[@class='lists']").find_elements_by_xpath('./a[@class="list http"]')
	first_url = elements[0].get_attribute('href')
	second_url = elements[1].get_attribute('href')

	# first_url is for https protocol
	driver.get(first_url)

	try:
		WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath("//section[@class='data']/textarea").is_displayed())
	except TimeoutException:
		print("TimeoutException: Element not found")

	data = driver.find_element_by_xpath('//section[@class="data"]/textarea').text
	ips = data.split('\n')
	for ip in ips:
		proxies.append({'https': 'https://' + ip})

	# second_url is for http protocol
	driver.get(second_url)

	try:
		WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath("//section[@class='data']/textarea").is_displayed())
	except TimeoutException:
		print("TimeoutException: Element not found")
		return None

	data = driver.find_element_by_xpath('//section[@class="data"]/textarea').text
	ips = data.split('\n')
	for ip in ips:
		proxies.append({'http': 'http://' + ip})

	return proxies


def get_proxies5():

	driver = configure_driver(headless=True)
	driver.get('https://www.proxynova.com/proxy-server-list/')
	# This website is updated every 60s
	proxies = {'anonymous': [], 'transparent': []}

	try:
		driver.execute_script('window.scrollTo(0, 1000)')
		WebDriverWait(driver, 30).until(lambda s: s.find_element_by_xpath("//table[@id='tbl_proxy_list']").is_displayed())
	except TimeoutException:
		print("TimeoutException: Element not found")
		return None

	rows = driver.find_elements_by_xpath('//table[@id="tbl_proxy_list"]/tbody[1]/tr')
	for row in rows:
		if row.text != '':
			data = row.text.replace('\n', ' ').split(' ')
			if data[-1] != 'Transparent':
				proxies['anonymous'].append({'http': 'http://' + data[0] + ':' + data[1]})
			else:
				proxies['transparent'].append({'http': 'http://' + data[0] + ':' + data[1]})
	print('Found: ' + str(len(proxies['anonymous'])) + ' anonymous proxies and ' + str(len(proxies['transparent'])) + ' transparent proxies')

	driver.close()
	return proxies


def get_proxies6():

	driver = configure_driver()
	driver.get('http://www.freeproxylists.net/?c=&pt=&pr=&a[]=1&a[]=2&u=10')
	proxies = []

	try:
		WebDriverWait(driver, 120).until(lambda s: s.find_element_by_xpath('//table[@class="DataGrid"]').is_displayed())
	except TimeoutException:
		print('Element not found at www.freeproxylists.net')
		return None

	next_page = True

	while next_page:

		try:
			WebDriverWait(driver, 120).until(lambda s: s.find_element_by_xpath('//table[@class="DataGrid"]/tbody/tr[position() > 1]').is_displayed())
		except TimeoutException:
			print('TimeoutError: Next page not found at www.freeproxylists.net')

		rows = driver.find_elements_by_xpath('//table[@class="DataGrid"]/tbody/tr[position() > 1]')

		for row in rows:
			print(row.text)
			if row.text != '':
				data = row.text.split(' ')
				if data[2] == 'HTTPS':
					proxies.append({'https': 'https://' + data[0] + ':' + data[1]})
				else:
					proxies.append({'http': 'http://' + data[0] + ':' + data[1]})

		try:
			driver.implicitly_wait(60)
			driver.find_element_by_xpath('//div[@class="page"]/a[.="Next »"]').click()
		except NoSuchElementException:
			print('Found: ' + str(len(proxies)) + ' proxies.')
			next_page = False

	driver.close()
	return proxies

