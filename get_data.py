import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from sqlalchemy import Column, String, DECIMAL, Integer, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database


class Extractor:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1'
    }
    URL = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'

    def __init__(self):
        self.table = None

    def get_rows(self):
        if not self.table:
            self._get_table()

        rows = []
        t_rows = self.table.find_all('tr')

        for row in t_rows:
            value = row.find_all('td')
            beautified_value = [dp.text.strip() for dp in value]

            if len(beautified_value) == 0 or beautified_value[1] == 'World':
                continue

            beautified_value[1] = beautified_value[1].replace(',', '')
            beautified_value[2] = beautified_value[2].replace('%', '')

            rows.append(beautified_value[0:3])

        return rows

    def get_headers(self):
        if not self.table:
            self._get_table()

        titles = self.table.find('tr', attrs={'class': 'is-sticky'})

        headers = []
        for title in titles:
            table_string = title.text.strip()
            result = " ".join(re.findall("[a-zA-Z0-9]+", table_string))
            headers.append(result)

        headers = list(filter(None, headers))[0:3]
        return headers

    def _get_table(self):
        if not self.table:
            with requests.Session() as session:
                response = session.get(url=Extractor.URL, headers=Extractor.HEADERS)
                soup = BeautifulSoup(response.text, 'html.parser')
                self.table = soup.find('table', attrs={'class': 'wikitable'})
        return self.table


class DB:
    def __init__(self, parsed_data):
        load_dotenv()
        DB_CONFIG_DICT = {
            'user': os.environ.get('POSTGRES_USER'),
            'password': os.environ.get('POSTGRES_PASSWORD'),
            'host': os.environ.get('POSTGRES_HOST'),
            'port': os.environ.get('POSTGRES_PORT'),
        }
        self.database = os.environ.get('POSTGRES_DB')
        DB_CONN_FORM = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
        self.DB_CONN = (DB_CONN_FORM.format(database=self.database,
                                            **DB_CONFIG_DICT))

        self.engine = None
        self.table = None
        self.parsed_data = parsed_data

    def master(self):
        self._create_db()
        self._create_table()
        self._insert_data()

    def _create_db(self):
        self.engine = create_engine(self.DB_CONN)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

    def _create_table(self):
        Base = declarative_base()

        class Countries(Base):
            __tablename__ = 'countries'
            id = Column(Integer, primary_key=True)
            rank = Column(String(250))
            dependency_raw = Column(Integer)
            dependency_percentage = Column(DECIMAL)

        Base.metadata.drop_all(self.engine, checkfirst=True)

        self.table = Countries
        Base.metadata.create_all(self.engine)

    def _insert_data(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        for row in self.parsed_data:
            country = self.table(rank=row[0], dependency_raw=row[1], dependency_percentage=row[2])
            session.add(country)

        session.commit()


if __name__ == '__main__':
    extractor = Extractor()

    parsed = extractor.get_rows()
    DB = DB(parsed)
    DB.master()
