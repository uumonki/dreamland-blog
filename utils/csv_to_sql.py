from sqlalchemy import create_engine, Column, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
import sys
import pandas as pd
from datetime import datetime

Base = declarative_base()

class BlogPost(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    author = Column(Boolean, nullable=False)
    date = Column(Text, nullable=False)  
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)

engine = create_engine('sqlite:///instance/example.db')  # Path to your .db file
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


def preprocess_date(date_str):
    # Dictionary to map your custom month abbreviations to standard ones
    month_map = {
        'jan': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'apr': 'Apr',
        'may': 'May', 'june': 'Jun', 'july': 'Jul', 'aug': 'Aug',
        'sept': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dec': 'Dec'
    }
    # Split the date string
    month, day, year = date_str.split()
    # Normalize the month and format the date string
    normalized_date = f"{month_map[month.lower()]} {int(day)} {year}"
    return datetime.strptime(normalized_date, '%b %d %Y').strftime('%Y-%m-%d')


csv_file = os.path.join(os.path.dirname(sys.argv[0]), 'data.csv')
df = pd.read_csv(csv_file)

# preprocess dataframe
df['date'] = df['date'].apply(preprocess_date)
df.rename(columns={'side': 'author'}, inplace=True)
df['author'] = df['author'].apply(lambda x: False if x == 'left' else True)

for index, row in df.iterrows():
    new_post = BlogPost(
        author=row['author'],
        date=row['date'],
        content=row['content'],
        rating=row['rating']
    )
    session.add(new_post)

session.commit()