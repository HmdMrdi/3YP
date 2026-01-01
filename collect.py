# Feature to be collected
# nb_hyperlinks - no. of hyperlinks
# ratio_intHyperlinks - ration of internal hyperlinks
# ratio_extHyperlinks - ibid external
# ratio_nullHyperlinks - ibid null
# nb_extCSS - no. of external CSS

# NOTE: not implemented - may take a long time to run if several hyperlinks - will try and only gather static DOM related data
# ratio_intErrors - ratio of internal hyperlinks that are errors - NOTE: bs4 and requests, raise_for_status each website - count no. of errors
# ratio_extErrors - ibid external

# login_form - presence of login form
# external_favicon - presence of external favicon

# links_in_tags - presence of hyperlinks in <script> <style> ... tags
# submit_email - email submissiosn in forms
# ratio_intMedia
# ratio_extMedia
# sfh
# iframe
# popup_window
# safe_anchor - presence of safe anchors
# onmouseover - present of onmouseover eventhandler
# right_click - right click disabled
# empty_title - self-explanatory
# DOM depth - depth of the DOM tree
# 

import requests
import cloudscraper
from bs4 import BeautifulSoup, NavigableString
import csv
import urllib3

def collect_features(url: str):
    # to prevent 403 errors 
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0'
        # 'User-Agent': 'ResearcherBot/1.0 (hmphpremium@gmail.com)'
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    }


    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # NOTE: cloudscraper doesnt work either... selenium?
        scraper = cloudscraper.CloudScraper()
        response = scraper.get(url,headers=headers, timeout=10)

        #response = requests.get(url,headers=headers,verify=False, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        
        #link related data capture NOTE: Consider taking log of total count as well may be useful
        null_link_count = external_link_count = internal_link_count = 0
        hyperlinks = soup.find_all('a')
        for link in hyperlinks:
            href = link.get('href')
            if (href == None) or (len(href) == 0):
                null_link_count += 1
            elif href.startswith('http') and href not in url:
                external_link_count += 1
            elif href in url:
                internal_link_count += 1


        link_count = len(hyperlinks)
        print(f'internal = {internal_link_count} external = {external_link_count} null = {null_link_count}')
        ratio_intHyperlinks = (internal_link_count/link_count)
        ratio_extHyperlinks = (external_link_count/link_count)
        ratio_nullHyperlinks = (null_link_count/link_count)

        # styling
        nb_extCSS = 0
        styling = soup.find_all('link', rel='stylesheet')
        for style in styling:
            href = (style.get('href'))
            if href.startswith('http'):
                nb_extCSS += 1

            
        # login form and favicon
        login_form = 0
        login_form: int
        all_forms = soup.find_all('form')
        for form in all_forms:
            password_input = soup.find('input', {'type':'password'})
            if password_input:
                login_form = 1
        # server form handler
            handler = form.get('action')
            if handler != None:
                sfh = True
            else:
                sfh = False

        
        #this function is a little unreliable
        favicon:int = 0
        all_favicon = soup.find_all('link', rel="icon")
        #print(f'all: {all_favicon}')
        for icon in all_favicon:
            href = icon.get('href')
            #print(href)
            # if (href.startswith('http')):
            #     favicon += 1
            if ((href and 'http') or (href and 'www.') ) in href:
                favicon+=1
        

        # links in tags
        presence_of_links_in_tags = 0
        all_scripts_styles = soup.find_all(['script', 'style'])
        #print(f'content: {all_scripts_styles} ')
        for tag in all_scripts_styles:
            #print(f'tag content: {tag}')
            tag = str(tag)
            if ('http' in tag) or ('//' in tag):
                print('fruit')
                presence_of_links_in_tags = 1
        
        
        # email submission forms
        all_forms = soup.find_all('form')
        email_submission_forms = 0
        for _ in all_forms:
            email = soup.find('input', {'type':'email'})
            if email:
                email_submission_forms += 1

        
        # ratio_intMedia and extmEDIA
        internal_media_count = external_media_count = 0
        media_tags = soup.find_all(['audio', 'video', 'img', 'source'])
        for media in media_tags:
            media= str(media)
            print(media)
            if ('http' in media) and not (url in media):
                external_media_count +=1
            else:
                internal_media_count +=1

        # iframe
        nb_iframes = len(soup.find_all('iframe'))

        # popup_window
        nb_popup_window = 0
        all_scripts = soup.find_all('script')
        for script in all_scripts:
            script = str(script)
            if 'window.open' in script:
                nb_popup_window +=1


        # get depth - recusrive child 
        def depth(node, current_depth=0) -> int:
            max_depth = current_depth
            for child in node.children:
                #
                # print(f'child types: {type(child)}')
                if isinstance(child, NavigableString):
                    continue
                
                child_depth = depth(child, current_depth+1)
                max_depth = max(max_depth, child_depth)
            return max_depth

        base_nod = soup.html if (soup.html != None) else soup
        page_depth = depth(base_nod)

        result = (url, link_count, ratio_intHyperlinks, ratio_extHyperlinks, ratio_nullHyperlinks, nb_extCSS, login_form,
                   favicon,presence_of_links_in_tags, email_submission_forms, internal_media_count, external_media_count,
                    sfh, nb_iframes, nb_popup_window, page_depth)

        return(result)
    
    except requests.RequestException as e:
        print(f'Error fetching {url}: {e}')
        return(url, None, None)

def main(links: list, filename: str):
    
    #tentative
    header = ['url', 'nb_hyperlinks', 'ratio_intHyperlinks', 'ratio_extHyperlinks','ratio_nullHyperlinks', 'nb_extCSS', 'login_form',
               'favicon','links_in_tags', 'email_submission_forms','internal_media_count', 'external_media_count', 'sfh', 'nb_iframe','nb_popup_window_count',
                 'page_depth']
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for link in links:
            result = collect_features(link)
            writer.writerow(result)
    print(f'Scraping complete: data save to {filename}')

tentative_links = [
    'https://en.wikipedia.org/wiki/University_of_Warwick',
    'https://www.google.com/'
    # 'https://docs.google.com/forms/',
    # 'https://serasa-feirao.github.io/2025/',
    # 'http://express.rakutenglobal.com/'
    # 'https://j206f.xyz/',
    # 'https://ortan.ru/vendor/nesbot/https/verif2.php',
    # 'https://meta-realm-9t6.pages.dev/',
    # 'https://meta-anchorage.pages.dev/',
    # 'https://teppalaakash.github.io/netflix-clone/',
    # 'https://muskan-ahuja567.github.io/Amazon-clone/',
    # 'https://jupiterexchangedapps.pages.dev/',
    # 'https://saloni156.github.io/Amazon-project/'
]

main(tentative_links, 'test.csv')
        