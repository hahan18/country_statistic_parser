# Country statistic parser

Country statistic parser is an application which parse data from wikipedia page with country population statistic:  https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population 
  and returns human-readable table with region, total population, max/min population countries statistic. 

# About and Technologies

Country statistic parser based on pure Python, using BeautifulSoup and SQLAlchemy.

## Installation

Clone the repository:
```git clone https://github.com/hahan18/country_statistic_parser.git```

Country statistic parser requires [Python 3.10](https://www.python.org/downloads/release/python-3100/) to run.

Navigate into project root:
```cd /your/path/to/project/country_statistic_parser```

Make virtual environment using venv in project root:
```python -m venv venv```

Activate venv:
```venv\Scripts\Activate```

Update the Pip, install the requirements and start the server.
```python -m pip install --upgrade pip```

```python -m pip install -r requirements.txt```

You need to specify .env file with this structure:

```POSTGRES_USER=``` # PostgreSQL user, Default - postgres

```POSTGRES_PASSWORD=``` # Your user's password

```POSTGRES_HOST=``` # Default - localhost

```POSTGRES_PORT=``` # Default - 5432

```POSTGRES_DB=``` # Your DB name, Default - Storage 

!!!Do not create your own DB. Script will create it automatically!!!

Execute ```python get_data.py```

Then ```python print_data.py```

## Docker

To run script using Docker:

Clone the repository:
```git clone https://github.com/hahan18/country_statistic_parser.git```

Navigate into project root:
```cd /your/path/to/project/country_statistic_parser```

To extract data:
```docker-compose up get_data ```

To print the table result: 
```docker-compose up print_data```


   
   
   
