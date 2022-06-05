from cgitb import reset
from itertools import product
from math import prod
from pip import main
import requests
from bs4 import BeautifulSoup
import lxml
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

from categories import categories
from config import headers
from models import Product, Category


# Saves categories into DB
def save_categories(session):
    for category in categories:
        new_category = Category(name = category['name'], link = category['link'], vk_id = category['vk_id'])
        session.add(new_category)
    session.commit()


def update_categories(session):
    for category in categories:
        q = session.query(Category).filter_by(name = category['name']).first()
        q.vk_id = category['vk_id']
    session.commit()


# Takes categories from db and saves items
def save_product_links_from_category(session: sessionmaker):
    q = session.query(Category)
    for category in q:
        links = parse_category_page(category.link)
        for link in links:
            if not session.query(Product).filter_by(link=link).first():
                product = Product(category=category.name, link=link)
                session.add(product)
            else:
                print("Already added")
    session.commit()


# Opens category page by link and gets all products links
def parse_category_page(link):
    page = BeautifulSoup(requests.get(url=link, headers=headers).text, 'lxml')
    page_number = 1
    try:
        pagination = page.find('div', class_='module-pagination')
        page_number = int(pagination.find_all('a')[-1].text.strip())
    except Exception as e:
        # print("EXCEPTION:", e)
        pass
    links = []
    if page_number == 1:
        links = get_products_links(links, page)
    else:
        for i in range(page_number):
            page = BeautifulSoup(requests.get(url=link+"?PAGEN_1={}".format(i+1), headers=headers).text, 'lxml')
            links = get_products_links(links, page)
    return links


# Finds all the products links on page
def get_products_links(links: list, page):
    elements = page.find_all('div', class_='catalog_item')
    for element in elements:
        links.append("https://hishnikmarket.ru" + element.find('a', class_='shine').get('href'))
    return links


# Takes all products links from db and gets each product info
def save_products_info(session):
    q = session.query(Product)
    for product in q:
        if not product.name:
            product_info = parse_item_page(product.link)
            product.name = product_info['name']
            product.description = product_info['description']
            product.price = product_info['price']
            product.photo = product_info['photo']
            session.commit()


# Gets all info about product in page
def parse_item_page(link):
    page = BeautifulSoup(requests.get(url=link, headers=headers).text, 'lxml')
    name = page.find('h1').text.strip()
    try:
        description = page.find('div', class_='detail_text').text
    except Exception as e:
        description = name
    try:
        photo = "https://hishnikmarket.ru" + page.find('a', class_='popup_link').get('href')
    except Exception as e:
        photo = "None"  
    try:
        price = page.find('span', class_='price_value').text.replace("руб.","").replace(" ","")
    except Exception as e:
        price = "None"

    item = {
        'name': name,
        'description': description,
        'price': price,
        'photo': photo,
    }
    return item


def update_product(session, product: Product):
    new_item = parse_item_page(product.link)
    product.name = new_item['name']
    product.description = new_item['description']
    product.price = new_item['price']
    product.photo = new_item['photo']
    session.commit()


def main():
    engine = create_engine('sqlite:///hishnik.db', echo=True)
    session = sessionmaker(bind=engine)()
    # links = parse_category_page("https://hishnikmarket.ru/catalog/odezhda-i-obuv/obuv/botinki/")
    # link = "https://hishnikmarket.ru/catalog/odezhda-i-obuv/obuv/botinki/261849/"
    # product = session.query(Product).filter_by(name='Ботинки мужские "Странник" (черные) зима р.').first()
    # update_product(session=session, product=product)
    # save_categories(session=session)
    # save_product_links_from_category(session=session)
    # save_products_info(session=session)
    # print(parse_item_page("https://hishnikmarket.ru/catalog/odezhda-i-obuv/odezhda/kostyumy-kurtki/odezhda-iz-flisa/238189/"))

    # q = session.query(Product).filter_by(name="Test name")
    # print(dir(Product))
    # test = q.first()
    # session.add_all()


if __name__ == '__main__':
    main()
