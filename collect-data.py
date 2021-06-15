#!/usr/bin/python3

from bs4 import BeautifulSoup

def get_shabbat_zmanim():
    with open("zmanim") as fp:
        soup = BeautifulSoup( fp, 'html.parser' )
        
    # The entire page is inside #PAGES_CONTAINER
    for container in soup.find(id='PAGES_CONTAINER'):
        for span in container.find_all('span'):
            print( "span={0}".format( span.text ) )
    
get_shabbat_zmanim()

