import sys
import json
import utils
import datetime
import constants
import feedparser


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
            article_date = datetime.datetime.strptime(article_date_str, '%Y-%m-%d')
            article_date = article_date.strftime('%Y-%m-%d')

            if article_date == constants.TODAY:
                urls_list.append({'title': article['title'], 'url': article['link']})
            elif article_date == constants.YESTERDAY:
                urls_list.append({'title': article['title'], 'url': article['link']})

        except Exception as e:
            print(e)
            print('Error to get article')
            continue

    return urls_list


# Controls the tasks for handling RSS URLs.
def store_rss():
    # Variable for store all URLs from RSS feed.
    urls_feed = []

    # Get a list of *.json files.
    for file_feed in utils.get_json(constants.JSON_PATH):
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
            urls_table = []

            # Check if newspaper table exists on SQLite database.
            if utils.check_table(news_data['metadata']['title']) is False:
                # Create table SQLite database.
                created = utils.create_table(news_data['metadata']['title'])
                if created is False:
                    continue
            else:
                # Gets a list with newspaper section information of SQLite database table.
                newspaper_rows = utils.rows_table(news_data['metadata']['title'])
                for article_db in newspaper_rows:
                    # Only URL of newspaper.
                    urls_table.append(article_db[3])

            if utils.check_table(news_data['metadata']['title']) is True:
                # Gets newspaper articles list for RSS feed.
                article_list = get_urls(feed['url'])

                for article in article_list:
                    urls_feed.append(article['url'])

                # For each article.
                for article in article_list:
                    # Checks if a article URL no exists on list URL of SQLite database newspaper table.
                    if article['url'] not in urls_table or article['url'] not in urls_feed:
                        # Insert article data on SQLite database newspaper table.
                        inserted = utils.insert_row(news_data['metadata']['title'], data=[feed['section'], article['title'], article['url']])
                        if inserted is False:
                            continue

                # Print article information for logs purposes.
                print('{0}, {1} OK\n'.format(news_data['metadata']['title'], feed['section']).upper())


def main():
    utils.make_folder(constants.SQLITE_PATH)
    store_rss()
    print('\nFINISHED')


if __name__ == "__main__":
    main()
