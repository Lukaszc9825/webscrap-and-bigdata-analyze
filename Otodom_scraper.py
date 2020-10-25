import requests
import json
from bs4 import BeautifulSoup as bs

class Scraper(object):
	
	def __init__(self, url, headers):
		self.url = url
		self.headers = headers
		self.page = requests.get(url, headers=headers)

		# Convert to bs object
		self.soup = bs(self.page.content, 'html.parser')

		# Contains all informations about apartments
		self.apartment_info = {}
		self.apartments_list = []

		Scraper.separate(self, self.soup)
		Scraper.all_pages(self)

	
	# Separate the apartments from each other 
	def separate(self,soupy):
		
		# Save all off the apartments into a list
		self.apartments = soupy.find_all(class_ = 'offer-item-details')
		
		#loop for evry single apartment
		for ap in self.apartments:

	  		#take data from <a> section
	  		temp = ap.find('a')
	  		self.apartment_info['href'] = temp.get('href')
	  		self.apartment_info['area'] = temp.find('strong').get_text()
	  		self.apartment_info['advertisment name'] = temp.find(class_ = 'offer-item-title').get_text()
	  		
	  		#take data from <p> section	
	  		temp = ap.find('p')

	  		if 'mieszkanie na wynajem:' == temp.find('span').get_text().lower().strip():
	  			self.apartment_info['for rent/sale'] = 'rent'
	  		else:
	  			self.apartment_info['for rent/sale'] = 'sale'
	  
	  		self.apartment_info['localization'] = temp.get_text().split(':')[1].strip()
	  		self.apartment_info['price'] = ap.find(class_ = 'offer-item-price').get_text().replace('/mc', '').strip()
	  
	  		self.apartments_list.append(self.apartment_info.copy())

		return self.apartments_list	


	#return information about the number of last page
	def get_number_of_pages(self):
		
		self.mess = self.soup.find_all(class_ = 'pager')
		for m in self.mess:
			a_class = m.find_all('a')
			for i, page in enumerate(a_class):
				if i == 4:
					self.last_page = int(page.get_text())
					return self.last_page		

	
	#make "separate" function fo all off the pages. (without first because of different url)
	def all_pages(self):
		for i in range(1, Scraper.get_number_of_pages(self)):
			self.url2 = 'https://www.otodom.pl/wynajem/mieszkanie/?page=' + str(i+1)
			self.page2 = requests.get(self.url2, headers=self.headers)
			self.soup2 = bs(self.page2.content, 'html.parser')
			Scraper.separate(self, self.soup2)


	#print list of dictionary in a more readable way (line by line)
	def display(list):
		for ap in list:
			[print(key, value) for key, value in ap.items()]



#help storage data in json file
class Json_file():

	def save(self, title, data):
		with open(title, 'w', encoding = 'utf-8') as f:
			json.dump(data, f, ensure_ascii = False, indent = 2)

	def load(self, title):
		with open(title, encoding = 'utf-8') as f:
			return json.load(f)



if __name__ == '__main__':

	url = 'https://www.otodom.pl/wynajem/mieszkanie/'

	headers = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
	(KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

	scraper = Scraper(url, headers)
	j = Json_file()
	j.save("otodom_data", scraper.apartments_list)