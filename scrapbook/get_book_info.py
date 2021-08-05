from bs4 import BeautifulSoup
from urllib.request import urlopen


def append_book_general_info(books_table, books_general_info):
    """ajoute les informations generales de chaque livre dans books_general_info"""
    for row in books_table.findAll(
            "li", attrs={"class": "col-xs-6 col-sm-4 col-md-3 col-lg-3"}
    ):
        url = "https://books.toscrape.com/catalogue/" + row.h3.a["href"][9:]
        books_general_info['product_page_urls'].append(url)

        row_name = row.h3.a["title"]
        name = row_name.replace('"', '-')
        name = name.replace('/', '-')
        books_general_info['titles'].append(name)

        image = "https://books.toscrape.com/" + row.img["src"][12:]
        books_general_info['image_urls'].append(image)

        rating = "".join(row.p["class"][1:])
        books_general_info['review_ratings'].append(rating)


def append_books_details(books_table, books_details):
    """ajoute les details de chaque livre dans books_details"""
    urls = []
    for detail_row in books_table.findAll(
            "li", attrs={"class": "col-xs-6 col-sm-4 col-md-3 col-lg-3"}
    ):
        url = "https://books.toscrape.com/catalogue/" + detail_row.h3.a["href"][9:]
        urls.append(url)

    for details_url in urls:

        page = urlopen(details_url)
        soup = BeautifulSoup(page, "html.parser")
        details_table = soup.find("table", attrs={"class": "table table-striped"})
        for detail_row in details_table.findAll("tr"):
            key = detail_row.th.text
            if key in books_details:
                value = detail_row.td.text
                books_details[key].append(value)

        description_table = soup.find("head")
        for p in description_table.findAll("meta", attrs={"name": "description"}):
            row_description = p["content"]
            description = row_description.replace('"', '-')
            books_details['product_descriptions'].append(description)

