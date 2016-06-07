# API for gathering SEC Special Disclosures


### `/company/<ticker>` or cik and receive company information like:

e.g. `/company/AAPL`
```json
{
    "business_address": "ONE INFINITE LOOP, CUPERTINO CA 95014, (408) 996-1010",
    "cik": "0000320193",
    "company_name": "APPLE INC",
    "filing_date": "2013-04-23 16:32:57",
    "mailing_address": "ONE INFINITE LOOP, CUPERTINO CA 95014",
    "sec_accession_number": "0001193125-13-167469",
    "sic_code": "3571",
    "sic_description": "Electronic Computers"
}
```

### `sec_sd_filings/<cik>` and receive list of special disclosures 

e.g. `sec_sd_filings/0000320193`

```json
{
    "2014": {
        "url": "http://www.sec.gov/Archives/edgar/data/320193/000119312514217311/0001193125-14-217311-index.htm",
        "year": "2014"
    },
    "2015": {
        "url": "http://www.sec.gov/Archives/edgar/data/320193/000119312515045292/0001193125-15-045292-index.htm",
        "year": "2015"
    },
    "2016": {
        "url": "http://www.sec.gov/Archives/edgar/data/320193/000119312516523320/0001193125-16-523320-index.htm",
        "year": "2016"
    }
}
```

### `sec_supporting_docs/<cik>/<year>` receive the supporting docs for the special disclosure for the year requested

e.g. `/sec_supporting_docs/0000320193/2014`

```json
[
    {
        "business_address": "ONE INFINITE LOOP, CUPERTINO CA 95014, (408) 996-1010",
        "cik": "0000320193",
        "company_name": "APPLE INC",
        "description": "d729300dsd.htm",
        "filing_date": "2014-05-29 16:30:39",
        "mailing_address": "ONE INFINITE LOOP, CUPERTINO CA 95014",
        "req_cik": "0000320193",
        "req_year": "2014",
        "sec_accession_number": "0001193125-14-217311",
        "sic_code": "3571",
        "sic_description": "Electronic Computers",
        "title": "FORM SD",
        "url": "https://www.sec.gov/Archives/edgar/data/320193/000119312514217311/d729300dsd.htm"
    },
    {
        "business_address": "ONE INFINITE LOOP, CUPERTINO CA 95014, (408) 996-1010",
        "cik": "0000320193",
        "company_name": "APPLE INC",
        "description": "d729300dex102.htm",
        "filing_date": "2014-05-29 16:30:39",
        "mailing_address": "ONE INFINITE LOOP, CUPERTINO CA 95014",
        "req_cik": "0000320193",
        "req_year": "2014",
        "sec_accession_number": "0001193125-14-217311",
        "sic_code": "3571",
        "sic_description": "Electronic Computers",
        "title": "EX-1.02",
        "url": "https://www.sec.gov/Archives/edgar/data/320193/000119312514217311/d729300dex102.htm"
    },
    {
        "business_address": "ONE INFINITE LOOP, CUPERTINO CA 95014, (408) 996-1010",
        "cik": "0000320193",
        "company_name": "APPLE INC",
        "description": "0001193125-14-217311.txt",
        "filing_date": "2014-05-29 16:30:39",
        "mailing_address": "ONE INFINITE LOOP, CUPERTINO CA 95014",
        "req_cik": "0000320193",
        "req_year": "2014",
        "sec_accession_number": "0001193125-14-217311",
        "sic_code": "3571",
        "sic_description": "Electronic Computers",
        "title": "Complete submission text file",
        "url": "https://www.sec.gov/Archives/edgar/data/320193/000119312514217311/0001193125-14-217311.txt"
    }
]
