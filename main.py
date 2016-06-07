from datetime import datetime
from flask import Flask
from flask_restful import Api, Resource
from flask.ext.cors import CORS

from utils import (
    get_feed_from_edgar,
    get_annual_sd_filings_from_cik,
    get_soup,
    get_meta_info_from_soup,
)

app = Flask(__name__)
api = Api(app)
CORS(app)


# Get company info given a stock ticker
class Company(Resource):
    def get_the_most_recent_8k(self, ticker_id):
        feed = get_feed_from_edgar(ticker_id, '8-K')
        # We just pull off the most recent entry
        entry = feed.entries[-1]
        str_date = entry['filing-date']
        date = datetime.strptime(str_date, '%Y-%m-%d')
        links = entry['links']
        return {'date': str(date), 'link': links[0]['href']}

    def get(self, ticker_id):
        recent_8k = self.get_the_most_recent_8k(ticker_id)
        soup = get_soup(recent_8k['link'])
        info = get_meta_info_from_soup(soup)
        return info


# SECFilings - get all the SD filings for a given cik
class SECFilings(Resource):
    def get(self, cik):
        return get_annual_sd_filings_from_cik(cik)


class SECFilingsDocs(Resource):
    # Data Processing methods
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
                    title = 'XX: could not parse 2'
                try:
                    description = cols[2].find('a').text
                except:
                    description = 'XX: could not parse 2'
                try:
                    url_part = cols[2].find('a').attrs['href']
                    url = '%s%s' % (base_url, url_part)
                except:
                    url = 'XX: could not parse 2'
                all_data.update({
                    'title': title,
                    'url': url,
                    'description': description,
                })
            else:
                # This means that it's probably not the header row but something else wierd is happening
                all_data.update({
                    'title': 'XX: could not parse 3',
                    'url': 'XX: could not parse 3',
                    'description': 'XX: could not parse 3',
                })
            docs.append(all_data)
        return docs

    def get(self, cik, year):
        filings = get_annual_sd_filings_from_cik(cik)
        url = filings[year]['url']
        if not url:
            return {}
        soup = get_soup(url)
        if not soup:
            return {}
        meta_dict = get_meta_info_from_soup(soup)
        meta_dict.update({
            'req_cik': cik,
            'req_year': year
        })
        docs = self._get_docs_from_soup(soup, meta_dict)
        return docs

## Actually setup the Api resource routing here
api.add_resource(Company, '/company/<ticker_id>')
api.add_resource(SECFilings, '/sec_sd_filings/<cik>')
api.add_resource(SECFilingsDocs, '/sec_supporting_docs/<cik>/<year>')

if __name__ == '__main__':
    app.run(debug=True, port=8899)
