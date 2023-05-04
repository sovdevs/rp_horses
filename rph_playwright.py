import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from collections import OrderedDict
from datetime import datetime
import pytz
import os
import csv
import polars as pl
import time
import pyarrow as pa

tz = pytz.timezone('Europe/Berlin')
tztoday = datetime.now(tz)

async def get_connections(soup):
    connections = []
    conns = {}

    uls = soup.find_all('ul', class_='hp-details__owners-list')

    regex = r"([a-zA-Z& ]+) until (\d{1,2} [a-zA-Z]{3} \d{4})"
    prevOwners = []
    for ul in uls:
        s = ul.get_text().strip()
        matches = re.findall(regex, s)
        # date_tz = tz.localize(date)
        # SPLIT TJESE NTP OWNER1 OWNER2 etc
        prevOwners = [{'name': match[0], 'dateTo': match[1]}
                      for match in matches]
        prevOwners2 = [{'name': match[0], 'dateTo': tz.localize(
            datetime.strptime(match[1], '%d %b %Y'))} for match in matches]
        # for i,po in enumerate(prevOwners2):
        #     f'prevOwner{i+1}_name' = po['name']
        #     f'prevOwner{i+1}_dateTo' = po['dateTo']

    hdivs = soup.find_all('dd', class_='pp-definition__description')

    progLinks = []
    connLinks = []
    for dt in hdivs:
        progLink = dt.find(['a'], attrs={
                           'class': 'ui-link ui-link_table js-popupLink hp-horseDefinition__link'})
        connLink = dt.find(
            ['a'], attrs={'class': 'ui-link ui-link_table js-popupLink'})
        if progLink:
            l_ = progLink.get('href')
            # print(l_)
            progLinks.append(l_)
        # returns SIRE DAM DAMSIRE in this order!
        if connLink:
            l_ = connLink.get('href')
            # print(l_)
            connLinks.append(l_)
        # try:
        #    href = dt.find_next_sibling('a', ).get('href', None)
        #    print(href)
        # except AttributeError as e:
        #     print("ERR:", e)
    if len(progLinks) == 3:
        sireU, damU, damSireU = progLinks
        sireId = None
        damId = None
        damSireId = None
        if "horse" in sireU:
            sireId = int(sireU.split("/")[-2])
        if "horse" in damU:
            damId = int(damU.split("/")[-2])
        if "horse" in damSireU:
            damSireId = int(damSireU.split("/")[-2])
    else:
        sireU = ""
        damU = ""
        damSireU = ""

    dts = soup.find_all('dt', class_='pp-definition__term')
    for dt in dts:
        _text = dt.get_text().strip()
        # print(_text)
        if 'yo' in _text:
            horseStats = dt.find_next_sibling('dd').find(
                'span').get_text().strip().replace('(', "").replace(")", "")
            try:
                hStats = horseStats.split(" ")
                dob = hStats[0]
                color = hStats[1]

                gender = hStats[2]

            except (ValueError, IndexError) as e:
                dob = ""
                color = ""
                gender = ""
                print("Error:", e)
        if 'Breeder:' in _text:
            breederName = dt.find_next_sibling('dd').get_text().strip()
            conns['breederName'] = breederName.lower()
        else:
            breederName = 'Unknown'
        if 'Trainer:' in dt.get_text():
            href = dt.find_next_sibling('dd').find('a').get('href')
            conns['trainerUrl'] = href
            try:
                parts = href.split("/")
                trainer_id = int(parts[-2])
                trainer_name = parts[-1]
                name_parts = trainer_name.split("-")
                trainer_name_formatted = " ".join(
                    [part.capitalize() for part in name_parts])
            except (ValueError, IndexError) as e:
                # Handle exceptions that may occur during conversion or indexing
                trainer_id = 'Unknown'
                trainer_name = 'Unknown'
                print("Error:", e)

        siresSeen = 0
        damSireregex = r"\bDam's Sire:\b"
        if re.match(damSireregex, dt.get_text()):
            dshref = dt.find_next_sibling('dd').find('a').get('href')
            # print("matched", dshref)
        # if "Dam's Sire" in dt.get_text():
        #     shref = dt.find_next_sibling('dd').find('a').get('href')
        #     print(shref)
        #     conns['damsireUrl'] = shref

        if "Sire:" in dt.get_text():
            siresSeen += 1
            shref = dt.find_next_sibling('dd').find('a').get('href')
            # conns[f'sireUrl_{siresSeen}'] = shref
            try:
                parts = shref.split("/")
                sireId = int(parts[-2])
                # conns[f'sireId_{siresSeen}'] = sireId

            except (ValueError, IndexError) as e:
                sireId = ""

        if 'Owner:' in dt.get_text():
            href = dt.find_next_sibling('dd').find('a').get('href')
            try:
                parts = href.split("/")
                owner_id = int(parts[-2])
                owner_name = parts[-1]

                name_parts = owner_name.split("-")
                owner_name_formatted = " ".join(
                    [part.capitalize() for part in name_parts])
            except (ValueError, IndexError) as e:
                # Handle exceptions that may occur during conversion or indexing
                owner_id = 'Unknown'
                owner_name = 'Unknown'
                currentOwner = {}
                print("Error:", e)
            today = datetime.today().strftime('%d %b %Y')
            currentOwner = {}
            currentOwner['name'] = owner_name_formatted
            currentOwner['url'] = href
            currentOwner['dateTo'] = today
            # print(currentOwner)
            prevOwners.append(currentOwner)
            if gender == "g":
                isGelded = True
            else:
                isGelded = False
            if color == "gr":
                isGray = True
            else:
                isGray = False
            if gender in ['m', 'f']:
                isFemale = True
            else:
                isFemale = False

            co = {'name': currentOwner['name'], 'dateTo': tz.localize(
                datetime.strptime(currentOwner['dateTo'], '%d %b %Y'))}
            prevOwnerArray = []
            prevOwnerArray.append(co)
            if len(prevOwners) == 2:
                po = {'name': prevOwners[1]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[1]['dateTo'], '%d %b %Y'))}
                prevOwnerArray.append(po)
                prevOwnerArray = sorted(
                    prevOwnerArray, key=lambda k: k['dateTo'], reverse=True)
            if len(prevOwners) == 3:
                po1 = {'name': prevOwners[1]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[1]['dateTo'], '%d %b %Y'))}
                po2 = {'name': prevOwners[2]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[2]['dateTo'], '%d %b %Y'))}
                prevOwnerArray.append(po1)
                prevOwnerArray.append(po2)
                prevOwnerArray = sorted(
                    prevOwnerArray, key=lambda k: k['dateTo'], reverse=True)
            if len(prevOwners) == 4:
                po1 = {'name': prevOwners[1]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[1]['dateTo'], '%d %b %Y'))}
                po2 = {'name': prevOwners[2]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[2]['dateTo'], '%d %b %Y'))}
                po3 = {'name': prevOwners[3]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[3]['dateTo'], '%d %b %Y'))}
                prevOwnerArray.append(po1)
                prevOwnerArray.append(po2)
                prevOwnerArray.append(po3)
                prevOwnerArray = sorted(
                    prevOwnerArray, key=lambda k: k['dateTo'], reverse=True)
            if len(prevOwners) == 5:
                po1 = {'name': prevOwners[1]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[1]['dateTo'], '%d %b %Y'))}
                po2 = {'name': prevOwners[2]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[2]['dateTo'], '%d %b %Y'))}
                po3 = {'name': prevOwners[3]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[3]['dateTo'], '%d %b %Y'))}
                po4 = {'name': prevOwners[4]['name'], 'dateTo': tz.localize(
                    datetime.strptime(prevOwners[4]['dateTo'], '%d %b %Y'))}
                prevOwnerArray.append(po1)
                prevOwnerArray.append(po2)
                prevOwnerArray.append(po3)
                prevOwnerArray.append(po4)
                # sort by dateTo
                prevOwnerArray = sorted(
                    prevOwnerArray, key=lambda k: k['dateTo'], reverse=True)

            conns = {'breederName': breederName, 'ownerId': owner_id, 'trainerId': trainer_id, 'trainerName': trainer_name_formatted,
                     'dob': dob, 'color': color, 'gender': gender, 'prevOwners': prevOwnerArray, 'progLinks': progLinks, 'connLinks': connLinks, 'sireU': sireU, 'damU': damU, 'damSireU': damSireU, 'sireId': sireId, 'damId': damId, 'damSireId': damSireId,
                     'isGray': isGray, 'isFemale': isFemale, 'isGelded': isGelded,  'retrievedAt': tztoday}
            print(conns)
            connections.append(conns)
    return connections

async def get_text_from_url(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        # text = soup.get_text()
        connections = await get_connections(soup)
        # extract id from URL using regular expression
        id_match = re.search(r'/horse/(\d+)/', url)
        if connections and id_match:
            horseId = id_match.group(1)
            connections[0]['horseId'] = horseId
        # extract name from URL using regular expression
        url_parts = url.split("/")
        try:
            _horseName = url_parts[-2]
        except IndexError:
            _horseName = url
        connections[0]['horseName'] = _horseName
        orderedConnections = OrderedDict(
            sorted(connections[0].items(), key=lambda x: x[0], reverse=True))
        await browser.close()
        return dict(orderedConnections)




if __name__ == "__main__":

    hurls = [] # <- inputs
    results = []
 

    start_time = time.time()
    for i, h in enumerate(hurls):
        # res = asyncio.get_event_loop().run_until_complete(get_text_from_url(url))
        res = asyncio.run(get_text_from_url(h))
        results.append(res)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time, " seconds")
    print(len(results))
    print(results)  # list of objects

    parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
    rp_horses_file_path = os.path.join(parent_dir, "data/horses/test_horseData.csv")
    with open(rp_horses_file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        if os.path.getsize(rp_horses_file_path) == 0:
            writer.writeheader()
        writer.writerows(results)
