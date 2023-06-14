import csv
import os
import re
import urllib.request
from time import sleep
import numpy as np


def pubmed_extract_data(query, num_pulls=4, total_abstract_count=200):

    # common settings between esearch and efetch
    base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    db = 'db=pubmed'
    os.makedirs(query, exist_ok=True)

    # esearch settings
    search_eutil = 'esearch.fcgi?'
    search_term = '&term=' + ('+').join(query.split(' '))
    search_usehistory = '&usehistory=y'
    search_rettype = '&rettype=json'

    # call the esearch command for the query and read the web result
    search_url = base_url+search_eutil+db+search_term+search_usehistory+search_rettype
    print("this is the esearch command:\n" + search_url + "\n")
    f = urllib.request.urlopen (search_url)
    search_data = f.read().decode('utf-8')

    # extract the total abstract count
    #total_abstract_count = int(re.findall("<Count>(\d+?)</Count>",search_data)[0])
    total_abstract_count = 200


    # efetch settings
    fetch_eutil = 'efetch.fcgi?'
    retmax = np.floor(total_abstract_count/num_pulls)
    retstart = 0
    fetch_retmode = "&retmode=text"
    fetch_rettype = "&rettype=abstract"

    # obtain webenv and querykey settings from the esearch results
    fetch_webenv = "&WebEnv=" + re.findall ("<WebEnv>(\S+)<\/WebEnv>", search_data)[0]
    fetch_querykey = "&query_key=" + re.findall("<QueryKey>(\d+?)</QueryKey>",search_data)[0]

    # call efetch commands using a loop until all abstracts are obtained
    run = True
    all_abstracts = list()
    loop_counter = 1

    while run:
        print("this is efetch run number " + str(loop_counter))
        loop_counter += 1
        fetch_retstart = "&retstart=" + str(retstart)
        fetch_retmax = "&retmax=" + str(retmax)
        # create the efetch url
        fetch_url = base_url+fetch_eutil+db+fetch_querykey+fetch_webenv+fetch_retstart+fetch_retmax+fetch_retmode+fetch_rettype
        print(fetch_url)
        # open the efetch url
        f = urllib.request.urlopen (fetch_url)
        fetch_data = f.read().decode('utf-8')
        with open(f"{query}/{retstart}-{retmax+retstart}.txt", "w") as text_file:
            text_file.write(fetch_data)
        # wait 2 seconds so we don't get blocked
        sleep(5)
        # update retstart to download the next chunk of abstracts
        retstart = retstart + retmax
        if len(loop_counter) > num_pulls:
            run = False

def main():
    query = input('Enter your question: ')
    num_pages = 5
    pubmed_extract_data(query)


if __name__ == '__main__':
    main()