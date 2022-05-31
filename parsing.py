from cgitb import reset
from urllib import response
from wsgiref import headers
from pip import main
import requests
from bs4 import BeautifulSoup
import lxml

from config import headers


def parse_item_page(page):
    item_title = page.find('h1').text.strip()
    item_description = page.find('div', class_='detail_text').text
    try:
        item_price = page.find('div', class_='prices_block').find('div', class_='price')['data-value']
    except Exception as e:
        pass
    item = {
        'item_title': item_title,
        'item_description': item_description,
        'item_price':item_price,
    }
    return item


def main():
    response = requests.get(url='https://hishnikmarket.ru/catalog/odezhda-i-obuv/odezhda/kostyumy-kurtki/zhilety/', headers=headers)
    # with open(f'index.html', 'w') as file:
    #     file.write(response.text)

    # with open('index.html', 'r', encoding="utf-8") as file:
    #     src = file.read
    #     file.close
    
    soup = BeautifulSoup(response.text, 'lxml')
    type = soup.find('h1').text.strip()
    cards = soup.find_all('div', class_='catalog_item')
    for card in cards:
        card_title = card.find('div', class_='item-title').text.strip()
        try:
            card_price = "".join(card.find('div', class_='js_price_wrapper').find('span', class_='values_wrapper').text.strip().split()[:-1])
        except Exception as e:
            card_price = "".join(card.find('span', class_='price_value').text.strip().split())

        card_link  = card.find('a')['href']
        page =  requests.get(url=f'https://hishnikmarket.ru/{card_link}', headers=headers)
        item = parse_item_page(page=page)
        card_description = ""
        card_image = ""
        print(card_title, "=", card_price, card_link)


if __name__ == '__main__':
    main()
