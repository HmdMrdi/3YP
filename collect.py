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

# NOTE: most of the above are based off of an older dataset - mixed with some new feautures not all will be implemented

import requests
import cloudscraper
from bs4 import BeautifulSoup, NavigableString
import csv
import urllib3
import os

def collect_features(url: str, safety_tag: str, local: bool):
    soup=None

    if local:
        try:
            with open(url, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            soup = BeautifulSoup(content, 'html.parser')
            #url = os.path.basename(url)   
        except Exception as e:
            print(f'error reading local file {url}: {e}')
            return -1
    
    else:
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
            # i dont actually care anymore, if it doesnt work just skip -> although means dataset ignores cloudfare protected or cloudflare designated malicious sites
            scraper = cloudscraper.CloudScraper()
            response = scraper.get(url,headers=headers, timeout=10)

            #response = requests.get(url,headers=headers,verify=False, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f'Error fetching {url}: {e}')
            return(-1)

    try:        
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
        # print(f'internal = {internal_link_count} external = {external_link_count} null = {null_link_count}')
        if link_count == 0:
            ratio_intHyperlinks = ratio_extHyperlinks = ratio_nullHyperlinks = 0
        else:
            ratio_intHyperlinks = (internal_link_count/link_count)
            ratio_extHyperlinks = (external_link_count/link_count)
            ratio_nullHyperlinks = (null_link_count/link_count)

        # styling
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

            
        # login form and favicon
        sfh:bool = False
        login_form:int = 0

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
        # if RCD_elements:
        #     rcd = True
        # else:
        #     rcd = False


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
                #
                # print(f'child types: {type(child)}')
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
    

def main(links: list, filename: str, safety_tag: str, local:bool):
    skipped_urls = []
    existing_urls = set()
    header = ['url', 'safety_tag', 'nb_hyperlinks', 'ratio_intHyperlinks', 'ratio_extHyperlinks','ratio_nullHyperlinks', 'nb_extCSS', 'login_form',
               'favicon','links_in_tags', 'email_submission_forms','internal_media_count', 'external_media_count',
                 'sfh', 'nb_iframe','nb_popup_window_count', 'onmouseover', 'right click disabled', 'empty_title', 'page_depth']
    

    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row:
                    existing_urls.add(row[0])

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not (os.path.exists(filename)):
            writer.writerow(header)
        
        for link in links:
            if link not in existing_urls:
                result = collect_features(link, safety_tag, local)
                if result != -1:
                    writer.writerow(result)
                else:
                    print(f'Skipping url due to error: {link}')
                    skipped_urls.append(link)
            else:
                print(f'Skipping duplicate url: {link}')
    


def linkify_the_text_file(link_file):
    links = []
    with open(link_file, 'r', encoding='utf-8') as file:
        for line in file:
            url=line.strip()
            links.append(url)
    return links


def get_local_files(directory):
    locals_path = []
    if os.path.exists(directory):
        for root, _, files, in os.walk(directory):
            for file in files:
                locals_path.append(os.path.join(root,file))
    return locals_path




# file_names = ['gng_links.txt', 'opp_links.txt', 'gpt_links.txt']
# website_tags = ['benign', 'malicious', 'gpt_generated']
# file_names = ['gng_links.txt', 'gpt_links.txt']
# website_tags = ['benign', 'gpt_generated']

# file_names = ['gng_links.txt']
# website_tags = ['benign']
# for x, file in enumerate(file_names):
#     file = linkify_the_text_file(file)
#     main(file, 'website_features.csv', website_tags[x])

# ---------------- local testing ----------------
local_directory = 'AI_html_ground_truth/'
local_html_files  = get_local_files(local_directory)

main(local_html_files, 'website_features.csv', 'gpt_generated', local=True)



        