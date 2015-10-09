from bs4 import BeautifulSoup
import urllib2
import urllib
from sqlalchemy import create_engine
import os
import argparse
from itertools import product

# llinois EPA DMR url
URL = 'http://dataservices.epa.illinois.gov/dmrdata/dmrsearch.aspx'

# get the 'value' attribute for a given id
def getValue(soup, id):
    return soup.find(id=id).attrs['value']

# load the DMR page and make the request it wants
def getSoup():
    page = urllib2.urlopen(URL).read()
    soup = BeautifulSoup(page)
    
    values = {
        '__EVENTARGUMENT': '',
        '__EVENTTARGET': 'ctl00$MainContent$rblSearchOptions$0',
        '__EVENTVALIDATION': getValue(soup, '__EVENTVALIDATION'),
        '__LASTFOCUS':'',
        '__SCROLLPOSITIONX':'0',
        '__SCROLLPOSITIONY':'0',
        '__VIEWSTATE': getValue(soup, '__VIEWSTATE'),
        '__VIEWSTATEGENERATOR': getValue(soup, '__VIEWSTATEGENERATOR'),
        'ctl00$MainContent$rblSearchOptions':'0'
    }
    
    data = urllib.urlencode(values)
    req = urllib2.Request(URL,data)
    response = urllib2.urlopen(req)
    page = response.read()
    soup = BeautifulSoup(page)
    
    return soup

# given the DMR page returned by getSoup() get the lists of valid npdes_ids and years for download
def getOptions(soup):
    npdes_ids = [option.attrs['value'] for option in soup.find(id='ctl00_MainContent_ddlNpdes').findAll('option')]
    years = [option.attrs['value'] for option in soup.find(id='ctl00_MainContent_ddlYear').findAll('option')]
    
    # get rid of empty string
    years = [year for year in years if len(year) > 0]
    
    return npdes_ids, years

# download the CSV corresponding to a given npdes id and year
def getCSV(soup, npdes_id, year):

    values = {
        '__EVENTTARGET':'ctl00$MainContent$lnkExport',
        '__EVENTARGUMENT':'',
        '__LASTFOCUS':'',
        '__VIEWSTATE': getValue(soup, '__VIEWSTATE'),
        '__VIEWSTATEGENERATOR': getValue(soup, '__VIEWSTATEGENERATOR'),
        '__SCROLLPOSITIONX':'0',
        '__SCROLLPOSITIONY':'225',
        '__EVENTVALIDATION': getValue(soup, '__EVENTVALIDATION'),
        'ctl00$MainContent$rblSearchOptions':'0',
        'ctl00$MainContent$ddlNpdes': npdes_id,
        'ctl00$MainContent$ddlYear': year,
    }
    
    headers = {
        'Host': 'dataservices.epa.illinois.gov',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0 Iceweasel/30.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Referer': 'http://dataservices.epa.illinois.gov/dmrdata/dmrsearch.aspx',
        'Connection': 'keep-alive'
    }
    
    data = urllib.urlencode(values) 
    req = urllib2.Request(URL, data, headers)
    response = urllib2.urlopen(req)
    return response.read()

parser = argparse.ArgumentParser(description='Download npdes csvs')
parser.add_argument('--npdes', help='import a particular npdes permit')
parser.add_argument('--year', help='import all npdes permits for a particular year')
parser.add_argument('-o', action='store_true', help='overwrite existing csvs')
parser.add_argument('--dir', default='csv', help='directory to store csvs')
parser.add_argument('--psql', action='store_true', help='whether to run psql \\copy')

args = parser.parse_args()

soup = getSoup()
npdes_ids, years = getOptions(soup)

if args.npdes is not None:
    npdes_ids = [args.npdes]

if args.year is not None:
    years = [args.year]

if not os.path.isdir(args.dir):
    os.mkdir(args.dir)

for npdes_id, year in product(npdes_ids, years):
    filename = os.path.join('csv', '{}-{}.csv'.format(npdes_id, year))
    if (not os.path.exists(filename)) or args.o:
        print filename
        csv = getCSV(soup, npdes_id, year)
        with open(filename, 'w') as csv_file:
            csv_file.write(csv)
            csv_file.close()
            if args.psql:
                os.system("psql -c 'delete from dmr where date_part('year', period_end_date) = {} and npdes_id='{}'".format(year, npdes_id))
                os.system("psql -c '\copy dmr from {} with csv header;'".format(filename))
