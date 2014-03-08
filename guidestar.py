import Queue
import re
import threading
import time

import cookielib
import mechanize
import pymongo

keywords = [
    'lesbian'
    , 'gay'
    , 'bisexual'
    , 'transgender'
    , 'transmen'
    , 'transwomen'
    , 'queer'
    , '"two spirit"'
    , 'intersex'
    , '"gender non*"'
    , 'gender'
    , 'lgbt'
    , 'lgbtq'
]
incomes = [
    ('','1')
    ,('1','100k')
    ,('100k','200k')
    ,('200k','300k')
    ,('300k','400k')
    ,('400k','500k')
    ,('500k','600k')
    ,('600k','700k')
    ,('700k','800k')
    ,('800k','900k')
    ,('900k','1m')
    ,('1m','')
]
keywords = ['gay']
incomes = [('0','')]

base_url = 'http://www.guidestar.org/'
search_url = base_url + 'AdvancedSearch.aspx'
login_url = base_url + 'Login.aspx'

login_email = 'ctl00$phMainBody$LoginMainsite$UserName'
login_password = 'ctl00$phMainBody$LoginMainsite$Password'

keyword_name = 'ctl00$phMainBody$orgSearchConfiguration_keywords$txtValue'
min_income_name = 'ctl00$phMainBody$orgSearchConfiguration_incometotal$tbMin'
max_income_name = 'ctl00$phMainBody$orgSearchConfiguration_incometotal$tbMax'
category_name = 'ctl00$phMainBody$orgSearchConfiguration_nteecode$txtValue'
state_name = 'ctl00$phMainBody$orgSearchConfiguration_state$gslbList'

name_regex = r'<p class="org-name">(.*?)</p>'
addr1_regex = r'<span id="ctl00_phMainBody_spQuickAddr1">\s*(.*?)\s*</span>'
addr2_regex = r'<span id="ctl00_phMainBody_spQuickAddr2">\s*(.*?)\s*</span>'
addr_regex = r'<dd id="ctl00_phMainBody_divQuickAddress">.*?</span>.*?</span>\s*(.*?)\s*</dd>'
ein_regex = r'<dd id="ctl00_phMainBody_divQuickEin">(.*?)</dd>'
url_regex = r'<dd id="ctl00_phMainBody_divQuickWeb"><a id="ctl00_phMainBody_aQuickUrl" href="(.*?)"'
primary_regex = r'<dd id="ctl00_phMainBody_divPrimaryOrganizationSubType">\s*(\w*)'
secondary_regex = r'<dd id="ctl00_phMainBody_divSecondaryOrganizationSubType">\s*(\w*)'
tertiary_regex = r'<dd id="ctl00_phMainBody_divTertiaryOrganizationSubType">\s*(\w*)'
revenue_regex = r'Total\s+Revenue</th>\s*<td>(.*?)</td>'
expense_regex = r'Total\s+Expenses</th>\s*<td>(.*?)</td>'
fye_regex = r'Fiscal Year Ending:\s*<span class="date">\s*\w+\s+\w+,\s+(\w+)'
ruling_regex = r'<dd id="ctl00_phMainBody_divRulingYear">\s*(\d+)'
population_regex = r'<dd id="id="ctl00_phMainBody_rptPrograms_ctl00_ddTarget">\s*(.*?)\s*</dd>'
desc_regex = r'<div id="ctl00_phMainBody_rptPrograms_ctl00_pProgDesc" class="html-snippet>\s*(.*?)\s*</div>\s*<p class="label">\s*Program Long-Term Success'
mission_regex = r'Mission Statement</h3>\s*<div class="html-snippet">\s*(.*?)</div>'
contact_regex = r'<dd id="ctl00_phMainBody_divContactName">\s*(.*?)\s*</dd>'
email_regex = r'<dd id="ctl00_phMainBody_divContactEmail">\s*<a href="mailto:(.*?)"'
title_regex = r'<dd id="ctl00_phMainBody_divContactTitle">\s*(.*?)\s*</dd>'
phone_regex = r'<dd id="ctl00_phMainBody_divContactPhone">\s*(.*?)\s*</dd>'

headers = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
scrape_delay = 0.1

# Connect to database
db = pymongo.Connection('localhost').guidestar
db.to_search.remove()
db.searched.remove()
db.to_fetch.remove()
db.fetched.remove()
db.to_scrape.remove()
db.results.remove()
to_search = db.to_search
searched = db.searched
to_fetch = db.to_fetch
fetched = db.fetched
to_scrape = db.to_scrape
results = db.results

# Raw html results
html = []

# Scraped results
data = {}

br = mechanize.Browser()
br.addheaders = headers
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

def main():
    
    login()
    create_searches()
    do_searches()
    fetch_search_results()
    scrape_search_results()
    write_results()

def login():
    time.sleep(scrape_delay)
    br.open(login_url)
    br.set_cookie('.gifAuth=')
    br.set_cookie('ASP.NET_SessionId=')
    br.set_cookie('Persistent_id_GccFfvWdeXaVUW=')
    br.set_cookie('Session_GccFfvWdeXaVUW=')
    br.select_form('aspnetForm')
    # The email/password are probably not needed if you have the cookies set
    #br[login_email] = ''
    #br[login_password] = ''
    response = br.submit()

def create_searches():
    print "Creating searches"
    for keyword in keywords:
        for income in incomes:
            print '    adding search %s, %s, %s, %s' % (
                keyword, income[0], income[1], ''
            )
            params = {
                'keyword':keyword
                , 'min_income': income[0]
                , 'max_income': income[1]
                , 'category': ''
            }
            to_search.insert({'params':params})
    return
    for income in incomes:
        print '    adding search %s, %s, %s, %s' % (
            '', income[0], income[1], 'R26'
        )
        params = {
            'keyword':''
            , 'min_income': income[0]
            , 'max_income': income[1]
            , 'category': 'R26'
        }
        to_search.insert({'params':params})

def do_searches():
    print "Doing searches"
    for query in to_search.find():
        params = query['params']
        if searched.find(params).count() == 0:
            search(params)
            searched.insert(params)
        else:
            print "Search cached: %s, %s, %s, %s" % (
                params['keyword']
                , params['min_income']
                , params['max_income']
                , params['category'])

def search(query):
    print "Doing search: %s, %s, %s, %s" % (
        query['keyword']
        , query['min_income']
        , query['max_income']
        , query['category'])
    # Initialize a headless browser and load the page
    time.sleep(scrape_delay)
    response = br.open(search_url)
    # Submit the form
    br.select_form('aspnetForm')
    br[state_name] = ['MA', 'CA']
    br[keyword_name] = query['keyword']
    br[min_income_name] = query['min_income']
    br[max_income_name] = query['max_income']
    br.set_cookie('.gifAuth=E8AA5AFCCF481F9647E5ADE1AFABD0476DF014ADEFF14172B582521E925F8F65CC1A66A2BA7D4D840C2345E075DE457C223E506E140B4CBCBCD0F80C0C29190735698B791032975DA8497CBEC07EF3EAAEED85E1EC7C3EBD0B8A9EF7E8D29206C07E07863B7B0B46D071CD21DA0F7EA96F5F8398')
    br.set_cookie('ASP.NET_SessionId=ol4nuhlipv32ynuicy0m2ztb')
    br.set_cookie('Persistent_id_GccFfvWdeXaVUW=0CAAB756D13C:1394127144')
    br.set_cookie('Session_GccFfvWdeXaVUW=0CACC5933B80')
    if len(query.get('category', '')) > 0:
        br[category_name] = query['category']
    response = br.submit()
    html = response.read()
    response.close()
    # Parse the results
    page = 1
    while True:
        print "    page %d" % page
        orgs = re.findall(r'<!-- org name -->.*?href="(.+?)"', html, re.DOTALL)
        for org in orgs:
            if fetched.find({'url':base_url + org}).count() == 0:
                to_fetch.insert({'url':base_url + org})
        # Try to go to the next page
        page += 1
        next_id = 'ctl00$phMainBody$repPaginationTop$ctl%02d$lbPage' % page
        if len(re.findall(re.escape(next_id), html, re.MULTILINE)) > 0:
            br.select_form('aspnetForm')
            br.form.find_control('__EVENTTARGET').readonly = False
            br['__EVENTTARGET'] = next_id
            response = br.submit()
            html = response.read()
            response.close()
        else:
            print 'No more pages'
            break

def fetch_search_results():
    print "Fetching results"
    while to_fetch.count() > 0:
        print "    Results left to fetch: %d" % to_fetch.count()
        search_result = to_fetch.find_one()
        to_fetch.remove(search_result)
        url = search_result['url']
        to_scrape.insert({'html':get_page(url)})
        fetched.insert({'url':url})

def scrape_search_results():
    print "Scraping results"
    while to_scrape.count() > 0:
        print "    Results left to scrape: %d" % to_scrape.count()
        page = to_scrape.find_one()
        results.insert(scrape(page['html']))
        to_scrape.remove(page)

def get_page(url):
    print "Fetching: %s" % url
    time.sleep(scrape_delay)
    response = br.open(url.encode('utf-8'))
    html = response.read()
    response.close()
    return html
    
def scrape(html):
    datum = {}
    # Scrape
    try:
        datum['name'] = re.search(name_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['ein'] = re.search(ein_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['addr1'] = re.search(addr1_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['addr2'] = re.search(addr2_regex, html, re.DOTALL).group(1)
        datum['addr2'] = re.sub(r'<br\s*/>', ' ', datum['addr2'], flags=re.MULTILINE)
    except AttributeError:
        pass
    try:
        datum['addr3'] = re.search(addr_regex, html, re.DOTALL).group(1)
        datum['addr3'] = re.sub(r'^\s*$', '', datum['addr3'], flags=re.MULTILINE)
        datum['addr3'] = re.sub(r'^\s*', '', datum['addr3'], flags=re.MULTILINE)
        datum['addr3'] = re.sub(r'\s*$', '', datum['addr3'], flags=re.MULTILINE)
        datum['addr3'] = re.sub(r'\r\n?|\n', ',', datum['addr3'], flags=re.MULTILINE)
        datum['addr3'] = re.sub(r'&nbsp;*', ' ', datum['addr3'], flags=re.MULTILINE)
        datum['addr3'] = re.sub(r'<br\s*/>', ' ', datum['addr3'], flags=re.MULTILINE)
    except AttributeError:
        pass
    try:
        datum['contact'] = re.search(contact_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['title'] = re.search(title_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['email'] = re.search(email_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['phone'] = re.search(phone_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['primary'] = re.search(primary_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['secondary'] = re.search(secondary_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['tertiary'] = re.search(tertiary_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['revenue'] = re.search(revenue_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['expense'] = re.search(expense_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['url'] = re.search(url_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['fye'] = re.search(fye_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['ruling date'] = re.search(ruling_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['population'] = re.search(population_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['desc'] = re.search(desc_regex, html, re.DOTALL).group(1)
    except AttributeError:
        pass
    try:
        datum['mission'] = re.search(mission_regex, html, re.DOTALL).group(1)
        datum['mission'] = re.sub(r'\r\n?|\n', ',', datum['mission'], flags=re.MULTILINE)
    except AttributeError:
        pass
    return datum

def write_results():
    data = {}
    for result in results.find():
        try:
            data[result['ein']] = result
        except KeyError:
            print "No EIN: %s" % result
    with open('results.csv', 'wb') as f:
        fields = [
            'name'
            , 'addr1'
            , 'addr2'
            , 'addr3'
            , 'ein'
            , 'url'
            , 'contact'
            , 'title'
            , 'email'
            , 'phone'
            , 'primary'
            , 'secondary'
            , 'tertiary'
            , 'revenue'
            , 'expense'
            , 'fye'
            , 'ruling date'
            , 'population'
            , 'desc'
            , 'mission']
        f.write('\t'.join(fields))
        f.write("\n")
        for datum in data.values():
            f.write('\t'.join([datum.get(field,'').encode('utf8') for field in fields]))
            f.write("\n")

if __name__ == '__main__':
    main()
    
