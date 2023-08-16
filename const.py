"""設定ファイル"""
from model import MenuLink
from model import MenuList

# 本の情報
LANG = "ja"
AUTHOR = "admin"

# スクレイピングi に必要な情報
URL: str or MenuList = "http://localhost:8000"
# URL: str or MenuList = MenuList([
#         MenuLink("サイトの名前", "http://", "ページファイル名（半角英数字）")
#     ],
#     "サイトの名前",
#     "http://",
#     "出力ファイル.epub"
# )
# コンテンツのセレクタ 例：#CONTENT_ID.CONTENT_CLASS
CONTENT_TAG = "main"
CONTENT_ID = ""
CONTENT_CLASS = ""
#  目次のセレクタ
NAV_TAG = "nav"
NAV_ID = ""
NAV_CLASS = ""

TAG_FLG = True
