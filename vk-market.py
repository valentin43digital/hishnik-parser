from email.mime import image
from math import prod
import string
import time
from unicodedata import category
from dotenv import load_dotenv
load_dotenv()
import os
from PIL import Image
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker


from models import Product, Category
from categories import categories
from config import headers

group_id = os.environ['VK_GROUP_ID']
token = os.environ['VK_TOKEN']


def add_product(session, product: Product):
    photo_id = upload_market_photo(product)
    params = {
        'owner_id':"-"+group_id,
        'name': product.name,
        'description': product.description,
        'category_id': 802,
        'price': product.price,
        'main_photo_id': photo_id,
        'url': product.link,
        'access_token': token,
        'v': 5.131
    }
    req = requests.get(f"https://api.vk.com/method/market.add", params=params).json()
    print("RESPONSE=",  req)
    product.vk_id = req['response']['market_item_id']
    product.vk_photo_id = photo_id
    session.commit()
    return product.vk_id


# Gets link of photo upload server
def get_market_upload_server():
    params = {
        'access_token': token,
        'group_id': group_id,
        'main_photo': 1,
        'v': 5.131,
    }
    r = requests.get("https://api.vk.com/method/photos.getMarketUploadServer", params=params).json()
    return r['response']['upload_url']


# Uploads market photo to VK server, returns photo id
def upload_market_photo(product: Product):
    image_name = download_image(product.photo)
    im = Image.open(f"images/{image_name}")
    if im.width <400 or im.height <400:
        resize_image(image=im, image_name=image_name)
    im.close()
    upload_url = get_market_upload_server()
    file = {'file1': open(f'images/{image_name}', 'rb')}
    upload_response = requests.post(url=upload_url, files=file).json()
    # print("response=", upload_response)
    params = {
        'access_token': token,
        'group_id': group_id,
        'server': upload_response['server'],
        'photo': upload_response['photo'],
        'hash': upload_response['hash'],
        'crop_data': upload_response['crop_data'],
        'crop_hash': upload_response['crop_hash'],
        'v': 5.131,
        }
    r = requests.get("https://api.vk.com/method/photos.saveMarketPhoto", params=params).json()
    return r['response'][0]['id']


def resize_image(image: Image, image_name):
    width = int(image.width)
    height = int(image.height)
    if width < height:
        new_width = 400
        new_height = height*new_width//width
    else:
        new_height = 400
        new_width = width*new_height//height
    new_size = (new_width, new_height)
    res = image.resize(new_size)
    res.save(f"images/{image_name}")


def download_image(link: string):
    image_name = link.split("/")[-1]
    res = requests.get(link)
    if not os.path.exists(f"images/{image_name}"):
        with open(f'images/{link.split("/")[-1]}', 'wb') as img_file:
            img_file.write(res.content) 
    return image_name


def add_categories(session):
    categories = session.query(Category)
    for category in categories:
        add_category(category)


def add_category(category: Category):
    pass


def add_to_category(product: Product, category: Category):
    params = {
    'access_token': token,
    'owner_id': "-"+group_id,
    'item_id': product.vk_id,
    'album_ids': category.vk_id,
    'v': 5.131,
    }
    r = requests.get("https://api.vk.com/method/market.addToAlbum", params=params).json()


def get_categories():
    params = {
        'access_token': token,
        'owner_id': "-"+group_id,
        'v': 5.131,
    }
    r = requests.get("https://api.vk.com/method/market.getAlbums", params=params).json()
    return r['response']['items']


def add_products(session):
    categories = session.query(Category)
    for category in categories:
        products = session.query(Product).filter_by(category=category.name)
        for product in products:
            if product.vk_id:
                print(product.name, "уже загружен")
            else:
                print("Добавляю", product.name)
                try:
                    add_product(session=session, product=product)
                    add_to_category(product=product, category=category)
                    print("Добавлен", product.name)
                except Exception as e:
                    print("Не добавлен", product.name, "по причине", e)
                    # break
                time.sleep(0.8)


def get_products(session):
    params = {
    'access_token': token,
    'owner_id': "-"+group_id,
    'v': 5.131,
    }
    r = requests.get("https://api.vk.com/method/market.get", params=params).json()
    return r['response']['items']


def clean_product_vk_id(session, link):
    product = session.query(Product).filter_by(link=link).first()
    product.vk_id = None
    session.commit()


def update_product(session, product: Product):
    product.description = "Чучело предназначено для приманивания летящих и сидящих уток. В большом количестве в тандеме с самкой оживит любую партию. Легкое и компактное чучело. РЕАЛИСТИЧНАЯ РАСКРАСКА! Голова съемная, крепится к туловищу (вкручивается). В нижней части туловища чучела предусмотрена специальная ниша для укладки съемной головы при транспортировке, что делает данные чучела более компактными. Выбирая это чучело, вы гарантируете себе успешный сезон охоты. Чучела такого качества - мечта, как новичка, так и опытного охотника. Материал - полистирол. Вес - 180 грамм. Длина - 310 мм. Ширина - 170 мм. Высота: без головы - 90 мм, с головой - 160 мм. У селезня в брачном наряде голова и зоб каштаново-красные либо рыжие, грудь и область вокруг хвоста чёрные (грудь с заметным блеском), спина и бока светло-серые с мелкими поперечными пестринами (при ярком дневном свете эти области выглядят беловатыми), радужина красная. «Зеркальце» на крыле отсутствует."
    session.commit()


def main():
    # photo_id = upload_photo()
    engine = create_engine('sqlite:///hishnik.db', echo=False)
    session = sessionmaker(bind=engine)()
    # add_products(session=session)


    category_name="Аксессуары для рыбалки"
    # products = session.query(Product).filter_by(category=category_name)
    products = session.query(Product)
    category = session.query(Category).filter_by(name=category_name).first()
    for product in products:
        if not product.vk_id:
            print(product.name)
            # try:
            #     add_to_category(product=product, category=category)
            #     print(product.name, "добавлен в категорию")
            # except Exception as e:
            #     print("Уже добавлен в категорию")


    # name="Костюм Remington TRAIL CAMO Eurowinter Green forest, р."
    # product = session.query(Product).filter_by(name=name).first()
    # print(product.vk_id)
    # add_product(session=session, product=product)
    # add_to_category(product=product, category=product.category)
    # while True:
    #     try:
    #         add_products(session=session)
    #     except Exception as e:
    #         print("Exception = ", e)
    # product = session.query(Product).filter_by(name='Тетерка').first()
    # update_product(session=session, product=product)
    # add_product(session, product)
    # category = session.query(Category).filter_by(name='Ботинки').first()
    # add_to_category(product, category)
    # req =  requests.get(url).text
    # print(req)
    # image_name = "9729fd0c5136920d0d155602a426f6ac.jpg"
    # im = Image.open(f"images/{image_name}")
    # resize_image(image=im, image_name=image_name)
    # q = session.query(Product).filter_by(category='Головные уборы')
    # i = 1
    # for item in q:
    #     print(i,"=", item)
    #     i+=1
    # for product in get_products(session=session):

    # list = [
    # ]
    # for item in list:
    #     clean_product_vk_id(session=session, link=item)


    # add_product(session=session, product=product)
    # add_to_category(product=product, category=category)
    # print("Добавлен", product.name)
    # download_image(jpeg)
    # vk_session = vk_api.VkApi(token=VK_TOKEN)
    # vk_session.auth()
    # vk = vk_session.get_api()
    # # print(vk.wall.post(message='Hello world!'))
    # vk.market.add(
    #     owner_id="-77604264",
    #     name="Test",
    #     description="Test123",
    #     price="123"
    #     )

if __name__ == '__main__':
    main()
