import collections
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists

from countryinfo import CountryInfo

from tabulate import tabulate


class ToDB:
    def __init__(self):
        load_dotenv()
        DB_CONFIG_DICT = {
            'user': os.environ.get('USER'),
            'password': os.environ.get('PASSWORD'),
            'host': os.environ.get('HOST'),
            'port': os.environ.get('PORT'),
        }
        self.database = 'Statistic'
        DB_CONN_FORM = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
        self.DB_CONN = (DB_CONN_FORM.format(database=self.database,
                                            **DB_CONFIG_DICT))

        self.regions = None
        self.region_names = None

        self.data = self.__get_data()
        self.__sort_regions(self.data)

    def __get_data(self):
        engine = create_engine(self.DB_CONN)
        if not database_exists(engine.url):
            raise Exception("Run get_data.py before print_data.py")

        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, rank, dependency_raw, CAST(dependency_percentage AS TEXT) FROM countries"))
            rows = result.fetchall()

        return rows

    def __sort_regions(self, data):
        if not self.regions:
            self.regions = {}

            for row in data:
                try:
                    region = str(CountryInfo(row[1]).region())
                except KeyError:
                    region = 'Other'

                if region not in self.regions:
                    self.regions[region] = [row]
                else:
                    self.regions[region].append(row)
        return self.regions

    def get_region_name(self):
        if not self.region_names:
            self.region_names = list(self.regions.keys())

        try:
            region_name = self.region_names.pop()
            return region_name
        except IndexError:
            return None

    def sorted_data(self):
        used_regions = []

        total_population = {}
        biggest_countries = {}
        smallest_countries = {}
        while True:
            region_name = self.get_region_name()
            if region_name is None or region_name in used_regions:
                break

            population = 0
            biggest_population = 0
            biggest_country = ''
            smallest_population = 0
            smallest_country = ''
            for region in self.regions[region_name]:
                population += int(region[2])

                if biggest_population < region[2]:
                    biggest_population = region[2]
                    biggest_country = region[1]

                if not smallest_population:
                    smallest_population = region[2]
                elif region[2] < smallest_population:
                    smallest_population = region[2]
                    smallest_country = region[1]

            total_population[region_name] = population
            biggest_countries[region_name] = (biggest_country, biggest_population)
            smallest_countries[region_name] = (smallest_country, smallest_population)

            used_regions.append(region_name)

        total_population = collections.OrderedDict(sorted(total_population.items()))
        biggest_countries = collections.OrderedDict(sorted(biggest_countries.items()))
        smallest_countries = collections.OrderedDict(sorted(smallest_countries.items()))

        dicts = (total_population, biggest_countries, smallest_countries)

        merged = {}
        for key in dicts[0].keys():
            merged[key] = tuple(d[key] for d in dicts)

        return merged


class Printer:
    def __init__(self, db_instance):
        self.db = db_instance
        self.regions = []

    def print(self):
        regions = []
        while True:
            region_name = self.db.get_region_name()
            if region_name is None or region_name in regions:
                break
            regions.append(region_name)
        regions.sort()
        merged = self.db.sorted_data()

        response = []
        for region in regions:
            element = merged[region]
            region_name = region
            total_population = element[0]
            biggest_country_population_name = element[1][0]
            biggest_country_territory_population = element[1][1]
            smallest_country_population_name = element[2][0]
            smallest_country_territory_population = element[2][1]
            response.append(
                (region_name, total_population, biggest_country_population_name, biggest_country_territory_population,
                 smallest_country_population_name, smallest_country_territory_population))

        print(tabulate(response, headers=["Region", "Population", "Biggest Country", "Biggest Country Population",
                                          "Smallest Country", "Smallest Country Population"]))


if __name__ == '__main__':
    db = ToDB()
    p = Printer(db)
    p.print()
