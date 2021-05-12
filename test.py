from bs4.element import Comment
from ksalib.Auth import Auth
from ksalib.gaonnuri import *

sangwoo = Auth()
sangwoo.gaonnuri_auth("ksa17003","17-003")

a = Post(sangwoo,"http://gaonnuri.ksain.net/xe/board_select/703441")

comments = a.comment()

print(comments)

# a.delete_comment("705998")
# a.write_comment("asdas")