'''
collect_integ - modified and cleaner version of collect.py
any ammendments made (if any) are to optimise being called by
third party applications

is this kind of redundant? For now yes...
'''

import requests
import cloudscraper
from bs4 import BeautifulSoup, NavigableString
import csv
import urllib3
import os

# NOTE: This function is bad practice, consider rewriting -> mostly one big function
def collect_features(url: str, safety_tag: str, local: bool):
    soup=None

    # Reads from local file, when integrating, will need to write to a temp file and then run the function on that
    if local:
        try:
            with open(url, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            soup = BeautifulSoup(content, 'html.parser')
        except Exception as e:
            print(f'error reading local file {url}: {e}')
            return -1
    
    else:
        # Prevent 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
            'Upgrade-Insecure-Requests': '1'
        }


        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # NOTE: Originally used to try to bypass cloudflare protection (for user) doesnt work in practice
            # Fine for practical application, user can manually bypass or just not proceed with flagged sites
            scraper = cloudscraper.CloudScraper()
            response = scraper.get(url,headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f'Error fetching {url}: {e}')
            return(-1)



    try:        
        # Link related data capture
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
        if link_count == 0:
            ratio_intHyperlinks = ratio_extHyperlinks = ratio_nullHyperlinks = 0
        else:
            ratio_intHyperlinks = (internal_link_count/link_count)
            ratio_extHyperlinks = (external_link_count/link_count)
            ratio_nullHyperlinks = (null_link_count/link_count)



        # Styling
        nb_extCSS = 0
        styling = soup.find_all('link', rel='stylesheet')
        for style in styling:
            href = (style.get('href'))
            try:
                if href.startswith('http'):
                    nb_extCSS += 1
            except:
                print(f'href for link: {url} couldnt be processed')
                continue

            

        # Login form and favicon
        sfh:bool = False
        login_form:int = 0

        all_forms = soup.find_all('form')
        for form in all_forms:
            password_input = soup.find('input', {'type':'password'})
            if password_input:
                login_form = 1
        
        # Server Form Handler
            handler = form.get('action')
            if handler != None:
                sfh = True
            else:
                sfh = False

        favicon:int = 0
        all_favicon = soup.find_all('link', rel="icon")
        #print(f'all: {all_favicon}')
        for icon in all_favicon:
            href = icon.get('href')
            try:
                if ((href and 'http') or (href and 'www.') ) in href:
                    favicon+=1
            except:
                print(f'favicon for link: {url} couldnt be processed')
                continue



        # links in tags
        presence_of_links_in_tags = 0
        all_scripts_styles = soup.find_all(['script', 'style'])
        #print(f'content: {all_scripts_styles} ')
        for tag in all_scripts_styles:
            #print(f'tag content: {tag}')
            tag = str(tag)
            if ('http' in tag) or ('//' in tag):
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
            # print(media)
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



        # hovering even handler
        onmouseover_elements = soup.find_all(attrs={"onmouseover": True})
        if onmouseover_elements:
            onmouseover = True
        else:
            onmouseover = False



        # right click disabled -> RCD
        RCD_elements = soup.find_all(attrs={"oncontextmenu": True})
        rcd = True if RCD_elements else False



        # check if empty title
        title_tag = soup.find('title')
        if not title_tag or title_tag == None:
            empty_title = True
        elif title_tag.string == None:
            empty_title = True
        elif title_tag.string == "":
            empty_title = True
        else:
            empty_title = False



        # get depth - recusrive child 
        def depth(node, current_depth=0) -> int:
            max_depth = current_depth
            for child in node.children:
                if isinstance(child, NavigableString):
                    continue
                child_depth = depth(child, current_depth+1)
                max_depth = max(max_depth, child_depth)
            return max_depth
        base_nod = soup.html if (soup.html != None) else soup
        page_depth = depth(base_nod)



        result = (url, safety_tag, link_count, ratio_intHyperlinks, ratio_extHyperlinks, ratio_nullHyperlinks, nb_extCSS, login_form,
                    favicon,presence_of_links_in_tags, email_submission_forms, internal_media_count, external_media_count,
                    sfh, nb_iframes, nb_popup_window, onmouseover, rcd, empty_title, page_depth)

        return(result)
    
    except Exception as e:
        print(f'Feature extraction error for {url} : {e}')
        return -1
    

def collect_live(url: str):
    safety_tag = "NULL"
    local = False
    pass

def collect_file(url: str):
    safety_tag = "NULL"
    local = True
    pass
    
