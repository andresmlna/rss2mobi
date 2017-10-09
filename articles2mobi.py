import os
import glob
import json
import time
import utils
import sqlite3
import datetime
import constants
from kp3 import Periodical
from newspaper import Article

# news_items - list - List with *.mobi file names.
news_items = []


# Gets the newspapers sections names on SQLite database.
def newspaper_sections(news_name):
    conn = None
    sections = []

    try:
        conn = sqlite3.connect(constants.SQLITE_PATH + '/' + constants.SQLITE_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        with conn:
            cur = conn.cursor()
            cur.execute('SELECT DISTINCT section FROM {0};'.format(news_name))
            rows = cur.fetchall()

            for row in rows:
                sections.append(row[0])
            return sections

    except sqlite3.Error as e_sql:
        print(e_sql)
        print('Error on SQLite.')
        return None
    except Exception as e:
        print(e)
        print('General exception.')
        return None
    finally:
        if conn:
            conn.close()


# Converts datetime to unix timestamp for published date articles.
# date_time - datetime - datetime for published date articles.
def published_date_timestamp(date_time):
    if date_time is None:
        return int(datetime.datetime.utcnow().timestamp())
    else:
        return int(time.mktime(date_time.timetuple()))


# Downloads and parse articles from internet.
# Also Sets content (articles downloaded) for kindle-periodical (kp3) library https://github.com/andresmlna/kindle-periodical
# urls - list - URL list for download articles.
def set_content(urls):
    json_content = []
    for url in urls:
        try:
            article = Article(url, keep_article_html=True, memoize_articles=True, fetch_images=False)
            article.download()
            article.parse()

            if article.article_html != '':
                # Adds QR code at ends article.
                article_html_qr = article.article_html + '\n<br><br><br>[QR CODE]: <a href={1}>{0}</a>'.format(
                    article.title, 'https://api.qrserver.com/v1/create-qr-code/?size=450x450&data=' + url)
                # Sets content for kindle-periodical (kp3) library.
                json_content.append(
                    {
                        "author": ', '.join(article.authors),
                        "published": published_date_timestamp(article.publish_date),
                        "content": json.dumps(article_html_qr),
                        "title": article.title
                    })
                # Print date and URL.
                print(str(time.strftime("%H:%M:%S %z") + ' - ' + article.url))

        except Exception as e:
            print(e)
            print('General exception.')
            continue

    return json_content


# Return a simplified file size.
# file - strung - File path for calculate a simplified file size.
def get_size(file):
    file_bytes = os.path.getsize(file)

    if file_bytes <= 999:
        return str(file_bytes) + ' bytes'

    if file_bytes <= 999999 and file_bytes > 999:
        file_kb = file_bytes / 1024
        file_kb = str(file_kb).split('.')
        file_kb = file_kb[0]
        return str(file_kb) + ' KB'

    if file_bytes > 999999:
        file_mb = round((file_bytes / 1048576), 1)
        return str(file_mb) + ' MB'


# Write text file.
# filename - string - File path.
# content - string - Content for the file to write.
def write_file(filename, content):
    file = open(filename, 'w+', encoding='utf-8')
    file.write(content)


# Delete all *.mobi files in a path.
# path - string - Path for delete files.
def delete_old_mobi(path):
    try:
        file_list = []
        file_list = file_list + glob.glob(path + '/' + '*.mobi')

        for file in file_list:
            os.remove(file)

    except Exception as e:
        print(e)
        print('Error deleting old files')


# Moves all *.mobi files to determined path.
# path - string - Path of files to move.
# target_path - string - Path to store files moved.
def move_mobi(path, target_path):
    file_list = []
    file_list = file_list + glob.glob(path + '/' + '*.mobi')

    for file in file_list:
        mobi_path = file
        mobi_name = mobi_path.split('/')
        mobi_name = mobi_name[-1]

        os.rename(path + '/' + mobi_name, target_path + '/' + mobi_name)


# Write *.mobi file using kindle-periodical (kp3) library.
# news_data - list - List with newspaper data to write.
# contents - list - List with *.html data of articles to write.
def write_mobi(news_data, contents):
    per = Periodical()
    per.BOOK_DIR_TEMP = constants.TEMP_PATH
    per.KINDLEGEN_PATH = constants.KINDLEGEN_PATH
    per.IMAGE_COVER = constants.CURRENT_PATH + '/images_recipes/' + news_data['images']['cover']
    per.IMAGE_MASTHEAD = constants.CURRENT_PATH + '/images_recipes/' + news_data['images']['masthead']
    per.set_metadata(news_data['metadata'])
    per.set_content(contents)

    mobi_full_path = per.make_periodical()

    return mobi_full_path


# Sets contents for *.html file.
# items - list - List items for *.html file.
def make_html(items):
    news_one = []
    news_two = []

    # Divide items in two lists.
    for n in range(0, len(items)):
        if (n % 2) == 0:
            news_one.append(items[n])
        else:
            news_two.append(items[n])

    html_str = open(constants.CURRENT_PATH + '/index.template', 'r').read()
    html_content = html_str.format('\n\t\t\t\t'.join(news_one), '\n\t\t\t\t'.join(news_two))
    write_file(constants.WEB_PATH + '/index.html', html_content)


# Controls the tasks for handling RSS URLs.
def articles2mobi(path):
    # Gets *.json files names.
    for feed in utils.get_json(path):
        sites_content = []
        # Open *.json file.
        try:
            with open(feed, encoding='utf-8') as data_file:
                news_data = json.load(data_file)

        except Exception as e:
            print(e)
            print('Error to open json file.')
            continue

        # Remove unsupported characters for SQLite table names.
        news_name = utils.remove_unsupported_chars(news_data['metadata']['title']).lower()
        # Gets section list by newspaper table name.
        news_sections = newspaper_sections(news_name)

        if news_sections is not None:
            for section in news_sections:
                url_list = []
                # Gets newspaper section URLs
                rows_section = utils.rows_by_section(news_name, section)
                for row in rows_section:
                    # Only URLs
                    url_list.append(row[1])

                # Sets a list with newspaper metadata an list with html downloaded articles.
                sites_content.append({"title": section, "items": set_content(url_list)})

            # Only if exists articles.
            if len(sites_content) > 0:
                # mobi_path - string - Path of *.mobi file
                mobi_path = write_mobi(news_data, sites_content)

                if mobi_path is not None:
                    mobi_name = mobi_path.split('/')
                    mobi_name = mobi_name[-1]

                    # Insert a '<li>' html item with *.mobi name.
                    news_items.append('<li><a href="{1}">{0}</a><br><span class="li-sub_header">{1} {2}</span></li>'.format(
                        news_data["metadata"]["title"],
                        mobi_name,
                        get_size(mobi_path)))
                else:
                    print('\nError generating {0} *.mobi file.'.format(news_name))
        else:
            continue


def main():
    utils.make_folder(constants.WEB_PATH)
    utils.make_folder(constants.TEMP_PATH)

    articles2mobi(constants.JSON_PATH)

    # Optional, for generating *.html with *.mobi file names.
    # make_html(news_items)

    delete_old_mobi(constants.WEB_PATH)
    move_mobi(constants.TEMP_PATH, constants.WEB_PATH)


if __name__ == "__main__":
    main()
