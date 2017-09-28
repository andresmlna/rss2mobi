import feedparser
import sqlite3
import time
import glob
import json
import sys
import os
from datetime import datetime, timedelta

TODAY = datetime.today().strftime('%Y-%m-%d')
YESTERDAY = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
SQLITE_FILE = 'rss2mobi' + '_' + TODAY + '.db'
SQLITE_PATH = CURRENT_PATH + '/sqlite_dbs/'
JSON_PATH = CURRENT_PATH + '/rss_recipes/'


# Create a folder on determinate path.
# path - string - Path to create folder.
def make_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Replace accented characters.
# word - Characters to replace.
def remove_accents(word):
    word = word.replace('á', 'a')
    word = word.replace('é', 'e')
    word = word.replace('í', 'i')
    word = word.replace('ó', 'o')
    word = word.replace('ú', 'u')
    return word


# Check if a table exists. True if exists. False if not exists.
# table_name - string - Name of database table for check if exists.
def check_table(table_name):
    conn = None
    table_name = remove_accents(table_name)
    table_name = str(table_name).replace(' ', '_').lower()
    table_name = str(table_name).replace('.', '_').lower()
    table_name = (table_name,)

    try:
        conn = sqlite3.connect(SQLITE_PATH + SQLITE_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?;''', table_name)

            rows = cur.fetchone()
            if rows is None:
                return False
            else:
                return True
    except sqlite3.Error as e_sql:
        print(e_sql)
        print('Error on SQLite.')
        sys.exit()
    except Exception as e:
        print(e)
        print('General exception.')
    finally:
        if conn:
            conn.close()


# Create table
# table_name - string - Name for the new table.
def create_table(table_name):
    conn = None
    table_name = remove_accents(table_name)
    table_name = str(table_name).replace(' ', '_').lower()
    table_name = str(table_name).replace('.', '_').lower()

    try:
        conn = sqlite3.connect(SQLITE_PATH + SQLITE_FILE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

        with conn:
            cur = conn.cursor()
            cur.execute('CREATE TABLE {0} (id INTEGER PRIMARY KEY AUTOINCREMENT, section TEXT, title TEXT, url TEXT, timestamp INTEGER);'.format(table_name))
            print('\nTable ' + table_name + ' created.\n')
    except sqlite3.Error as e_sql:
        print(e_sql)
        print('Error on SQLite.')
        sys.exit()
    except Exception as e:
        print(e)
        print('General exception.')
    finally:
        if conn:
            conn.close()


# Get rows for a determinate newspaper section.
# table_name  - string - Name of the table.
# section - string -  Name of the newspaper section.
def rows_by_section(table_name, section):
    conn = None
    table_name = remove_accents(table_name)
    table_name = str(table_name).replace(' ', '_').lower()
    table_name = str(table_name).replace('.', '_').lower()
    section = (section,)

    try:
        conn = sqlite3.connect(SQLITE_PATH + SQLITE_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        with conn:
            cur = conn.cursor()
            cur.execute('SELECT title, url FROM {0} WHERE section = ?;'.format(table_name), section)

            rows = cur.fetchall()
            return rows
    except sqlite3.Error as e_sql:
        print(e_sql)
        print('Error on SQLite.')
        sys.exit()
    except Exception as e:
        print(e)
        print('General exception.')
    finally:
        if conn:
            conn.close()


# Insert a new row on determined table.
# table_name - string - Name of the table.
# data - list - Data for row to insert.
def insert_row(table_name, data):
    conn = None
    table_name = remove_accents(table_name)
    table_name = str(table_name).replace(' ', '_').lower()
    table_name = str(table_name).replace('.', '_').lower()
    table_name = (table_name,)

    try:
        conn = sqlite3.connect(SQLITE_PATH + SQLITE_FILE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

        with conn:
            cur = conn.cursor()
            cur.execute('''INSERT INTO {0} (section, title, url, timestamp) VALUES (?, ?, ?, (SELECT strftime('%s','now')));'''.format(table_name[0]), (data[0], data[1], data[2]))
            conn.commit()
            # Print date, time and inserted row information.
            print(time.strftime("%H:%M:%S %z\t") + ' - '.join(data))
    except sqlite3.Error as e_sql:
        print(e_sql)
        print('Error on SQLite.')
        sys.exit()
    except Exception as e:
        print(e)
        print('General exception.')
    finally:
        if conn:
            conn.close()


# Get a list of *.json files on determined folder.
# path - string - Path to search  *.json files.
def get_json(path):
    file_list = []
    file_list = file_list + glob.glob(path + '*.json')
    return file_list


# Return a list for all article published now and yesterday for a RSS feed.
# url - string - URL of RSS feed.
def get_urls(url):
    urls_list = []
    feeds = feedparser.parse(url)

    for article in feeds['entries']:
        # In case something goes wrong with the extraction of the publication dates.
        try:
            article_date_str = '{0}-{1}-{2}'.format(
                article['published_parsed'][0],
                article['published_parsed'][1],
                article['published_parsed'][2])
            article_date = datetime.strptime(article_date_str, '%Y-%m-%d')
            article_date = article_date.strftime('%Y-%m-%d')

            if article_date == TODAY:
                urls_list.append({'title': article['title'], 'url': article['link']})
            elif article_date == YESTERDAY:
                urls_list.append({'title': article['title'], 'url': article['link']})
        except Exception as e:
            print(e)
            print('Error to get article date')

    return urls_list


# Controls the tasks for handling RSS URLs
def make_rss():
    # Get a list of *.json files.
    for file_feed in get_json(JSON_PATH):
        # Open *.json file.
        try:
            with open(file_feed, encoding='utf-8') as data_file:
                news_data = json.load(data_file)
        except Exception as e:
            print(e)
            print('Error to open json file.')
            sys.exit()

        # Loop for each RSS feed on *.json file.
        for feed in news_data['feeds']:
            # Variable for store all URL of newspaper section on SQLite database.
            urls_feed = []
            # Check if newspaper table exists on SQLite database.
            if check_table(news_data['metadata']['title']) is False:
                # Create table SQLite database.
                create_table(news_data['metadata']['title'])
            else:
                # Gets a list with newspaper section information of SQLite database table.
                rows_section = rows_by_section(news_data['metadata']['title'], feed['section'])
                for article_db in rows_section:
                    # Only URL of newspaper section.
                    urls_feed.append(article_db[1])

            # Gets newspaper articles list for RSS feed.
            article_list = get_urls(feed['url'])
            # For each article.
            for article in article_list:
                # Checks if a article URL no exists on list URL of SQLite database newspaper table.
                if article['url'] not in urls_feed:
                    # Insert article data on SQLite database newspaper table.
                    insert_row(news_data['metadata']['title'], data=[feed['section'], article['title'], article['url']])

            # Print article information for logs purposes.
            print('{0}, {1} OK\n'.format(news_data['metadata']['title'], feed['section']).upper())


def main():
    make_folder(SQLITE_PATH)

    make_rss()
    print('\nFINISHED')


if __name__ == "__main__":
    main()