import feedparser
import requests
import os

from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


# Get company info given a stock ticker
class Company(Resource):
    def get(self, ticker_id):
        url = "http://edgaronline.api.mashery.com/v2/companies"
        params = {
            'appkey': os.environ.get('EDGAR_KEY'),
            'primarysymbols': ticker_id,
        }
        response = requests.get(url=url, params=params)
        return response.json()


def get_filings_from_cik(cik):
    filings = {}
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': cik,
        'type': 'SD',
        'owner': 'exclude',
        'start': 0,
        'count': 40,
        'output': 'atom',
    }
    req = requests.Request('GET', base_url, params=params)
    prepped = req.prepare()
    feed_url = prepped.url
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        str_date = entry['filing-date']
        date = datetime.strptime(str_date, '%Y-%m-%d')
        year = str(date.year)
        links = entry['links']
        if len(links) != 1:
            return {'status': 'error', 'message': 'There was an error'}
        filings[year] = {'year': year, 'url': links[0]['href']}
    return filings


# SECFilings - get all the SD filings for a given cik
class SECFilings(Resource):
    def get(self, cik):
        return get_filings_from_cik(cik)


class SECFilingsDocs(Resource):
    # Data Processing methods
    def _get_soup(self, url):
        page_response = requests.get(url)
        if page_response.status_code != 200:
            return None
        soup = BeautifulSoup(page_response.content, 'html.parser')
        return soup

    def _get_meta_dict_from_soup(self, soup):
        company_info = soup.find(class_='companyInfo')
        company_name_cik = company_info.find(class_='companyName').text
        try:
            company_name = company_name_cik.split(' (Filer)')[0]
        except:
            company_name = 'XXX: could not parse 1'
        try:
            cik = company_name_cik.split('CIK:')[1].split('(')[0].lstrip().rstrip()
        except:
            cik = 'XXX: could not parse 1'
        try:
            sec_accession_number = list(soup.find(id='secNum').descendants)[-1].split('\n')[0].lstrip()
        except:
            sec_accession_number = 'XXX: could not parse 1'
        try:
            required = None
            for infoHead in soup.findAll(class_='infoHead'):
                if infoHead.text == 'Accepted':
                    required = infoHead
            filing_date = required.next_sibling.nextSibling.text
        except:
            filing_date = 'XXX: could not parse 1'
        return {
            'ret_company_name': company_name,
            'ret_cik': cik,
            'ret_sec_accession_number': sec_accession_number,
            'ret_filing_date': filing_date
        }

    def _get_docs_from_soup(self, soup, meta_dict):
        base_url = "https://www.sec.gov"
        docs = []
        disclosure_components_table = soup.find(class_='tableFile')
        for row in disclosure_components_table.findAll('tr'):
            cols = row.findAll('td')
            all_data = meta_dict.copy()
            if len(cols) == 0:
                # This is the header row
                continue
            if len(cols) > 2:
                try:
                    title = cols[1].text
                except:
                    title = 'XXX: could not parse 2'
                try:
                    description = cols[2].find('a').text
                except:
                    description = 'XXX: could not parse 2'
                try:
                    url_part = cols[2].find('a').attrs['href']
                    url = '%s%s' % (base_url, url_part)
                except:
                    url = 'XXX: could not parse 2'
                all_data.update({
                    'ret_title': title,
                    'ret_url': url,
                    'ret_description': description,
                })
            else:
                # This means that it's probably not the header row but something else wierd is happening
                all_data.update({
                    'ret_title': 'XXX: could not parse 3',
                    'ret_url': 'XXX: could not parse 3',
                    'ret_description': 'XXX: could not parse 3',
                })
            docs.append(all_data)
        return docs

    def get(self, cik, year):
        filings = get_filings_from_cik(cik)
        url = filings[year]['url']
        if not url:
            return {}
        soup = self._get_soup(url)
        if not soup:
            return {}
        meta_dict = self._get_meta_dict_from_soup(soup)
        meta_dict.update({
            'cik': cik,
            'year': year
        })
        docs = self._get_docs_from_soup(soup, meta_dict)
        return docs

## Actually setup the Api resource routing here
api.add_resource(Company, '/company/<ticker_id>')
api.add_resource(SECFilings, '/sec_sd_filings/<cik>')
api.add_resource(SECFilingsDocs, '/sec_supporting_docs/<cik>/<year>')

if __name__ == '__main__':
    app.run(debug=True, port=8899)
