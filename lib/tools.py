# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="debug mode", action="store_true")
cmdline_args = parser.parse_args()


import unicodedata
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
def normalize(s):
    return strip_accents(s).replace(' ','').replace('-','').lower() if s else s

from datetime import datetime
def format_date(date):
    d = datetime.strptime(date,'%Y-%m-%d')
    return d.strftime('%-d %B %Y').decode('utf8')
