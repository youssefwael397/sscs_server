import pymysql
import os

# local mysql config vars
host = 'localhost'
user = 'root'
password = ''
db = 'sscs'  # sscs or shebak
port = 3306

# heroku shebak-db => clear db mysql_uri
# 'mysql://b6882d20dfbdb0:553e7660@us-cdbr-east-06.cleardb.net/heroku_8f810f4920e9790?reconnect=true'

# host = 'us-cdbr-east-06.cleardb.net'
# user = 'b6882d20dfbdb0'
# password = '553e7660'
# db = 'heroku_8f810f4920e9790'


mysql_uri = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
