import re
import feedparser
import requests

from bs4 import BeautifulSoup
from datetime import datetime


def get_feed_from_edgar(cik, sec_doc_type='SD'):
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': cik,
        'type': sec_doc_type,
        'owner': 'exclude',
        'start': 0,
        'count': 40,
        'output': 'atom',
    }
    req = requests.Request('GET', base_url, params=params)
    prepped = req.prepare()
    feed_url = prepped.url
    feed = feedparser.parse(feed_url)
    return feed


def get_annual_sd_filings_from_cik(cik):
    filings = {}
    feed = get_feed_from_edgar(cik, 'SD')
    for entry in feed.entries:
        str_date = entry['filing-date']
        date = datetime.strptime(str_date, '%Y-%m-%d')
        year = str(date.year)
        links = entry['links']
        if len(links) != 1:
            return {'status': 'error', 'message': 'There was an error'}
        filings[year] = {'year': year, 'url': links[0]['href']}
    return filings


#
#  Data processing methods
#

def get_soup(url):
    page_response = requests.get(url)
    if page_response.status_code != 200:
        return None
    soup = BeautifulSoup(page_response.content, 'html.parser')
    return soup


def get_meta_info_from_soup(soup):
    """ Expects a soup of a standard edgar detail page
    """

    # Company Name
    company_info = soup.find(class_='companyInfo')
    company_name_cik = company_info.find(class_='companyName').text
    try:
        company_name = company_name_cik.split(' (Filer)')[0]
    except:
        company_name = 'XXX: could not parse 1'

    # CIK
    try:
        cik = company_name_cik.split('CIK:')[1].split('(')[0].lstrip().rstrip()
    except:
        cik = 'XXX: could not parse 1'

    # Accession Number
    try:
        sec_accession_number = list(soup.find(id='secNum').descendants)[-1].split('\n')[0].lstrip()
    except:
        sec_accession_number = 'XX: could not parse 1'

    # Filing Date
    try:
        required = None
        for infoHead in soup.findAll(class_='infoHead'):
            if infoHead.text == 'Accepted':
                required = infoHead
        filing_date = required.next_sibling.nextSibling.text
    except:
        filing_date = 'XX: could not parse 1'

    other_info = soup.find(class_="identInfo")
    # Industry Code
    try:
        sic_code_link = other_info.find(href=re.compile("SIC"))
        sic_code = sic_code_link.text
    except:
        sic_code = 'XX: could not parse 1'

    # Industry Code Description
    try:
        sic_code_link = other_info.find(href=re.compile("SIC"))
        sic_description = sic_code_link.next_element.next_element
        sic_description = sic_description.lstrip()
    except:
        sic_description = 'XX: could not parse 1'

    addresses = soup.findAll(class_='mailer')
    for address in addresses:
        if 'Mailing Address' in address.get_text():
            mailing_address_raw = address.get_text()
        if 'Business Address' in address.get_text():
            business_address_raw = address.get_text()
    # Business Address
    try:
        business_address = business_address_raw.strip('Business Address\n')
        business_address = re.sub(r"\n+", ", ", business_address)  # Remove new lines
        business_address = re.sub(r"  +", "", business_address)  # Remove blanks
    except:
        business_address = 'XX: could not parse 1'

    # Mailing Address
    try:
        mailing_address = mailing_address_raw.strip('Mailing Address\n')
        mailing_address = re.sub(r"\n+", ", ", mailing_address)  # Remove new lines
        mailing_address = re.sub(r"  +", "", mailing_address)  # Remove blanks
    except:
        mailing_address = 'XX: could not parse 1'

    return {
        'company_name': company_name,
        'cik': cik,
        'sec_accession_number': sec_accession_number,
        'filing_date': filing_date,
        'business_address': business_address,
        'mailing_address': mailing_address,
        'sic_code': sic_code,
        'sic_description': sic_description,
    }
