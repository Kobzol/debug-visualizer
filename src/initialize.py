import gettext
import locale

def init_localization():
  locale.setlocale(locale.LC_ALL, '') # use user's preferred locale
  loc = locale.getlocale()
  filename = "res/lang/messages_%s.mo" % locale.getlocale()[0][0:2]
 
  try:
    trans = gettext.GNUTranslations(open( filename, "rb" ) )
  except IOError:
    trans = gettext.NullTranslations()
 
  trans.install()
 
if __name__ == '__main__':
  init_localization()
