# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 02:06:49 2024

@author: Kelvin
"""

import requests
import json
import os

def get_posts(language, metadata):
    url = 'https://open.api.nexon.com/static/tfd/meta/'+ language +'/' + metadata +'.json'
    try:
        response = requests.get(url)

        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

data_names = ['descendant','weapon','module','reactor','external-component', 'reward', 'stat','void-battle','title']
for item in data_names:
    print('getting: ' + item)
    meta_name = item + '.json'
    posts = get_posts('en', item)
    file_path = os.path.join('Data', meta_name)
    with open(file_path, 'w') as json_file:
        json.dump(posts, json_file, indent=4)





