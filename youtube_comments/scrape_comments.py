from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


def get_comments_from(driver, url):

	try:
		driver.get(url)
		driver.execute_script('window.scrollTo(0, 200)')
		WebDriverWait(driver, 20).until(lambda s: s.find_element_by_xpath('//ytd-comment-renderer').is_displayed())
		comments = []
		previous_number_of_comments = 0
		number_of_comments = len(driver.find_elements_by_xpath('//ytd-comment-renderer'))
		y = 200
		elements = []
		while number_of_comments > previous_number_of_comments:
			for i in range(9):
				if i <= 4:
					y += 500
				else:
					y += 150
				driver.execute_script('window.scrollTo(0,' + str(y) + ')')
				time.sleep(5)
			elements = driver.find_elements_by_xpath('//ytd-comment-renderer')
			previous_number_of_comments = number_of_comments
			number_of_comments = len(elements)

		for element in elements:
			comments.append(element.find_element_by_id('content-text').text + '\n')

		print('Found ' + str(number_of_comments) + ' comments')
		
		with open('all comments.txt', 'a') as file:
			file.writelines(comments)
		
		return comments

	except NoSuchElementException:
		print('Element not found.')
	except TimeoutException:
		print('Timeout Exception.')


def scrape():

	driver = webdriver.Firefox()

	with open('urls.txt', 'r') as file:
		urls = file.readlines()

	total_comments = []
	for url in urls:
		coments = get_comments_from(driver, url)
		total_comments.extend(coments)
	print('Total number of comments: ' + str(len(total_comments)))
	driver.quit()

	#with open('comments.txt', 'a') as file:
	#	file.writelines(total_comments)


scrape()
