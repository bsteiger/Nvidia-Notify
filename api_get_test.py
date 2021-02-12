from time import perf_counter, sleep
from statistics import mean
import requests
from dotenv import load_dotenv
from os import path, getenv, system
import random
from pprint import pprint
from notifier import *
import logging

load_dotenv()
MIN_DELAY = int(getenv('MIN_DELAY'))
MAX_DELAY = int(getenv('MAX_DELAY'))
display_names = [
    "EVGA RTX 3060 Tix", "EVGA RTX 3060 Tip", "NVIDIA GEFORCE RTX 3060 TI",
    "PNY GeForce RTX 3070 8GB UPRISING Dual Fan"
]
get_times = []

site_props = {
    "https://bestbuy.com": {
        "keyword": "cart.svg",
        "alert": True,
        "method": "GET_SELENIUM"
    },
    "https://www.newegg.com": {
        "keyword": "Add to cart",
        "alert": True,
        "method": "GET_URLLIB",
    },
    "https://www.bhphotovideo.com": {
        "keyword": "Add to Cart",
        "alert": True,
        "method": "GET_URLLIB",
    },
    "https://www.evga.com": {
        "keyword": "AddCart",
        "alert": True,
        "method": "GET_URLLIB",
    },
    "https://store.asus.com": {
        "keyword": ">Buy Now<",
        "alert": True,
        "method": "GET_URLLIB",
    }
}


def check_site(site):
    "Checks the site url based on the properties given, sets off an alert if it's in stock"
    print(
        f"\tChecking{' ' + site.get('name') if site.get('name') is not None else ''}..."
    )
    try:
        if site.get('method') == Methods.GET_SELENIUM:
            if not USE_SELENIUM:
                return
            html = selenium_get(site.get('url'))
        elif site.get('method') == Methods.GET_API:
            if 'nvidia' in site.get('name').lower():
                nvidia_get(site.get('url'), site.get('api'))
            return
        else:
            html = urllib_get(site.get('url'))
    except Exception as e:
        print("\t\tConnection failed...")
        print("\t\t{}".format(e))
        return
    keyword = site.get('keyword')
    alert_on_found = site.get('alert', True)
    index = html.upper().find(keyword.upper())
    if alert_on_found and index != -1:
        alert(site)
    elif not alert_on_found and index == -1:
        alert(site)
    return


def main():
    "Main Function Block"
    url = ""
    api_url1 = "https://api.nvidia.partners/edge/product/search?page=1&limit=900&locale=en-us&sorting=lp&category=GPU&category_filter=GPU~77,Laptop~139,Studio-Laptop~13,NVLINKS~1"
    retailers = nvidia_partners_get(display_names, api_url1)
    for retailer in retailers:
        search_nvidia_partner(retailer)


def search_nvidia_partner(retailer):
    "Check on the retailer's website for stock based on info returned by the NVIDIA Partners API"
    retailer_name = retailer.get("retailerName")
    purchase_link = retailer.get("purchaseLink")
    product_title = retailer.get("productTitle")
    if site_props.get(retailer_name) is None:
        print(
            f"\t{retailer_name} fetch from Nvidia Partner API is not supported\n"
        )
        return
    name = f"{retailer.get('productTitle')} at {purchase_link}"
    site = {
        **site_props.get(retailer_name), "url": purchase_link,
        "name": name
    }
    check_site(site)
    return


def sleep_random_length(base_sleep=1,
                        min_delay=MIN_DELAY,
                        max_delay=MAX_DELAY):
    "Sleep a random length of time"
    total_sleep = base_sleep + random.uniform(min_delay, max_delay)
    sleep(total_sleep)


def nvidia_partners_get(display_names, api_url) -> list:
    """Returns a list of retailer product dicts from the NVIDIA Partners API
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

    # find the product we want
    nvidia_api_result = []
    print(f"{len(products)} Products from API:")
    for product in products:
        product_title = product.get("productTitle")

        print(product_title)
        for retailer in product.get("retailers"):
            print(f'\tRetailer Name: {retailer.get("retailerName")}')
            # print(f'\tPurchase Link: {retailer.get("purchaseLink")}')
            # print(
            #     f'\tDirect Purchase Link: {retailer.get("directPurchaseLink")}'
            # )

        # if product_title.lower() in [name.lower() for name in display_names]:
        if 1 == 1:
            nvidia_api_result.extend(product.get("retailers"))

    print(f"{len(nvidia_api_result)} matching products found")
    return nvidia_api_result


if __name__ == "__main__":
    main()