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

		print('Found ' + str(number_of_comments))
		driver.quit()

	except NoSuchElementException:
		print('Element not found.')
	except TimeoutException:
		print('Timeout Exception.')


get_comments_from(webdriver.Firefox(), 'https://www.youtube.com/watch?v=ROeCwTHakqI&list=PLJqg1rgDPzxgDzQW40btWbzDWUAb6LPVG&index=1')
