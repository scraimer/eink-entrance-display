from pathlib import Path
from bs4 import BeautifulSoup
import sys
import requests

def extract_shabbat_times(html:str):
    soup = BeautifulSoup(html, 'html.parser')

    # Since I've no idea on how the tags are laid out, I'm going to focus on
    # two constants:
    # * "8:30"
    # * The words "צאת השבת"
    eight_thirty = soup.find(lambda tag:tag.name=="span" and "8:30" in tag.text)
    eight_thirty_div = eight_thirty.find_parent("div")
    first_column_div = eight_thirty_div
    print (first_column_div)
    END_OF_SHABBAT_TEXT = "צאת השבת וערבית"
    shabbat_end = soup.find(lambda tag:tag.name=="span" and END_OF_SHABBAT_TEXT in tag.text)
    end_column_div = shabbat_end.find_parent("div")

    parent = first_column_div.parent
    assert parent == end_column_div.parent

    # Find all the children between the first and last columns
    cols = []
    started = False
    for col in parent.children:
        if (not started) and (col == first_column_div):
            started = True
        if started:
            cols.append(col)
        if col == end_column_div:
            break

    def cols_to_pivot_table(cols):
        # Turn the columns into lists of texts
        text_cols = []
        for col in cols:
            if not col:
                continue
            texts = col.findAll(text=True)
            for t in texts:
                t = t.strip()
                #print(f"'>{t}<'")
            text_cols.append([t.strip().replace('\u200b','') for t in col.findAll(text=True)])

        # Pivot the columns into rows
        rows_count = max([len(col) for col in cols])
        rows = []
        for i in range(0,rows_count):
            row = [col[i] if i < len(col) else '' for col in text_cols]
            # Skip rows of empty data
            if all([not x for x in row]):
                continue
            rows.append(row)
        return rows

    # The early shabbat data is in a different DOM layout
    early_shabbat_div = eight_thirty_div.previous_sibling
    early_time = early_shabbat_div.find(lambda tag:":" in tag.text)
    #early_time_parent = early_time.find_parent("div").parent
    #early_time_parent = early_time.find_parent("div")
    early_time_parent = early_time
    et_cols = early_time_parent.find("div")

    rows = [*cols_to_pivot_table(et_cols), *cols_to_pivot_table(cols)]

    # Look for the word "פרשת "
    PARASHAT_TEXT = "פרשת "
    parasha_elem = soup.find(lambda tag:tag.name=="span" and PARASHAT_TEXT in tag.text)
    title_div = parasha_elem.find_parent("div")
    title_lines = title_div.findAll(text=True)
    title_lines = [x for x in title_lines if x.strip()]
    parasha_name = ' '.join(title_lines)
    print(f"Parasha Name: {parasha_name}")

    ### This is the part that hasn't been modified

    TIME_AFTER_SHUL = 'אחרי התפילה'
    rows_keyed = {}
    for row in rows:
        if len(row) == 1 and len(row[0]) == 0:
            continue

        times = []
        names = []
        for v in row:
            v = v.strip()
            if len(v) == 0:
                continue
            elif (v[-3] == ':') or (v == TIME_AFTER_SHUL):
                times.append(v)
            elif len(v) > 0:
                names.append(v)

        if len(names) != 1:
            if len(names) == 2:
                names = [names[0]]
            else:
                print(f"Warning: Expected 1 name but found {len(names)} names (names={names}) in the row: {row} (len={len(row)})")
                continue

        key = names[0]
        if key in rows_keyed:
            print(f"Warning: Duplicate key: {key} from row {row}")

        if len(times) == 0:
            continue

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

if __name__ == "__main__":
    print(scrape_shabbat_items())
