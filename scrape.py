from pathlib import Path
from bs4 import BeautifulSoup
import sys
import requests

def extract_shabbat_times(html:str):
    html = html.replace(' dir="rtl" style="font-size:25px; line-height:1.2em"','') \
        .replace(' dir="rtl" style="font-size:25px; line-height:1.2em; text-align:justify"','')
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('h1').find_parent('div').find_parent('div')
    # TODO: assert content.data-testid == 'mesh-container-content'

    parasha_name_elems = content.find('h1').find_parent('div').find_next_sibling('div')
    parasha_name = parasha_name_elems.get_text()

    col1 = parasha_name_elems.find_next_sibling('div')
    col2 = col1.find_next_sibling('div')
    col3 = col2.find_next_sibling('div')
    col4 = col3.find_next_sibling('div')

    cols = [col1, col2, col3, col4]
    col_as_lines = [col.get_text().split('\n') for col in cols]
    height = max([len(col) for col in col_as_lines])

    # Pivot the data from columns to rows
    rows = []
    for i in range(height):
        row = [col[i] for col in col_as_lines if len(col) > i]
        row = [v.replace('\u200b','').replace('\xa0','') for v in row]
        rows.append(row)

    TIME_AFTER_SHUL = 'אחרי התפילה'
    rows_keyed = {}
    for row in rows:
        times = []
        names = []
        for v in row:
            v = v.strip()
            if len(v) == 0:
                continue
            elif (v[-3] == ':') or (v == TIME_AFTER_SHUL):
                times.append(v)
            else:
                names.append(v)

        if len(names) != 1:
            print(f"Warning: Expected 1 name but found {len(names)} names in the row: {row}")
            continue

        key = names[0]
        if key in rows_keyed:
            print(f"Warning: Duplicate key: {key} from row {row}")

        rows_keyed[key] = times
        
    return {'parasha_name': parasha_name, 'times': rows_keyed}

def scrape_shabbat_items():
    ZMANIM_URL = 'https://reshitd.wixsite.com/home/zmanim'
    r = requests.get(ZMANIM_URL)
    if r.status_code != 200:
        print(f"HTTP Error {r.status_code} fetching {ZMANIM_URL}")
        sys.exit(1)
    html = r.text
    return extract_shabbat_times(html)

