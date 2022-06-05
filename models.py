from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///hishnik.db', echo=True)
base = declarative_base()


class Product(base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    description = Column(String)
    price = Column(Integer)
    link = Column(String)
    photo = Column(String)
    vk_id = Column(Integer)
    vk_photo_id = Column(Integer)
    def __repr__(self) -> str:
        return '<Product(name="{}", category="{}")>'.format(self.name, self.category)

class Category(base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    link = Column(String)
    vk_id = Column(Integer)


base.metadata.create_all(engine)
