from selenium import webdriver
from bs4 import BeautifulSoup

browser = webdriver.Firefox()
browser.get("http://www.rushhour.nl/store_master.php?numYear=2018&bIsOutOfStock=1&idxGenre=&app=1")
try:
	alert = browser.switch_to_alert()
	alert.accept()
	print "alert accpted"
except:
	print "no alert"
html = browser.page_source
browser.close()
soup = BeautifulSoup(html)


print soup