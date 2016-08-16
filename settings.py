#!/usr/bin/env python
'''Just parse settins.json as a dict for futher use.'''

from json import loads as jloads

def get_settings():
    settings_file = open('settings.json', 'r')
    settings = jloads(settings_file.read())['settings']
    return settings