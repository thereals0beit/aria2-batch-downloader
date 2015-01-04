#!/usr/bin/env python 

import sys
import subprocess
import urllib2
import base64
import re
import os.path
from bs4 import BeautifulSoup, NavigableString

USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

def startAndWaitForAria(chdir, url):
	if os.path.exists(chdir) is not True:
		print "Path {0} does not exist, attempting to create".format(chdir)
		try:
			os.makedirs(chdir)
		except:
			print "Failed to make directory, exiting"
			return

	os.chdir(chdir)

	print "Downloading: {0} to {1}".format(url, chdir)

	p = subprocess.Popen(['/usr/bin/aria2c', '-s16', '-x16', '-k1M', '--check-certificate=false', '--http-user={0}'.format(USERNAME), '--http-passwd={0}'.format(PASSWORD), url])
	p.wait()

def findFilesWithPattern(cwd, baseurl, pattern):
	downloadList = []

	data = downloadAuthFile(baseurl)

	if data is None:
		return downloadList

	data = data.read()

	soup = BeautifulSoup(data)
	
	table = soup.select('table')

	if len(table):
		for tr in table[0].find_all('tr'):

			if len(tr.contents) < 4:
				print "Incompatible HTTP list type"
				continue

			# Name Last Modified Size Type
			dlname = tr.contents[0]
			dltype = tr.contents[3]

			if dlname is None or dltype is None:
				print "Parse error #1"
				continue

			if type(dlname.next_element) is NavigableString:
				continue

			dlurl = dlname.next_element

			if dlurl is None:
				print "Parse error #2"
				continue

			# I added pattern check because if we're pattern matching we probably only want things from one directory
			# Recursion here could end up causing weird problems, especially if we're using it to download files from a root folder for example
			# It would traverse all the directories and end up downloading every file on the entire box that matched. Not good.
			# I will probably add a -r switch or something for this specific purpose
			if dltype.text.startswith('Directory') and dlurl['href'].startswith('.') is not True and pattern is None:
				newcwd = cwd + urllib2.unquote(dlurl['href'])
				print "Directory: " + newcwd
				downloadList = downloadList + findFilesWithPattern(newcwd, "{0}{1}".format(baseurl, dlurl['href']), pattern)
			else:
				filename = dlurl.contents[0]
				href = dlurl['href']

				if pattern is not None:
					if pattern.findall(filename):
						p = [cwd, "{0}{1}".format(baseurl, href)]

						downloadList.append(p)
				else:
					if href.startswith('.') is not True:
						p = [cwd, "{0}{1}".format(baseurl, href)]

						downloadList.append(p)

	return downloadList

def getBasicAuthString():
	return base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')

def downloadFileList(downloads):
	if len(downloads) > 0:
		for f in downloads:
			startAndWaitForAria(f[0], f[1])
	else:
		print "No files found in directory!"

def singleFileDownload(url):
	if url.endswith('/'):
		downloadFileList(findFilesWithPattern(os.getcwd() + '/', url, None))
	else:
		startAndWaitForAria(os.getcwd() + '/', url)

def multiRegexDownload(url, reg):
	if url.endswith('/') is not True:
		print "This mode only supports directories!"
	else:
		downloadFileList(findFilesWithPattern(os.getcwd() + '/', url, re.compile(reg)))

def downloadAuthFile(url):
	request = urllib2.Request(url)
	request.add_header("Authorization", "Basic %s" % getBasicAuthString())

	try:
		return urllib2.urlopen(request)
	except urllib2.URLError, e:
		print "URL Error ({0}): {1}".format(e.errno, e.strerror)
	except urllib2.HTTPError, e:
	    print "HTTP Error ({0}): {1}".format(e.errno, e.strerror)
	except:
		print "Unknown Exception: ", sys.exc_info()[0]

	return None

if len(sys.argv) == 2:
	singleFileDownload(sys.argv[1])
elif len(sys.argv) == 3:
	multiRegexDownload(sys.argv[1], sys.argv[2])
else:
	print "Parameter mismatch: Please enter URL to either a file, or a directory with an optional regex pattern"