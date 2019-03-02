import re
import requests
import wget


pages = [2, 3, 4, 5, 6, 7, 8, 9, 10]	# Which pages of data do you need?
# pages = [1]
for n in pages:
    url = 'https://bobp.cip-bobp.org/fr/tdcc_public?page=' + str(n) + '&cartridge_type_id=1'
    response = requests.get(url)
    html = response.content
    english_url_search = html.decode("utf-8").split(sep='FR</a>&nbsp;<a href=')	# Use this separator to find the english-language PDF filenames on the server
    line = []
    url_specific = []
    for index, item in enumerate(english_url_search, start=1):
        if index == english_url_search.__len__():
            continue
        # print(index, item)
        line.append(english_url_search[index].split('"')[1])					# Splitting at the quotes leaves us with only the filename
        if 'tdcc/tab-i' in line[-1]:
            print(line[-1])
            url_specific.append(line[-1])
            #print(url_specific[-1])
            # web_file = urllib.urlopen('https://bobp.cip-bobp.org' + url_specific[-1])
            # local_file = open(url_specific[-1].split('/')[-1], 'w')
            #print(local_file)
            # local_file.write(web_file.read())
            # web_file.close()
            # local_file.close()

            print('Downloading from page', n, ', file ', int((index + 1) / 2), ' of 20.')
            url = 'https://bobp.cip-bobp.org' + url_specific[-1]
            # wget.download(url, url_specific[-1].split('/')[-1])   # Uncomment this to download