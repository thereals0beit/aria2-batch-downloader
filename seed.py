#!/usr/bin/env python 

import sys
import subprocess
import urllib2
import base64
import re
import os.path
import pprint
from bs4 import BeautifulSoup, NavigableString

USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

def startAndWaitForAria(url):
	print "Downloading: {0}".format(url)
	p = subprocess.Popen(['/usr/bin/aria2c', '-s16', '-x16', '-k1M', '--check-certificate=false', '--http-user={0}'.format(USERNAME), '--http-passwd={0}'.format(PASSWORD), url])
	p.wait()

def findFilesWithPattern(baseurl, pattern):
	downloadList = []

	html = downloadAuthFile(baseurl)

	if html is None:
		return downloadList

	data = downloadAuthFile(baseurl)

	if data is None:
		return downloadList

	soup = BeautifulSoup(data)
	table = soup.select('table')

	if len(table):
		for tr in table[0].find_all('tr'):
			print tr

			if len(tr.contents) < 4:
				print "Incompatible HTTP list type"
				continue

			# Name Last Modified Size Type
			dlname = tr.contents[0]
			dltype = tr.contents[3]

			#print vars(dlname)
			#print vars(dltype)

			if dlname is None or dltype is None:
				print "Parse error #1"
				continue

			if type(dlname.next_element) is NavigableString:
				continue

			#FIX
			dlurl = dlname.next_element

			if dlurl is None:
				print "Parse error #2"
				continue

			print dltype.text
			print dlurl['href']
			#sys.exit(0)

			if dltype.text.startswith('Directory'):
				continue

				#I will soon add support for downloading subfolders
			else:
				filename = dlurl.contents[0]
				href = dlurl['href']

				if pattern is not None:
					if pattern.find_all(filename):
						downloadList.append("{0}{1}".format(baseurl, href))
				else:
					downloadList.append("{0}{1}".format(baseurl, href))

	return downloadList

def getBasicAuthString():
	return base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')

def downloadFileList(downloads):
	if len(downloads) > 0:
		for f in downloads:
			startAndWaitForAria(f)
	else:
		print "No files found in directory!"

def singleFileDownload(url):
	if url.endswith('/'):
		downloadFileList(findFilesWithPattern(url, None))
	else:
		startAndWaitForAria(url)

def multiRegexDownload(url, reg):
	if url.endswith('/') is not True:
		print "This mode only supports directories!"
	else:
		downloadFileList(findFilesWithPattern(url, re.compile(reg)))

def downloadAuthFile(url):
	request = urllib2.Request(url)
	request.add_header("Authorization", "Basic %s" % getBasicAuthString())

	data = None

	try:
		data = urllib2.urlopen(request)
	except urllib2.URLError, e:
		print "URL Error ({0}): {1}".format(e.errno, e.strerror)
	except urllib2.HTTPError, e:
	    print "HTTP Error ({0}): {1}".format(e.errno, e.strerror)
	except:
		print "Unknown Exception: ", sys.exc_info()[0]
	finally:
		return data.read()

	return None

if len(sys.argv) == 2:
	singleFileDownload(sys.argv[1])
elif len(sys.argv) == 3:
	multiRegexDownload(sys.argv[1], sys.argv[2])
else:
	print "Parameter mismatch: Please enter URL to either a file, or a directory with an optional regex pattern"
