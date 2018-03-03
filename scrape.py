import urllib.request
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import os, sys



"""Website to scrape: http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases 
Data format: Excel 
Fields: Disease name - Image link - Origin - See if you can identify the pest - Check what can legally come into Australia - Secure any suspect specimens 
Output data: 
- Submit the extracted Excel data 
- Submit your code 

Bonus points: 
- Download the images programmatically and link them in the Excel sheet locally. 
- Host the data back as a web page using the data from excel. """



"""Take url as argument and returns BeautifulSoup."""
def get_soup(url):
    user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'}
    response = requests.get(url, headers=user_agent)
    soup = bs(response.content, "lxml")
    return soup



class Write(object):
    """Writes the data to excel and creates webpages for every disease"""
    def __init__(self, disease_name, local_images,origin,identify_the_pest,legally_come_into_australia, suspect_specimens, image_links):
        self.disease_name =  disease_name
        self.local_images = local_images
        self.origin = origin
        self.identify_the_pest = identify_the_pest
        self.legally_come_into_australia = legally_come_into_australia
        self.suspect_specimens = suspect_specimens
        self.image_links = image_links

    def to_excel(self):
        df = pd.DataFrame()
        df['disease_name'] = self.disease_name
        df['origin'] = self.origin
        df['local_images'] = self.local_images
        df['image_links'] = self.image_links
        df['identify_the_pest'] = self.identify_the_pest
        df['legally_come_into_australia'] = self.legally_come_into_australia
        df['suspect_specimens'] = self.suspect_specimens
        writer = pd.ExcelWriter('leancrop.xlsx')
        df.to_excel(writer,'Sheet1')
        writer.save()

    def to_html(self):
        df = pd.read_excel('leancrop.xlsx')
        """
        df['disease_name']
        df['image_links']
        df['origin']
        df['identify_the_pest']
        df['legally_come_into_australia']
        df['suspect_specimens']
        """

        for i in range(len(df.index)):

            f = open(df['image_links'][i].split('/')[-1].split('.jpg')[0]+'.html','w+')

            html = """
            <html>
            <head></head>
            <body>
            
            <h1>"""+df['disease_name'][i]+"""</h1>
            
            <img src="""+df['local_images'][i]+""">
            </br></br>
            <strong>origin:</strong>"""+df['origin'][i]+"""
            </br></br>
            <strong>see if you can identify the pest</strong>
            <p>"""+df['identify_the_pest'][i]+"""</p>
            </br></br>
            <strong>Check what can legally come into australia</strong>
            <p>"""+df['legally_come_into_australia'][i]+"""</p>
             </br></br>
            <strong>secure any suspect specimens</strong>
            <p>"""+df['suspect_specimens'][i]+"""</p>
            </body>
            </html>"""

            f.write(html)
            f.close()

class Scrape(object):
    """fethes every field"""
    def __init__(self, soup):
        self.soup = soup

    def links(self):
        homepage_url = "http://www.agriculture.gov.au"
        atags = self.soup.find('ul', class_="flex-container").find_all('a')
        links = [homepage_url+atag['href'] for atag in atags if atag['href'].startswith('/')]
        return links


    def image(self):
        homepage_url = "http://www.agriculture.gov.au"
        try:
            image_url=  homepage_url + self.soup.find('div', class_="pest-header-image").find('img')['src']
            urllib.request.urlretrieve(image_url, image_url.split('/')[-1])
        except:
            try:
                image_url = homepage_url + self.soup.find('div', id="content_div_2393636").find('img')['src']
                urllib.request.urlretrieve(image_url, image_url.split('/')[-1])
            except:
                image_url = '/no image'


        return os.getcwd()+'/'+image_url.split('/')[-1],image_url

    def origin(self):

        try:
            origin = [strong.next_sibling for strong in self.soup.find('div', class_="pest-header-content").find_all('strong') if 'Origin' in strong.text]
        except:
            origin = ['']
        return origin[0]

    def disease_name(self):
        try:
            disease_name = self.soup.find('div', class_="pest-header-content").find('h2').text
        except:
            try:
                disease_name = self.soup.find('div', class_="page-content full-width").find('h1').text
            except:
                disease_name = 'no data'

        return disease_name

    def identify_the_pest(self):
        try:
            ptags = self.soup.find_all('h3',class_="trigger")[0].find_next('div', class_="hide").find_all('p')
            para = ''
            for p in ptags:
                para +=p.text.strip().replace('\r\n','')
            print(para)
        except:
            para = 'no data'
        return para

    def legally_come_into_australia(self):
        try:
            ptags = self.soup.find_all('h3',class_="trigger")[1].find_next('div', class_="hide").find_all('p')
            para = ''
            for p in ptags:
                para +=p.text.strip().replace('\r\n','')
            print(para)
        except:
            para = 'no data'
        return para

    def suspect_specimens(self):
        try:
            ptags = self.soup.find_all('h3',class_="trigger")[2].find_next('div', class_="hide").find_all('p')
            para = ''
            for p in ptags:
                para +=p.text.strip().replace('\r\n','')
            print(para)
        except:
            para = ''
        return para



def run(url):


    local_images = []
    origin = []
    identify_the_pest = []
    legally_come_into_australia = []
    suspect_specimens = []
    disease_name = []
    image_links = []


    """fetch given page then 
    fetch all links of diseases from that page"""
    soup = get_soup(url)
    scrape = Scrape(soup)
    links = scrape.links()


    """for each disease fetch its name, origin, etc"""
    for link in links:

        print(link)

        soup = get_soup(link)
        scrape = Scrape(soup)

        if scrape.disease_name() != 'no data':

            disease_name.append(scrape.disease_name())

            suspect_specimens.append(scrape.suspect_specimens())

            image = scrape.image()
            local_images.append(image[0])
            image_links.append(image[1])

            origin.append(scrape.origin())

            legally_come_into_australia.append(scrape.legally_come_into_australia())

            identify_the_pest.append(scrape.identify_the_pest())


    """write the data(in lists format) to excel(fields) """
    write = Write(disease_name, local_images,origin,identify_the_pest,legally_come_into_australia, suspect_specimens, image_links)
    write.to_excel()
    write.to_html()

def main():
    url= "http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases"
    """driver function of the program"""
    run(url)

if __name__ == '__main__':
    main()
