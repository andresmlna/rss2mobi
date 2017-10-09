import os
import glob
import time
import sqlite3
import constants


# Create a folder on determinate path.
# path - string - Path to create folder.
def make_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Get a list of *.json files on determined folder.
# path - string - Path to search  *.json files.
def get_json(path):
    file_list = []
    file_list = file_list + glob.glob(path + '/' + '*.json')
    return file_list


# Replace accented characters.
# word - Characters to replace.
def remove_unsupported_chars(word):
    word = word.replace(' ', '_')
    word = word.replace('.', '_')
    word = word.replace('á', 'a')
    word = word.replace('é', 'e')
    word = word.replace('í', 'i')
    word = word.replace('ó', 'o')
    word = word.replace('ú', 'u')
    return str(word)


# Check if a table exists. True if exists. False if not exists.
# table_name - string - Name of database table for check if exists.
def check_table(table_name):
    conn = None
    table_name = remove_unsupported_chars(table_name).lower()
    table_name = (table_name,)

    try:
        conn = sqlite3.connect(constants.SQLITE_PATH + '/' + constants.SQLITE_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

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
        return None
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
    table_name = remove_unsupported_chars(table_name).lower()

    try:
        conn = sqlite3.connect(constants.SQLITE_PATH + '/' + constants.SQLITE_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        with conn:
            cur = conn.cursor()
            cur.execute('CREATE TABLE {0} (id INTEGER PRIMARY KEY AUTOINCREMENT, section TEXT, title TEXT, url TEXT, timestamp INTEGER);'.format(table_name))
            conn.commit()

            # Print table name created.
            print('\nTable ' + table_name + ' created.\n')

            return True

    except sqlite3.Error as e_sql:
        print(e_sql)
        print('Error on SQLite.')
        return False
    except Exception as e:
        print(e)
        print('General exception.')
        return False
    finally:
        if conn:
            conn.close()


# Insert a new row on determined table.
# table_name - string - Name of the table.
# data - list - Data for row to insert.
def insert_row(table_name, data):
    conn = None
    table_name = remove_unsupported_chars(table_name).lower()
    table_name = (table_name,)

    try:
        conn = sqlite3.connect(constants.SQLITE_PATH + '/' + constants.SQLITE_FILE,  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        with conn:
            cur = conn.cursor()
            cur.execute('''INSERT INTO {0} (section, title, url, timestamp) VALUES (?, ?, ?, (SELECT strftime('%s','now')));'''.format(table_name[0]), (data[0], data[1], data[2]))
            conn.commit()

            # Print date, time and inserted row information.
            print(time.strftime("%H:%M:%S %z ") + ' - '.join(data))

            return True

    except sqlite3.Error as e_sql:
        print(e_sql)
        print('Error on SQLite.')
        return False
    except Exception as e:
        print(e)
        print('General exception.')
        return False
    finally:
        if conn:
            conn.close()


# Get rows for a determinate newspaper section.
# table_name  - string - Name of the table.
# section - string -  Name of the newspaper section.
def rows_by_section(table_name, section):
    conn = None
    table_name = remove_unsupported_chars(table_name).lower()
    section = (section,)

    try:
        conn = sqlite3.connect(constants.SQLITE_PATH + '/' + constants.SQLITE_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        with conn:
            cur = conn.cursor()
            cur.execute('SELECT title, url FROM {0} WHERE section = ?;'.format(table_name), section)

            rows = cur.fetchall()
            return rows

    except sqlite3.Error as e_sql:
        print(e_sql)
        print('Error on SQLite.')
        return None
    except Exception as e:
        print(e)
        print('General exception.')
    finally:
        if conn:
            conn.close()
