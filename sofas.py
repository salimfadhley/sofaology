import csv
import itertools
import logging
import requests

log = logging.getLogger(__name__)

CLEARANCE_URL = "https://api.sofology.co.uk/api/clearance-stock"

LEATHER_SOFAS_URL = "https://api.sofology.co.uk/api/catalog/v2/Leather?includeExtraLifestyles=true"

def get_clearance_ranges():
    response = requests.get(CLEARANCE_URL)
    assert response.status_code == 200, f"Got status {response.status_code}"
    log.info("Loading all ranges.")

    items = response.json()

    for item in items:
        if item["countOfItems"] > 0:
            yield item


def get_range_url(range_name:str)->str:
    return f"https://api.sofology.co.uk/api/clearance-stock/{range_name}"


def get_clearance_products():
    for range in get_clearance_ranges():
        range_name = range["rangeName"]
        url = get_range_url(range_name)
        range_response = requests.get(url)
        assert range_response.status_code == 200, f"Could not fetch {url}, got status code {range_response.status_code}"
        log.info(f"Fetched {url}")
        range_response_data = range_response.json()["content"]

        try:
            for productBundle in range_response_data["productBundles"]:
                for product in productBundle["products"]:
                    yield product
        except TypeError:
            log.exception("Cannot get data for %s", range_name)

    if False:
        yield None



def main():
    products, products1 = itertools.tee(get_clearance_products())
    with open("clearance.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=next(products1).keys())
        writer.writeheader()
        writer.writerows(products)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    log.info("Starting load!")
    main()
