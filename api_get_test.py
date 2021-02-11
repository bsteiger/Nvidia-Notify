"Testing if the api is broke"
from time import perf_counter, sleep
from statistics import mean
import requests
from dotenv import load_dotenv
from os import path, getenv, system
import random

load_dotenv()
MIN_DELAY = int(getenv('MIN_DELAY'))
MAX_DELAY = int(getenv('MAX_DELAY'))

get_times = []


def main():
    "Main Function Block"
    url = ""
    api_url1 = "https://api.nvidia.partners/edge/product/search?page=1&limit=900&locale=en-us&sorting=lp&category=GPU&category_filter=GPU~77,Laptop~139,Studio-Laptop~13,NVLINKS~1"
    resp = nvidia_partners_get(url, api_url1)


def sleep_random_length():
    base_sleep = 1
    total_sleep = base_sleep + random.uniform(MIN_DELAY, MAX_DELAY)
    sleep(1)


def nvidia_partners_get(_, api_url) -> list:
    """Returns a list of product dicts from the NVIDIA Partners API
    Expected fields this function uses:  
        productTitle: Title of the entry on the NVIDIA page
        purchaseLink: gethatch url that redirects to the purchase url from the retailer
        retailerName: url of retailer
    """
    tic = perf_counter()
    response = requests.get(api_url, timeout=15)
    toc = perf_counter()
    res = response.json()
    print(f"Got the API Json  in {toc - tic:0.4f} seconds")

    # Find the all the product entries, regular and 'featured
    products = res['searchedProducts']['productDetails']
    products.append(res['searchedProducts']['featuredProduct'])

    display_names = [
        "EVGA RTX 3060 Tix", "EVGA RTX 3060 Tip", "NVIDIA GEFORCE RTX 3060 TI"
    ]

    # find the product we want
    nvidia_api_result = []
    print(f"{len(products)} Products from API:")
    for product in products:
        product_title = product.get("productTitle")
        print(product_title)
        if product_title.lower() in [name.lower() for name in display_names]:
            retailers = product.get("retailers")
            for retailer in retailers:
                nvidia_api_result.append(retailer)

    return nvidia_api_result


if __name__ == "__main__":
    main()