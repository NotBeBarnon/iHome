

import os
# 基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# static 路径
STATIC_PATH = os.path.join(BASE_DIR, 'static')
# templates
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')
# media
MEDIA_PATH = os.path.join(STATIC_PATH, 'media')


DATABASE = {
    'NAME': 'ihome',
    'USER': 'root',
    'PASSWORD': '123456',
    'HOST': '127.0.0.1',
    'PORT': '3306',
    'ENGINE': 'mysql',
    'DRIVER': 'pymysql'

}