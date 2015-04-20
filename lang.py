# -*- coding: utf-8 -*-

import sys
import os
from subprocess import call

lang_path = "res/lang/"
lang_file_name = "en_GB.po"
lang_file_path = os.path.join(lang_path, lang_file_name)
lang_compiled_path = os.path.join(lang_path, lang_file_name.replace(".po", ".mo"))

if len(sys.argv) > 1:
	if sys.argv[1] == 'extract':
		call("find . -regex \".*\\.\\(py\\|glade\\)\" | xargs xgettext -j --from-code=UTF-8 -o{0}".format(lang_file_path), shell=True)
		print("Extracted strings")
	elif sys.argv[1] == 'compile':
		call("msgfmt {0} -o {1}".format(lang_file_path, lang_compiled_path), shell=True)
		print("Compiled strings")
else:
	print("Use command extract to extract strings or compile to compile strings")


#find . -regex ".*\.\(py\|glade\)" | xargs xgettext -j --from-code=UTF-8 -oen_GB.po
#msgfmt res/lang/en_GB.po -o res/lang/en_GB.mo
