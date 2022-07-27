from requests import get
from lxml import html
from json import dump
from csv import DictWriter
from math import ceil
from time import time
import asyncio
import aiohttp


HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
              "q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.106 Safari/537.36"}

# test on BMW 5 (all generations for broad selection):
TARGET_URL = "https://cars.av.by/filter?brands[0][brand]=8&brands[0][model]=5865"

# uncomment line below to specify other model (url of search page from AV.BY):
# TARGET_URL = input("Link to specific model >> ")


def parser(url: str, save_as_file: str) -> None:
    """Parses search-page of specific model on AV.BY, saves data to .json/-csv"""

    def total_pages() -> int:
        """Calculates number of pages to go through"""
        
        resp = get(url, headers=HEADERS)
        number_of_results = int(html.fromstring(resp.text).xpath("//h3[@class='listing__title']/text()")[2])
        pages = ceil(number_of_results / 25)
        print(f"Found {number_of_results} results on {pages} pages")
        return pages

    async def parse_page(current_page: int, storage: list) -> None:
        """Extracts information from one given page, saves to storage"""
        
        async with aiohttp.request("GET", url=url + f"&page={current_page}", headers=HEADERS) as response:
            content = await response.text()
            res = html.fromstring(content).xpath("//div[@class='listing__items']")[0]

            def f(name: str):
                """Helper with aim to improve readability of data-collecting block"""
                return {
                    "age": lambda x: int(x.split()[0]),
                    "kms": lambda x: int(x.replace("\xa0", "").replace("\u2009", "").split("км")[0]),
                    "byn": lambda x: int(x.replace("\xa0", "").replace("\u2009", "")[:-2]),
                    "usd": lambda x: int(x.replace("\xa0", "").replace("\u2009", "")[1:-1]),
                    "vol": lambda x: float(x.split()[0]),
                }[name]

            # collecting information:
            links = res.xpath(".//a[@class='listing-item__link']/@href")
            prices_byn = map(f("byn"), res.xpath(".//div[@class='listing-item__price']/text()"))
            prices_usd = map(f("usd"), res.xpath(".//div[@class='listing-item__priceusd']/text()"))
            year = map(f("age"), res.xpath(".//div[@class='listing-item__params']/div[1]/text()"))
            mile = map(f("kms"), res.xpath(".//div[@class='listing-item__params']/div[3]/span/text()"))
            engine_params = res.xpath(".//div[@class='listing-item__params']/div[2]/text()")
            engine_volume = map(f("vol"), engine_params[2::7])
            engine_fuel = engine_params[4::7]

            for c, y, f, v, m, b, u in zip(links, year, engine_fuel, engine_volume, mile, prices_byn, prices_usd):
                storage.append({
                    "link": "https://cars.av.by" + c,
                    "year": y,
                    "engine": v,
                    "fuel": f,
                    "mileage": m,
                    "price_byn": b,
                    "price_usd": u,
                })
            print(f"Processed page {current_page}")

    async def parse_all_pages() -> list:
        """Creates tasks to parse all pages, returns list of results"""
        
        search_result = list()
        await asyncio.gather(*[parse_page(current_page=p,
                                          storage=search_result) for p in range(1, total_pages() + 1)])
        return search_result

    data: list = sorted(asyncio.run(parse_all_pages()), key=lambda x: x["price_usd"], reverse=True)

    with open(f"{save_as_file}.json", "w") as json_fw, open(f"{save_as_file}.csv", "w", newline="") as csv_fw:
        dump(data, json_fw, indent=2)
        writer = DictWriter(csv_fw, data[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerows(data)
    print("Saved to files")


if __name__ == "__main__":
    start_time = time()
    parser(TARGET_URL, "bmw")
    end_time = time()
    print(f"Completed in {round(end_time - start_time, 2)} sec.")
