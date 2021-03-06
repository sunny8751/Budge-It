from pymongo import MongoClient
import numpy as np
import bottlenose
from bs4 import BeautifulSoup
from urllib2 import HTTPError
import random
import time

db = MongoClient('mongodb://sunny8751:gatechfinance@vandyhacksiv-shard-00-00-swivj.mongodb.net:27017,vandyhacksiv-shard-00-01-swivj.mongodb.net:27017,vandyhacksiv-shard-00-02-swivj.mongodb.net:27017/test?ssl=true&replicaSet=VandyHacksIV-shard-0&authSource=admin')['vandyhacks']
client = 0

def error_handler(err):
    ex = err['exception']
    if isinstance(ex, HTTPError) and ex.code == 503:
        # time.sleep(random.expovariate(0.1))
        time.sleep(random.randint(0, 1))
        return True


# use Bottlenose to access Amazon Product Advertising API
# TODO: Fill in two differenta ccount information
AWS_ACCESS_KEY_ID1 = None
AWS_SECRET_ACCESS_KEY1 = None
AWS_ASSOCIATE_TAG1 = None


AWS_ACCESS_KEY_ID2 = None
AWS_SECRET_ACCESS_KEY2 = None
AWS_ASSOCIATE_TAG2 = None


def printMongoProducts():
	for product in list(db.products.find()):
		print(product)

def removeMongoProduct(productName):
	db.products.remove({"name": productName})

def addMongoProduct(productName, productPrice, productUnit):
	products = db.products

	newProduct = {
		"name": productName, 
		"price": productPrice,
		"unit": productUnit
	}
	# print (products)
	id = products.insert_one(newProduct).inserted_id
	print("Added product ID:", id)

def getMongoInfo(productName):
	price = ""
	unit = ""
	products = db.products.find({"name": productName})
	if products.count() == 0:
		# product not found
		price = "0"
		unit = ""
		return (price, unit)
	# return product's price
	price = products[0]["price"]
	unit = products[0]["unit"]
	return (price, unit)

def getMap(root):
		if len(root) == 0:
			return root
		map = {}
		for child in root:
			tag = child.tag[child.tag.index('}') + 1:]
			if tag not in map:
				#only update if it isn't in the map already
				map[tag] = getMap(child)
		return map

def getAmazonClient():
	global client
	if client == 0:
		AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID1
		AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY1
		AWS_ASSOCIATE_TAG = AWS_ASSOCIATE_TAG1
	else:
		AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID2
		AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY2
		AWS_ASSOCIATE_TAG = AWS_ASSOCIATE_TAG2

	amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG,
	    Parser=lambda text: BeautifulSoup(text, 'xml'), ErrorHandler=error_handler)
	# MaxQPS=0.9, 
	client = (client + 1) % 2
	return amazon

def getAmazonProductInfo(productName):
	amazon = getAmazonClient()
	# response = None
	# while response is None:
	# 	try:
	response = amazon.ItemSearch(Keywords=productName, SearchIndex="All", ResponseGroup="Offers")
	imageURL = amazon.ItemSearch(Keywords=productName, SearchIndex="All", ResponseGroup="Images")

	if response == None or imageURL == None:
		return None

	url = None
	if imageURL.find("MediumImage") != None:
		url = imageURL.find("MediumImage").find("URL").string
		# except urllib.error.HTTPError:
		# 	pass

	# print(response)
	# response = amazon.ItemLookup(ItemId="B007OZNUCE", ResponseGroup="Offers")
	# print(response)
	# for event, elem in etree.iterparse(responseXML, events=('start-ns',)):
	# 	print elem

	# root = etree.parse("other.xml").getroot()
	# print (root.tag)
	# for child in root:
	# 	print(child.tag, child.attrib)

	#parse the xml into an ElementTree
	# response = etree.XML(response)
	#convert ElementTree into map
	# response = getMap(response)
	# price = response["Items"]["Item"]["OfferSummary"]["LowestNewPrice"]["Amount"].text
	if response.find('Amount') == None:
		return None
	price = response.find('Amount').string

	# itemId = response["Items"]["Item"]["ASIN"].text
	if response.find('ASIN') == None:
		return None
	itemId = response.find('ASIN').string

	response = amazon.ItemLookup(ItemId=itemId)
	# response = etree.XML(response)
	# response = getMap(response)
	# description = response["Items"]["Item"]["ItemAttributes"]["Title"].text
	if response.find('Title') == None:
		return None
	description = response.find('Title').string

	return (description, price, url)


# main code
# print getMongoPrice("cookout")
# print getMongoUnit("cookout")
# getAmazonProductInfo("Kindle")
# print(getAmazonProductInfo("Ramen"))
# print(printMongoProducts())

