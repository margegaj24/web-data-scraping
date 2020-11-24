from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException, StaleElementReferenceException, WebDriverException
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import pyautogui
import os
import datetime, time
import glob
import math


def configure_driver():
	# Add additional Options to the webdriver
	return webdriver.Firefox(executable_path=".\\geckodriver.exe")
	# return webdriver.Firefox(executable_path="./geckodriver")


def clean_images_directory():

	files = glob.glob('./images/*.png')
	for f in files:
		os.remove(f)


def get_options(driver):

	driver.get('https://www.publicmutual.com.my/Our-Products/Fund-Overview')
	time.sleep(4)
	options = []
	try:
		WebDriverWait(driver, 30).until(lambda s: s.find_element_by_xpath('//select[@id="dnn_ctr1074_FP_FundOverview_ddlFund"]').is_displayed())
		select = driver.find_element_by_xpath('//select[@id="dnn_ctr1074_FP_FundOverview_ddlFund"]')
		texts = select.find_elements_by_xpath('./option[position() > 1]')
		for t in texts:
			if t.text.startswith('PUBLIC'):
				options.append(t.text)
		print('Found ' + str(len(options)) + ' options')
		return options
	except TimeoutException:
		print("TimeoutException: Element not found")
		return None
	except NoSuchElementException:
		print('No such element')
		return None
	except UnexpectedAlertPresentException:
		print('UnexpectedAlertPresentException occurred')
		return None
	except WebDriverException:
		print('WebDriverException occurred')
		return None


def get_images(driver, options):

	driver.maximize_window()
	for option in options:
		time.sleep(5)
		for i in range(3):
			if get_image(driver, option):
				break


def get_image(driver, option):
	try:
		WebDriverWait(driver, 30).until(lambda s: s.find_element_by_xpath('//select[@id="dnn_ctr1074_FP_FundOverview_ddlFund"]').is_displayed())
		driver.find_element_by_xpath('//select[@id="dnn_ctr1074_FP_FundOverview_ddlFund"]/option[text()="' + option + '"]').click()
		driver.find_element_by_xpath('//a[text()="Go"]').click()
		time.sleep(10)
		img = pyautogui.screenshot()
		img.save('./images/' + option + '.png')
		print('Screenshot taken for ' + option)
		return True
	except TimeoutException:
		print('TimeoutException occurred on ' + option + '. Trying refresh...')
		try:
			driver.refresh()
		except UnexpectedAlertPresentException:
			return False
		return False
	except NoSuchElementException:
		print('NoSuchElementException occurred on ' + option)
		return False
	except UnexpectedAlertPresentException as e:
		print(e.msg.split(': ')[1])
		print('UnexpectedAlertPresentException occurred on ' + option + '. Trying refresh...')
		try:
			driver.refresh()
		except UnexpectedAlertPresentException:
			return False
		return False
	except WebDriverException:
		print('WebDriverException occurred on ' + option + '. Refreshing page...')
		driver.refresh()
		return False


def create_pdf():

	filenames = os.listdir('./images')
	filenames = list(filter(lambda filename: filename.endswith('.png'), filenames))

	today = datetime.datetime.now()
	today1 = today.strftime('%d/%m/%Y')
	timestamp = today.strftime('%Y%m%d%H%M%S')

	c = Canvas('PMBFUND ' + timestamp + '.pdf')

	number_of_pages = math.floor(len(filenames) / 3)

	if len(filenames) % 3 > 0:
		number_of_pages += 1

	for i in range(number_of_pages):
		c.drawString(200, 830, 'PMB Report ' + today1)
		if i > 0:
			c.showPage()
		story = []
		for filename in filenames[i:i+3]:
			img = Image('./images/' + filename, 7*inch, 3.5*inch)
			story.append(img)
			story.append(Spacer(8, 8))
		f = Frame(4, 3, 8*inch, 11*inch, showBoundary=1)
		f.addFromList(story, c)
		c.saveState()

	c.save()
	print('Report created.')


def main():
	clean_images_directory()
	driver = configure_driver()
	options = get_options(driver)

	if options:
		get_images(driver, options)
		driver.close()
		create_pdf()
	else:
		exit('No options found. Exiting...\nPlease try to run the script again.')


main()
