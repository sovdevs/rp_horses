



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
