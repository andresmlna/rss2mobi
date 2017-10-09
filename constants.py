import os
from datetime import datetime, timedelta

TODAY = datetime.today().strftime('%Y-%m-%d')
YESTERDAY = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
SQLITE_FILE = 'rss2mobi' + '_' + TODAY + '.db'
SQLITE_PATH = CURRENT_PATH + '/sqlite_dbs'
JSON_PATH = CURRENT_PATH + '/rss_recipes'

# Optional, for generating .html file with all .mobi files generated.
# Example: /var/html/www
WEB_PATH = ''

# Folder with temp files.
# Example: /tmp/rss2mobi
TEMP_PATH = ''

# Folder with kindlegen binary
# /bin
KINDLEGEN_PATH = ''
