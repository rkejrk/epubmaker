"""電子書籍を作成する"""
import os
from urllib.error import HTTPError
from urllib import request as resouse_d
from ebooklib import epub
import const

class EpubUtils:
    """電子書籍を作成する"""
    book = None

    def __init__(self, book_name:str):
        self.book = epub.EpubBook()
        self.set_meta(book_name)

    def set_meta(self, book_name:str):
        """Meta設定"""
        self.book.set_identifier('sample123456')
        self.book.set_title(book_name)
        self.book.set_language(const.LANG)
        self.book.add_author(const.AUTHOR)
        print(self.book.metadata)

    def add_menu(self):
        """目次生成"""
        page_links = []
        for page_info in self.book.get_items():
            if isinstance(page_info, epub.EpubHtml):
                page_links.append(
                        epub.Link(page_info.file_name, page_info.id, page_info.id)
                    )
        self.book.toc = tuple(page_links)
        # eページの並び順
        self.book.spine = ['nav'] + list(self.book.get_items())
        # ナビファイルの追加
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())


    def add_page(self, title:str, page_url:str, content):
        """Page追加"""
        if len(page_url) == 0 or len(content) == 0:
            return
        if not page_url.endswith(".html"):
            page_url = page_url + '.html'
        page = epub.EpubHtml(title, page_url, const.LANG)
        page.set_content(content)
        self.book.add_item(page)

    def add_style(
            self,
            uid:str,
            style = 'body { font-size: 10px; font-family: Roboto, Arial, sans-serif;}'):
        """cssを追加"""
        self.book.add_item(epub.EpubItem(uid,
                                file_name="style/nav.css",
                                media_type="text/css",
                                content=style))

    def add_media(self,image_path:str, file_name:str, media_type:str) -> bool:
        """メディアファイル追加"""
        resorce = None
        if (media_type.startswith('image') or
            media_type.startswith('audio') or
            media_type.startswith('video')):
            
            file_path = f'./{media_type}/{file_name}'
            print("file_path: " + file_path)
            if not os.path.isdir(media_type):
                os.makedirs(media_type)
            try:
                resouse_d.urlretrieve(image_path, file_path)
                resorce = epub.EpubItem(uid=f'{media_type}_{file_name}',
                                    file_name= file_path,
                                    media_type = media_type,
                                    content= './' + file_path)
            except HTTPError:
                print('HTTPError：　image_path')

        if not resorce is None:
            self.book.add_item(resorce)
            return True
        else:
            return False

    def output_epub(self):
        """Epub出力"""
        epub.write_epub(
            self.book.title + '.epub', self.book)
