# -*- coding: UTF-8 -*-
#Copyright (c) 2014 Caleb Ku
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from decimal import Decimal
import dataset
import time, datetime
import zenlogbook_settings
import logging
import pprint
import re
import ezodf


class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


SLEEP_SECONDS = 5

def login(driver,myusername,mypassword):

	driver.get("https://cloud.zenminer.com/login")
	
	if check_exists_by_xpath(driver,"//*[@id='login-form']/div[1]/div/input")==True:
		logging.info('Portal loaded properly.')
	else:
		logging.info('Page did not load properly.')
		return

	username = driver.find_element_by_name('username')
	password = driver.find_element_by_name('password')

	username.send_keys(myusername)
	password.send_keys(mypassword)

	driver.find_element_by_xpath("//*[@id='login-form']/div[3]/div/div[2]/button").click()

def parse_remove(mystringdata,mytypedata):
	if mytypedata=='finddevice':
		mystringdata=re.sub("\((.+?)\)","",mystringdata)
	elif mytypedata=='findpool':
		mystringdata = re.search('\((.+?)\)', mystringdata).group(1)
	elif mytypedata=='findperf':
		mystringdata = re.split(' ', mystringdata)[0]
	elif mytypedata=='numeric':
		mystringdata = re.sub("[^\d.]", "", mystringdata)
	elif mytypedata=='datefromcss':
		try:
		    mystringdata = re.search('• (.+?) 00', mystringdata).group(1)
		except AttributeError:
		    # date not found in the original string
		    mystringdata = '11/22/99' # something is wrong with data
	mystringdata = mystringdata.replace(" ", "");
	return mystringdata

def get_activitystats(driver,whatstopdate):

	driver.get("https://cloud.zenminer.com/activity/")

	if check_exists_by_xpath(driver,"//*[@id='content']/div/div[2]/div/div[4]/a")==True:
		logging.info('Activity page is loaded')
	else:
		logging.info('Activity page is not loaded')
		return
	time.sleep(5)


	activityarray=Vividict()
	keeppaging=True
	while keeppaging==True:

		for row in range(1,11):
			found_array=parsed_hashlet(driver,row)
			if found_array==False: #not a hashlet data table
				continue
			elif found_array['date']>whatstopdate:
				entry_devicename=found_array['device']
				del found_array['device']
				entry_date=found_array['date']
				del found_array['date']
				for k,v in found_array.iteritems():
					activityarray[entry_date][entry_devicename][k]=v
			else:
				keeppaging=False
				break

		driver.find_element_by_css_selector("#DataTables_Table_0_paginate > ul > li.next > a > i").click()
		time.sleep(5)

	pprint.pprint(activityarray)
	return activityarray

	
def parsed_hashlet(driver,parsed_row):
	parsed_array={}
	entry=driver.find_elements_by_xpath(".//*[@id='DataTables_Table_0']/tbody/tr[%d]/td[2]/dl[1]/*" % parsed_row)

	if not entry:
		return False
	try:
		entry_listmap={'device':2, 'power':4, 'BTCpayout':6,'fee':8}

		entry_sum_listmap={'firstpool':1,'date':2,'firstpool_actual':2}
		entry_sum=driver.find_elements_by_xpath(".//*[@id='DataTables_Table_0']/tbody/tr[%d]/td[2]/dl[2]/*" % parsed_row)
		
		if len(entry)==10:
			hp_listmap={'fee':10,'HPpayout':8}
			entry_listmap= dict(entry_listmap.items()+hp_listmap.items())

		if len(entry_sum)==4:
			doubledip_listmap={'secondpool':3, 'secondpool_actual':4}
			entry_sum_listmap=dict(entry_sum_listmap.items()+doubledip_listmap.items())

		for k,v in entry_listmap.iteritems():
			parsed_array[k]=entry[v-1].text
		
		for k,v in entry_sum_listmap.iteritems():
			parsed_array[k]=entry_sum[v-1].text

		parsed_array['date'] = parse_remove(parsed_array['date'].encode('utf-8'),'datefromcss')
		parsed_array['date']=datetime.datetime.strptime(parsed_array['date'],"%m/%d/%y").date()
		
		parsed_array['devicetype']=parse_remove(parsed_array['device'],'findpool')
		parsed_array['device']=parse_remove(parsed_array['device'],'finddevice')
		parsed_array['fee']=parse_remove(parsed_array['fee'],'numeric')
		
		parsed_array['BTCpayout']=parse_remove(parsed_array['BTCpayout'],'numeric')
		
		parsed_array['power']=parse_remove(parsed_array['power'],'numeric')
		parsed_array['firstpool_actual']=parse_remove(parsed_array['firstpool_actual'],'findperf')
		parsed_array['firstpool']=parse_remove(parsed_array['firstpool'],'')

		if len(entry)==10:
			parsed_array['HPpayout']=parse_remove(parsed_array['HPpayout'],'numeric')

		if len(entry_sum)==4:
			parsed_array['secondpool_actual']=parse_remove(parsed_array['secondpool_actual'],'findperf')
			parsed_array['secondpool']=parse_remove(parsed_array['secondpool'],'')

			
		#print parsed_array
		

	except NoSuchElementException:
		return False
	return parsed_array
		
def write_stats(write_array, mystopdate, myspreadsheet,columnkey):
	
	if not write_array:
		return
	else:

		sheet = myspreadsheet.sheets['Sheet1']
		#get count of rows/columns
		maxrows = sheet.nrows()
		#colcount = sheet.ncols()
		sheet.append_rows(len(write_array.keys()))

		for k,v in bacon.iteritems():
			maxrows=maxrows+1
			#iterating through dates
			for n,m in v.iteritems():
				sheet['%s%d' % (columnkey['date'],maxrows)].formula=str(k)
				sheet['%s%d' % (columnkey['devicename'],maxrows)].formula=str(n)
				for p,q in m.iteritems():
					sheet['%s%d' % (columnkey[p],maxrows)].formula=q
			

		myspreadsheet.save()
		
def get_stopdate(mystopdate,myspreadsheet,columnkey):
	if mystopdate=='yesterday':
		yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
		#stopdate = yesterday.strftime('%m/%d/%y')
		#print mystopdate

	elif mystopdate=='update':
		sheet = myspreadsheet.sheets['Sheet1']
		rowcount=sheet.nrows()
		stopdate=sheet['%s%d'% (columnkey['date'],rowcount)].value
		stopdate=datetime.datetime.strptime(stopdate,"%Y-%m-%d").date()
		#stopdate=stopdate.strftime('%m/%d/%y')
		#print stopdate

	return stopdate

def check_exists_by_xpath(driver,xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def check_exists_by_css(driver,css_selector):
    try:
        driver.find_element_by_css_selector(css_selector)
    except NoSuchElementException:
        return False
    return True

def check_hours():

	timestamp = datetime.datetime.now().time() # Throw away the date information
	time.sleep(1)

	# Or check if a time is between two other times
	start = datetime.time(15, 15)
	end = datetime.time(23)

	return (start <= timestamp <= end)

def cleanup_exit(driver):
	time.sleep(SLEEP_SECONDS)
	driver.close()


def get_stats():
	bacon =1
	if bacon==1:	
		driver = webdriver.Chrome()
		logging.basicConfig(filename='zenslogbook.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
		driver.set_page_load_timeout(30)
		ezodf.config.set_table_expand_strategy('all')
		myspreadsheet = ezodf.opendoc(zenlogbook_settings.SPREADSHEETNAME)
		logging.info('Time check - passed.'
		login(driver,hashlette_settings.ZENMINER_USERNAME,zenlogbook_settings.ZENMINER_PASSWORD)
		whatstopdate=get_stopdate(zenlogbook_settings.STOPDATE, myspreadsheet, zenlogbook_settings.SPREADSHEET_KEY)
		scraped_array = get_activitystats(driver,whatstopdate)
		write_stats(scraped_array,whatstopdate,myspreadsheet,zenlogbook_settings.SPREADSHEET_KEY)


		#cleanup_exit(driver)

	else:
		logging.warning("It's not time for scraping")
		cleanup_exit(driver)


get_stats()

