import requests
from bs4 import BeautifulSoup
import os
from get_book_info import append_books_details, append_book_general_info

website = "https://books.toscrape.com/index.html"
soup = BeautifulSoup(requests.get(website).content, "html.parser")

categories_table = soup.find("ul", attrs={"class": "nav nav-list"})
category_links = []

for row in categories_table.findAll("li"):
    link = "https://books.toscrape.com/" + row.a["href"]
    if link != "https://books.toscrape.com/catalogue/category/books_1/index.html":
        category_links.append(link)

""" Gère les pages suivantes dans les categories """

for category_link in category_links:
    catalogue_page_urls = [category_link]
    category_name = category_link.split("/")[-2]

    page_number = 2

    while True:
        next_catalogue_page_url = (
                category_link.split("/index")[0] + "/page-" + str(page_number) + ".html"
        )
        request = requests.get(next_catalogue_page_url)

        if request.status_code != 200:
            break

        catalogue_page_urls.append(next_catalogue_page_url)
        page_number += 1

    books_general_info = {
        "product_page_urls": [],
        "titles": [],
        "review_ratings": [],
        "image_urls": [],

    }
    books_details = {
        "UPC": [],
        "Price (incl. tax)": [],
        "Price (excl. tax)": [],
        "Product Type": [],
        "Availability": [],
        "product_descriptions": [],
    }
    for catalogue_page_url in catalogue_page_urls:
        soup = BeautifulSoup(requests.get(catalogue_page_url).content, "html.parser")
        books_table = soup.find("ol", attrs={"class": "row"})

        append_book_general_info(books_table, books_general_info)
        append_books_details(books_table, books_details)


    """créé un nouveau fichier fichier du nom de la categorie"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, category_name)
    try:
        os.makedirs(dest_dir)
    except OSError:
        pass  # already exists
    path = os.path.join(dest_dir, category_name)


    """ecrit le csv par categories"""
    
    with open(f"{category_name}/{category_name}.csv", "w") as f:
        f.write("product_page_url,title,image_url,review_rating,product_description,"
                "universal_product_code,price_including_taxes,price_excluding_taxes,category,availability\n")
        for url, name, image, rating, description, upc, pricetax, pricenotax, cat, available in zip(
            books_general_info['product_page_urls'], books_general_info['titles'], books_general_info['image_urls'],
            books_general_info['review_ratings'], books_details["product_descriptions"],
            books_details["UPC"], books_details["Price (incl. tax)"], books_details["Price (excl. tax)"],
            books_details["Product Type"], books_details["Availability"]
        ):

            f.write(
                f'"{url}","{name}","{image}","{rating}","{description}","{upc}","{pricetax}","{pricenotax}","{cat}",'
                f'"{available}"\n'
            )
            
    """telecharge les images des livres"""

    for image, title in zip(books_general_info["image_urls"], books_general_info["titles"]):
        with open(f"{category_name}/{title}", "wb") as f:
            response = requests.get(image)
            f.write(response.content)

