from requests_html import HTMLSession
from dataclasses import dataclass
from itertools import chain
from concurrent.futures import ThreadPoolExecutor


url_page = "https://gopher1.extrkt.com?paged={}"
url_product = "https://gopher1.extrkt.com/?product="
session = HTMLSession()


@dataclass
class Product:
    name: str
    price: str
    url: str
    sku: str
    category: str
    description: str
    additional_info: str


def get_product_links(page_num: int) -> list:
    product_links = []
    url = url_page.format(page_num)
    response = session.get(url)
    title = response.html.find("h1", first=True).text
    if title != "Shop":
        return []
    links = response.html.absolute_links
    for link in links:
        if url_product in link:
            product_links.append(link)
    return product_links


def parse_product(product_link: str) -> Product:
    prod_page = session.get(product_link)
    # Name
    name = prod_page.html.find("h1", first=True).text
    # Price
    price = prod_page.html.find(
        "span.woocommerce-Price-amount",
        first=True,
    ).text
    # SKU
    sku = prod_page.html.find("span.sku", first=True).text
    # Category
    category = prod_page.html.find("span.posted_in", first=True).text
    category = category.split(":")[-1].strip()
    # Description
    description_div = prod_page.html.find("#tab-description", first=True)
    description = "No description"
    if description_div:
        description = description_div.text.replace("Description\n", "").strip()
    # Additional Info
    additional_info_div = prod_page.html.find(
        "#tab-additional_information",
        first=True,
    )
    additional_info = "No additional information"
    if additional_info_div:
        additional_info = additional_info_div.text.replace(
            "Additional information\n", ""
        ).strip()
    product = Product(
        name=name,
        price=price,
        url=product_link,
        sku=sku,
        category=category,
        description=description,
        additional_info=additional_info,
    )
    print(product)
    return product


def scrape():
    product_links = []
    products = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        product_links = list(
            chain.from_iterable(executor.map(get_product_links, range(1, 13))),
        )
    with ThreadPoolExecutor(max_workers=4) as executor:
        products = list(executor.map(parse_product, product_links))
    print(f"Found {len(products)} products")


if __name__ == "__main__":
    scrape()
