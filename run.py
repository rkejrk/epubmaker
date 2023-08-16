"""
実行ファイル
"""
import sys
import mimetypes
import model
from html_util import HTMLUtils
from epub_util import EpubUtils
import const

sys.setrecursionlimit(100000)

def is_list():
    """リストか文字列化を判断する
    """
    return type(const.URL) is model.MenuList

def get_search_links(html_utils : HTMLUtils):
    """URLからリンクリストを生成する"""
    print("HTMLUtils.getSerchLinkandContent 開始")
    html = html_utils.get_connect()

    # ページ一覧を取得
    html_utils.linkable_pages = html_utils.get_links(html)
    print(html_utils.download_links.label)
    print(html_utils.linkable_pages.label)

    return html_utils

def generate_book(html_utils : HTMLUtils):
    """本を生成する"""
    book = EpubUtils(html_utils.generate_filename())
    book = media_download(html_utils.download_links, book)

    #最初の目次ページを追加
    connect = html_utils.get_connect()
    title = html_utils.get_title_tag(connect)
    content = html_utils.get_content(connect)

    # ホームコンテンツ追加
    book.add_page(
        title,
        html_utils.linkable_pages.file_name,
        content
        )
    book = generate_page(html_utils.linkable_pages, book)

    #Epub目次追加
    book.add_menu()
    book.output_epub()
    print("HTMLUtils.getSerchLinkandContent 作成完了")

def generate_page(links, book: EpubUtils) -> EpubUtils:
    """ループ可能なリンクに従いページを追加していく"""
    print('ページ生成開始')
    if type(links) is model.MenuList:
        #Listの場合
        print('対象セクション：'+ links.url)
        print('ページ数：'+ str(len(links.url)))
        for link in links.sub_menu:
            print('これを追加予定：'+ links.url)
            book = generate_page(link, book)

    elif type(links) is model.MenuLink:
        print('対象リンク：'+ links.url)
        #Linkの場合
        # ページ追加処理
        add_http =  HTMLUtils(links.url)
        connect = add_http.get_connect()
        title = add_http.get_title_tag(connect)
        content = add_http.get_content(connect)

        if len(content) > 0:
            print('タイトル：'+ title)
            # ホームコンテンツ追加
            book.add_page(
                title,
                add_http.generate_page_filename(links.url),
                content
                )

    print('ページ生成終了')
    return book

def media_download(links: model.MenuList, book:EpubUtils):
    """ダウンロードタスクを実行する"""
    print("メディアファイルをダウンロード：開始")
    print("データ数："+str(len(links.sub_menu)))
    for r_link in links.sub_menu:
        if isinstance(r_link, model.MenuLink):
            print("ダウンロード："+ r_link.url)
            #Filetypeをチェック
            (mimetype, type) = mimetypes.guess_type(r_link.url)

            book.add_media(r_link.url,
                           r_link.file_name,
                           mimetype)
    print("メディアファイルをダウンロード：終了")
    return book

def __main__():
    """リストの場合、データをもとに実行"""
    http: HTMLUtils = None
    if is_list():
        http = HTMLUtils(const.URL.url)
        http.linkable_pages = const.URL
    else:
        #文字の場合リンクの取得を行う
        http = HTMLUtils(const.URL)
        http = get_search_links(http)
    # リンクをもとに本を作成
    generate_book(http)

__main__()
