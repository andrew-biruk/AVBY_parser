from requests import get
from lxml import html
from bs4 import BeautifulSoup as bs
from json import dump
from csv import DictWriter
from math import ceil

URL = "https://cars.av.by/"
HEADERS = {
    "accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Chrome/102.0.0.0"}
params = {
    "bmw": {
        "brands[0][brand]": 8,
        "brands[0][model]": 5865,
        "brands[0][generation]": 4441,
        "page": 1},
    "audi": {
        "brands[0][brand]": 6,
        "brands[0][model]": 5810,
        "brands[0][generation]": 4301,
        "page": 1}}


def parse_av_lxml(target: str, par: dict) -> list[dict]:
    """
    :param target: base URL
    :param par: query parameters for specified model
    :return : JSON/CSV serializable array, which each item contains
    link to car, motor params, year of manufacturing, mileage and price"""
    cars = []

    def parser(lst: list) -> None:
        """parses given page and updates outer scope container with results"""
        req = get(target + "filter", params=par, headers=HEADERS)
        res = html.fromstring(req.text).xpath("//div[@class='listing__items']")[0]

        def f(name: str):
            """helper func with aim to improve readability"""
            funcs = {
                "age": lambda x: int(x.split()[0]),
                "kms": lambda x: int("".join(x.split()[:2])),
                "byn": lambda x: int(x.replace("\xa0", "").replace("\u2009", "")[:-2]),
                "usd": lambda x: int(x.replace("\xa0", "").replace("\u2009", "")[1:-1]),
                "vol": lambda x: float(x.split()[0])}
            return funcs[name]

        # xpath retrieves all occurrences of specified tag (list of all individual links):
        links = res.xpath(".//a[@class='listing-item__link']/@href")

        # separate lists for prices in byn & usd:
        prices_byn = map(f("byn"), res.xpath(".//div[@class='listing-item__price']/text()"))
        prices_usd = map(f("usd"), res.xpath(".//div[@class='listing-item__priceusd']/text()"))

        # separate lists for year of manufacturing & mileage:
        yage = map(f("age"), res.xpath(".//div[@class='listing-item__params']/div[1]/text()"))
        kage = map(f("kms"), res.xpath(".//div[@class='listing-item__params']/div[3]/span/text()"))

        # iterate through engine parameters to get engine volume & fuel type:
        engine_params = res.xpath(".//div[@class='listing-item__params']/div[2]/text()")
        volm = map(f("vol"), engine_params[2::7])
        fuel = engine_params[4::7]

        # combine all the data together:
        for c, y, f, v, m, b, u in zip(links, yage, fuel, volm, kage, prices_byn, prices_usd):
            lst.append({
                "link": target[:-1] + c,
                "year": y,
                "engine": v,
                "fuel": f,
                "mileage": m,
                "price_byn": b,
                "price_usd": u})

    # first request to estimate number of pages to go through:
    test_req = get(target + "filter", params=par, headers=HEADERS)
    pages = ceil(int(html.fromstring(test_req.text).xpath("//h3[@class='listing__title']/text()")[2]) / 25)

    # go through pages:
    for p in range(1, pages + 1):
        par["page"] = p
        parser(cars)

    return cars


def parse_av_bs(target: str, par: dict) -> list[dict]:
    """Parses AV.BY for specific model (dependent on query parameters)
    :param target: base URL
    :param par: query parameters for specified model
    :return : JSON/CSV serializable array, which each item contains
    link to car, motor params, year of manufacturing, mileage and price"""
    cars = []

    def parser(lst: list) -> None:
        """parses target url and updates outer scope container with results"""
        req = get(target + "filter", params=par, headers=HEADERS).text
        res = bs(req, 'html.parser').find_all('div', class_='listing-item__wrap')

        def f(name: str):
            """helper func with aim to improve readability"""
            funcs = {
                "age": lambda x: int(x[0][:4]),
                "kms": lambda x: int("".join([c for c in x[-1] if c.isdigit()])),
                "byn": lambda x: int(x.replace("\xa0", "").replace("\u2009", "")[:-2]),
                "usd": lambda x: int(x.replace("\xa0", "").replace("\u2009", "")[1:-1]),
                "vol": lambda x: float(x[1].split()[0]),
                "gas": lambda x: x[2].strip()}
            return funcs[name]

        for card in res:
            # car individual link:
            link = card.find('a', class_='listing-item__link').get('href')

            # prices in byn & usd:
            price_byn = f("byn")(card.find("div", class_="listing-item__price").text)
            price_usd = f("usd")(card.find("div", class_="listing-item__priceusd").text)

            # iterate through engine parameters:
            other_params = card.find("div", class_="listing-item__params").text.split(",")
            yage = f("age")(other_params)
            kage = f("kms")(other_params)
            volm = f("vol")(other_params)
            fuel = f("gas")(other_params)

        # add the car data to car list:
            lst.append({
                "link": target[:-1] + link,
                "year": yage,
                "engine": volm,
                "fuel": fuel,
                "mileage": kage,
                "price_byn": price_byn,
                "price_usd": price_usd})

    # first request to estimate number of pages to go through:
    test_req = get(target + "filter", params=par, headers=HEADERS)
    number_results = bs(test_req.text, "html.parser").find("h3", class_="listing__title").text.split()[1]
    pages = ceil(int(number_results) / 25)

    # go through pages:
    for p in range(1, pages + 1):
        par["page"] = p
        parser(cars)

    return cars


def write_json_csv(data: list[dict], filename: str) -> None:
    """creates filename.json and filename.csv in project directory"""
    with open(f"{filename}.json", "w") as json_fw, open(f"{filename}.csv", "w", newline="") as csv_fw:
        dump(data, json_fw, indent=2)
        writer = DictWriter(csv_fw, data[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerows(data)


for i in ("bmw", "audi"):
    temp = sorted(parse_av_lxml(URL, params[i]), key=lambda x: x["price_usd"], reverse=True)
    write_json_csv(temp, i)
