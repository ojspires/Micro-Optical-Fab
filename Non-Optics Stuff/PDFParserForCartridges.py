#!/usr/bin/python
# -*- coding: utf-8 -*-

### PDFParserForCartridges.py ###
#	Oliver Spires 3-2-2019		#
#	This script opens PDFs from	#
#	the Commission 				#
#	Internationale Permanente	#
#	Pour l'Épreuve des Armes à	#
#	Feu Portatives (C.I.P) and	#
#	scans for dimensional data	#
#	from every PDF you allow it	#
#	to look at. I did this to	#
#	find similar cartridges to	#
#	the ones that I use, in		#
#	order to find reloading		#
#	tools that would work with	#
#	my cartridges. Tool mfgrs	#
#	don't have my cartridges	#
#	listed as compatible with	#
#	some of their product lines	#
#	but if the dimensions match	#
#	up, they should work. The	#
#	script works well if the	#
#	PDFs to examine are in the	#
#	same folder as the script.	#
#	To download the PDFs, I		#
#	wrote another script, titled#
#	TDCCFiles.py. I can't		#
#	redistribute the PDFs, but	#
#	users of the script can		#
#	access the data on their	#
#	own, the script just 		#
#	automates the collection	#
#	of the files. Output is CSV.#
### Enjoy!			-Oliver	  ###

import PyPDF2
import textract					# I had trouble getting this running on Windows; try in Ubuntu, and look at the textract manual to see what packages are needed from apt prior to pip installing textract
import glob
import csv

# pdf_file = open('6.pdf', 'rb')
# read_pdf = PyPDF2.PdfFileReader(pdf_file)
# number_of_pages = read_pdf.getNumPages()
# page = read_pdf.getPage(0)
# page_content = page.extractText()
# print(page_content)


def getTextFromPDF(filename = 'tabical-en-page38.pdf'):
	#open allows you to read the file
	pdfFileObj = open(filename, 'rb')
	#The pdfReader variable is a readable object that will be parsed
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	#discerning the number of pages will allow us to parse through all #the pages
	num_pages = pdfReader.numPages
	count = 0
	text = ""
	shellName = EGDiam = EGWidth = caseHeadDiam = bulletDiam = throatLength = fullLength = ''	# These are the variables that will be filled by this script
	captureBullet = captureThroat = 0
	textMethod = ''
	snInput = ''
#The while loop will read each page
#	while count < num_pages:
#		print('Trying PyPDF2')
#		pageObj = pdfReader.getPage(count)
#		count +=1
#		text += pageObj.extractText()
	#This if statement exists to check if the above library returned #words. It's done because PyPDF2 cannot read scanned files.

	#If the above returns as False, we run the OCR library textract to #convert scanned/image based PDF files into text
	print('Trying textract with PdfToText')
	text = textract.process(filename, method='pdftotext', language='eng', layout='layout')

	if len(text) > 500:		# Commence scanning for readable data
		text = text
		textMethod = 'PdfToText'
		lines = text.split('\n')
		for p in lines:
			if 'C.I.P.  ' in p:				# Find name of ammunition
				CIPLine = p.split('  ')
				while len(CIPLine) > 6:
					CIPLine.remove('')
#					print(CIPLine)
				shellName = CIPLine[1].strip(' ')
				if shellName == 'Date' or shellName == '':
					shellName = prevLine.strip(' ')
#			elif 'E1       =' in p or 'E1      =' in p or 'E1          =' in p:	# Find extraction groove diameter
#				print(p)
#				qi = p.index('E1')
#				q = p[qi + 13:qi + 32].strip(' ')
#				print(qi)
#				print(q)
#				EGDiam = float(q)
#			elif 'R1       =' in p or 'R1      =' in p or 'R1          =' in p:	# Find head diameter
#				print(p)
#				pi = p.index('R1')
#				r = p[pi + 13:pi + 32].strip(' ')
#				print(r)
#				caseHeadDiam = float(r)
#			elif 'e min    =' in p or 'e min   =' in p or 'e min       =' in p:	# Find min width of extraction groove
#				print(p)
#				si = p.index('e min')
#				print(si)
#				s = p[si + 13:si + 30].strip(' ')
#				print(s)
#				EGWidth = float(s)
#			elif 'E1 =' in p:													# Find extraction groove diameter
#				print(p)
#				qi = p.index('E1')
#				q = p[qi + 6:qi + 22].strip(' ')
#				print(qi)
#				print(q)
#				EGDiam = float(q)
			elif 'E1' in p and '=' in p:										# Find full length
				print(p)
				qi = p.index('E1')
				qii = p.index('=')
				if qii - qi < 15:
					q = p[qii + 1:qii + 15].strip(' ')
					print(q)
					EGDiam = float(q)
#			elif 'R1 =' in p:													# Find head diameter
#				print(p)
#				ri = p.index('R1')
#				r = p[ri + 6:ri + 22].strip(' ')
#				print(r)
#				caseHeadDiam = float(r)
			elif 'R1' in p and '=' in p:										# Find head diameter
				print(p)														# This method works best; there are 2 other attempts commented out above
				ri = p.index('R1')
				rii = p.index('=')
				if rii - ri < 15:
					r = p[rii + 1:rii + 15].strip(' ')
					print(r)
					caseHeadDiam = float(r)
#			elif 'e min =' in p:												# Find min width of extraction groove
#				print(p)
#				si = p.index('e min')
#				print(si)
#				s = p[si + 9:si + 20].strip(' ')
#				print(s)
#				EGWidth = float(s)
			elif 'e min' in p and '=' in p:										# Find min width of extraction groove
				print(p)														# This method works best; there are 2 other attempts commented out above
				si = p.index('e min')
				sii = p.index('=')
				if sii - si < 15:
					s = p[sii + 1:sii + 18].strip(' ')
					print(s)
					EGWidth = float(s)
				if EGWidth == 0:
					EGWidth = input('Please double-check the extraction groove depth')
			elif p.count('G1 1)') == 2 or p.count('G11)') == 2 or p[40:].count('G1') == 2:	# Find the bullet diameter
				print(p)
				ti = p[40:].index('G1')
#				print(ti)
				if '=' in p:
					t = p[ti + 40:].split('=')[1].strip(' ').split(' ')[0].strip(' ')
				else:
					t = ''
				print(t)
				if t == '':
					captureBullet = 1	# If this method can't find a number, tag the following line to be tested with another method
				else:
					bulletDiam = float(t)
			elif p.count('L3') == 2:											# Find the length from the head to the throat
				print(p)
				ui = p.index('L3')
#				print(ui)
				if '=' in p:
					u = p[ui:].split('=')[1].strip(' ').split(' ')[0].strip(' ')
				else:
					u = ''
				print(u)
				if u == '':
					captureThroat = 1	# If this method can't find a number, tag the following line to be tested with another method
				else:
					throatLength = float(u)
#			elif 'L6          =' in p or 'L6           =' in p or 'L6         =' in p or 'L6            =' in p:	# Find the full length
#				print(p)
#				vi = p.index('L6')
#				print(vi)
#				v = p[vi + 15:vi + 30].strip(' ')
#				print(v)
#				fullLength = float(v)
#			elif 'L6 =' in p:				# Find full length
#				print(p)
#				vi = p.index('L6')
#				v = p[vi + 6:vi + 22].strip(' ')
#				print(v)
#				fullLength = float(v)
			elif 'L6' in p and '=' in p:				# Find full length
				print(p)								# This method works best; there are 2 other attempts commented out above
				vi = p.index('L6')
				vii = p.index('=')
				if vii - vi < 15:
					v = p[vii + 1:vii + 15].strip(' ')
					print(v)
					fullLength = float(v)
			elif captureBullet == 1:					# The other method of bullet diam. detection didn't work. Try again to find data on the following line; the PDF-to-text conversion doesn't always keep text aligned in the same row, and some parts of the line may shift down.
				print(p)
				if '=' in p:
					t = p.split('=')[1].strip(' ')
				else:
					t = ''
				print(t)
				if t == '':
					captureBullet = 1
				else:
					bulletDiam = float(t)
					captureBullet = 0
			elif captureThroat == 1:					# The other method of throat length detection didn't work. Try again to find data on the following line
				print(p)
				if '=' in p:
					u = p.split('=')[1].strip(' ')
				else:
					u = ''
				print(u)
				if u == '':
					captureThroat = 1
				else:
					throatLength = float(u)
					captureThroat = 0
			prevLine = p
	#If the above returns as False, we run the OCR library textract to #convert scanned/image based PDF files into text
	else:
		print('Trying PyPDF2')
		while count < num_pages:
			pageObj = pdfReader.getPage(count)
			count +=1
			text += pageObj.extractText()

		if len(text) > 500:
			text = text
			textMethod = 'pdfReader'

		else:
			print('Trying textract with tesseract')	
			text = textract.process(filename, method='tesseract', language='eng')
			textMethod = 'Tesseract'
			shellName = text.split('\n')[20]
			print(text.split('\n')[10:30])
			print(shellName)
			try:
				snInput = input('ENTER if this is correct, type the accurate shell name if not:\n')
			except:
				snInput = ''
			if snInput != '':
				shellName = snInput
			print(text)	# Display the extracted data. With this tool (tesseract), the text extraction is unreliable. You can scroll in the terminal window to find what you need, or open the PDF and manually enter the requested data
			EGDiam = input('Find and enter E1:\n')
			EGWidth = input('Find and enter e min:\n')
			caseHeadDiam = input('Find and enter R1:\n')
			bulletDiam = input('Find and enter the Projectile G1:\n')
			throatLength = input('Find and enter L3:\n')
			fullLength = input('Find and enter L6:\n')
	# Now we have a text variable which contains all the text derived #from our PDF file. Type print(text) to see what it contains. It #likely contains a lot of spaces, possibly junk such as '\n' etc.
	# Now, we will clean our text variable, and return it as a list of keywords.
	return(text, textMethod, shellName, EGDiam, EGWidth, caseHeadDiam, bulletDiam, throatLength, fullLength)
#textOuter = getTextFromPDF('6-mm-dbg-en.pdf')
#print(len(textOuter[0]))
#print(textOuter[0].split('\n')[1][60:])
files = glob.glob('*.pdf')	# Find all of the PDFs in the CWD and return a list of them
textOuter = dataOuter = []
writeFile = open('shellsOutput.csv', 'w')
for n in files:
	print(n)							# Print the filename currently being processed
	returnedText = getTextFromPDF(n)	# Receive all data
	returnedData = returnedText[1:]		# Receive the processed data
	print(returnedText[1:])
	if '' in returnedText[1:]:			# Print the file text if any item fails to process correctly
		print(returnedText[0])
	textOuter.append(returnedText)
	csvWrite = csv.writer(writeFile, delimiter=',', quotechar='"')
	csvWrite.writerow(returnedText[1:])	# Write the collected data to a CSV file
#	print(returnedText[0])
#print(textOuter)
#print(dataOuter)
writeFile.close()
