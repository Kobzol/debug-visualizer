# -*- coding: utf-8 -*-

import os
import sys
import gettext
import locale

import paths
sys.path.append(paths.DIR_GUI)

from config import Config
from app import VisualiserApp

lang_path = "res/lang"
language_file = os.path.join(lang_path, "en_GB.mo")

def init_localization():
  #locale.setlocale(locale.LC_ALL, '') # use user's preferred locale
  #loc = locale.getlocale()
  filename = language_file
 
  try:
    trans = gettext.GNUTranslations(open( filename, "rb" ) )
  except IOError:
    trans = gettext.NullTranslations()
 
  trans.install()
 
if __name__ == '__main__':
  init_localization()
  config = Config()
  app = VisualiserApp(config)
  app.start()
