from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


def get_comments_from(driver, url):

	try:
		driver.get(url)
		WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath('//ytd-comment-renderer').is_displayed())
		comments = []
		previous_number_of_comments = 0
		number_of_comments = len(driver.find_elements_by_xpath('//ytd-comment-renderer'))
		y = 200
		while number_of_comments > previous_number_of_comments:
			for i in range(4):
				y += 500
				driver.execute_script('window.scrollTo(0,' + str(y) + ')')
				time.sleep(5)
			for i in range(5):
				y += 150
				driver.execute_script('window.scrollTo(0,' + str(y) + ')')
				time.sleep(5)
			elements = driver.find_elements_by_xpath('//ytd-comment-renderer')
			previous_number_of_comments = number_of_comments
			number_of_comments = len(elements)

		for element in elements:
			comments.append(element.find_element_by_id('content-text').text + '\n')

		print('Found ' + str(number_of_comments))
		return comments

	except NoSuchElementException:
		print('Element not found.')
	except TimeoutException:
		print('Timeout Exception.')


def scrape():

	driver = webdriver.Firefox()
	urls = ['https://youtu.be/tqoFTGaZfaI?list=PLJqg1rgDPzxgDzQW40btWbzDWUAb6LPVG',
			'https://youtu.be/NMYFLMYzvB4?list=PLJqg1rgDPzxgDzQW40btWbzDWUAb6LPVG',
			'https://youtu.be/t6iRYbREyc8?list=PLJqg1rgDPzxgDzQW40btWbzDWUAb6LPVG',
			'https://youtu.be/DflOq3rUXp4?list=PLJqg1rgDPzxgDzQW40btWbzDWUAb6LPVG']

	total_comments = []
	for url in urls:
		coments = get_comments_from(driver, url)
		total_comments.extend(coments)
	print('Total number of comments: ' + str(len(total_comments)))
	driver.quit()

	with open('comments.txt', 'a') as file:
		file.writelines(total_comments)


scrape()
