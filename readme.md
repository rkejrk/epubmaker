
##  設定項目
#　url
- メニューの一覧を持っている場合、または、特定のサイトをEpubにまとめたい場合
    ```python
    url = model.MenuList("タイトル", [
        model.MenuLink("コンテンツ１", "http:/")
    ])
    ```
- URLに紐づく同一サイトのURLをEpubにまとめたい場合
    ```python
    url = "https://~"
    ```

# セレクタ
- content_id: Epubにしたいコンテンツがすべて含まれているHTMLタグのID
- content_class: Epubにしたいコンテンツがすべて含まれているHTMLタグのClass

TODO要素:
- title_selecter:  もくじに必要なタイトルのCSSセレクタ
- subtitle_selecter:  もくじに必要なサブタイトルのCSSセレクタ
- tag_flg: HTMLタグ付きで生成uするか確認