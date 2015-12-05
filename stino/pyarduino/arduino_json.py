#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import inspect
import json
import os

this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))


def get_plugin_path():
    this_folder_path = os.path.dirname(this_file_path)    
    plugin_path = os.path.dirname(this_folder_path)
    preset_path = os.path.dirname(plugin_path)
    return preset_path


def get_boards_file_path():
    file_path = get_plugin_path() + '\\preset\\boards.json'
    return file_path


# Get the list with all the boards in the json file
# @return a json object

def get_json_boards():
	json_file = get_boards_file_path()
	boards = []
	with open(json_file) as boards_file:
		boards_data = json.load(boards_file)
		for data in boards_data:
			boards += data['boards']
		return boards