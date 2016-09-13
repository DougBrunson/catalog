from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base, Item, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


item_1 = Item(title='Nob Hill Studio', description='Lorem ipsum dolor sit amet, consectetur adipisicing elit. Error eaque eligendi ullam enim dolore, impedit libero sequi sint maxime atque unde vero voluptatum totam rem vitae molestiae. Consectetur molestiae, ipsum!', img_url='https://a1.muscache.com/im/pictures/12122/196848ed_original.jpg?aki_policy=x_medium')
session.add(item_1)
session.commit()

item_2 = Item(title='Dolores Park View (2 rooms)', description='Lorem ipsum dolor sit amet, consectetur adipisicing elit. Error eaque eligendi ullam enim dolore, impedit libero sequi sint maxime atque unde vero voluptatum totam rem vitae molestiae. Consectetur molestiae, ipsum!', img_url='https://a1.muscache.com/im/pictures/4a39d213-2024-4ae6-b931-a8c51ccef1f1.jpg?aki_policy=x_medium')
session.add(item_2)
session.commit()

item_3 = Item(title='Stay in the Famous Painted Ladies!', description='Lorem ipsum dolor sit amet, consectetur adipisicing elit. Error eaque eligendi ullam enim dolore, impedit libero sequi sint maxime atque unde vero voluptatum totam rem vitae molestiae. Consectetur molestiae, ipsum!', img_url='https://a2.muscache.com/im/pictures/6c856728-5b88-42bf-94a0-b6484ae1c6f0.jpg?aki_policy=x_medium')
session.add(item_3)
session.commit()

item_4 = Item(title='Efficiency Studio in Pacific Height', description='Lorem ipsum dolor sit amet, consectetur adipisicing elit. Error eaque eligendi ullam enim dolore, impedit libero sequi sint maxime atque unde vero voluptatum totam rem vitae molestiae. Consectetur molestiae, ipsum!', img_url='https://a0.muscache.com/im/pictures/dc51020f-4d26-48db-8e36-ad14c8fc5250.jpg?aki_policy=x_medium')
session.add(item_4)
session.commit()

item_5 = Item(title='Private Ocean View Retreat w Full Bath', description='Lorem ipsum dolor sit amet, consectetur adipisicing elit. Error eaque eligendi ullam enim dolore, impedit libero sequi sint maxime atque unde vero voluptatum totam rem vitae molestiae. Consectetur molestiae, ipsum!', img_url='https://a1.muscache.com/im/pictures/a607a14a-7938-4ef6-ba6d-1b57bef43d58.jpg?aki_policy=x_medium')
session.add(item_5)
session.commit()

item_6 = Item(title='Mission Bay Apartment', description='Lorem ipsum dolor sit amet, consectetur adipisicing elit. Error eaque eligendi ullam enim dolore, impedit libero sequi sint maxime atque unde vero voluptatum totam rem vitae molestiae. Consectetur molestiae, ipsum!', img_url='https://a2.muscache.com/im/pictures/081ebc12-a6d0-4b42-bef0-29e7c603f84d.jpg?aki_policy=x_medium')
session.add(item_6)
session.commit()

