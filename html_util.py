"""HTML分析ファイル"""
import re
import random
import string
import mimetypes
import requests
from bs4 import BeautifulSoup
from bs4 import element
import model
import const

class HTMLUtils:
    """HTML分析クラス"""
    url:str

    DOMAIN_PTN = re.compile('^(http|https)+(://).+/?$')
    ANCHOR_PTN = re.compile('#.+$')

    # グループタグ（子要素を分析する）
    SECTION_TAG = ["body", "section", "nav", "article", "aside", "header",
                   "footer", "address", "div", "main", "details", "table", "tbody", "tr", "td"]
    # アイテムタグ（ 文言を取得しEPUBに反映する）
    CONTENT_TAG = [ "pre", "blockquote", "li", "dt", "dd", "figcaption",
                   "em", "strong", "small", "s", "cite", "title", "q", "dfn", "abbr", "time",
                   "code","var", "samp","kbd","sub","sup", "i", "b", "mark", "ruby","bdo",
                   "span", "ins", "del", "br", "wbr", "summary"]
    # リンクタグ （同一サイト内の記事はEpub内リンクを適用する）
    LINK_TAG = ["a"]
    # リソースタグ（ダウンロードしてリンク可能にする）
    OUTER_RESOURCE_TAG = ["img", "area", "map", "source", "audio", "video",
                        "iframe", "embed", "object","canvas","param"]
    # アイテムタグ（可読性向上のため設定に関わらずタグを反映する）
    ENABLED_TAG = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "ol", "ul", "dl"] #table

    #リンク情報（ページ追加タスク・置換タスク・目次）
    linkable_pages:model.MenuList
    # ファイルのリンク
    download_links:model.MenuList

    def __init__(self,
                 url:str):
        self.url = url
        self.linkable_pages = model.MenuList(
            [],
            self.generate_page_filename(self.url),
            self.url,
            self.generate_page_filename(self.url)
        )
        self.download_links = model.MenuList(
            [],
            self.generate_page_filename(self.url),
            self.url,
            self.generate_page_filename(self.url)
        )

    def get_connect(self):
        """httpリクエスト準備"""
        response = requests.get(self.url, timeout=5)
        response.encoding = response.apparent_encoding
        return response.text

    def get_links(self, content:str) -> list:
        """ループ可能な（重ため）リンク作成メソッド
        更新プロパティ
        ・download_links
        """
        content_bs = BeautifulSoup(content, 'html.parser')
        content_bs = content_bs.select_one(self.generate_menu_selecter())
        # リソース取得
        self.set_resources(content_bs, "src", self.url)
        self.set_resources(content_bs, "data", self.url)

        # リンク処理
        links = content_bs.select("[href]")
        response_urls = model.MenuList(
            [],
            self.generate_page_filename(self.url),
            self.url,
            self.generate_page_filename(self.url)
        )
        print("link取得開始: " + str(len(links)))
        for link in links:
            if isinstance(link, element.Tag):
                link_url = link.attrs.get("href")
                print("対象リンク: "+ link_url)
                #ファイル形式チェック
                (mimetype, mime) = mimetypes.guess_type(link_url)
                if (not self.download_links.check_url(link_url) and
                    not mimetype is None and(
                     mimetype.startswith('image') or
                     mimetype.startswith('video') or
                     mimetype.startswith('audio'))):
                    #メディアファイルの場合メディアに追加
                    resource_file_name = self.generate_page_filename(link_url)
                    if link_url.startswith('/'):
                        domain = self.DOMAIN_PTN.match(self.url).group()
                        link_url = domain + link_url.lstrip('/')
                    self.download_links.sub_menu.append(model.MenuLink(
                            resource_file_name,
                            link_url,
                            resource_file_name
                        ))
                    print("メディアファイルでした")

                elif self.generate_page_filename(link_url).count('.php') == 0:
                    #リンク内にhtml以外のファイル名が含まれないかチェック
                    link_url = self.clear_anchor(link_url)
                    file_name = self.generate_page_filename(link_url)
                    print("リンク済みかチェック")
                    if (self.check_domain(link_url) and
                        self.get_generated_link(self.linkable_pages, link_url)  is None and
                        self.get_generated_link(response_urls, link_url) is None):
                        print("結果： False（リンク対象）")

                        #同一ドメインの場合 かつ Listに存在しないリンクの場合
                        # さらにリンクがないかチェック
                        subhtml:HTMLUtils
                        if link_url.startswith('/'):
                            domain = self.DOMAIN_PTN.match(self.url).group()
                            link_url = domain + link_url.lstrip('/')
                        subhtml = HTMLUtils(link_url)
                        
                        # サブリンク追加(※サイトの規模によってはエラーになる)
                        # subitems = subhtml.get_links(subhtml.get_content(subhtml.get_connect()))

                        # if len(subitems) > 0:
                        #     #リンクが存在する場合
                        #     response_urls.sub_menu.append(model.MenuList(
                        #         subitems,
                        #         content_bs.select_one("title"),
                        #         link_url,
                        #         self.generate_page_filename(link_url) + ".html"
                        #     ))
                        # リソース取得
                        html = subhtml.get_connect()
                        subtar = subhtml.get_content(html)
                        sub_content = BeautifulSoup(subtar, 'html.parser')
                        if not sub_content is None:
                            self.set_resources(sub_content, "src", link_url)
                            self.set_resources(sub_content, "data", link_url)
                            page_id = content_bs.select_one("title")
                            if page_id is None:
                                page_id = file_name
                            # else:
                            # リンクがない場合
                            response_urls.sub_menu.append(model.MenuLink(
                                page_id,
                                link_url,
                                file_name + ".html"
                            ))

        return response_urls

    def set_resources(self, content_bs:BeautifulSoup, attr: str, url: str):
        """属性値からリソースのリンクを取得する
        更新プロパティ
        ・download_links
        """
        res = content_bs.select(f"[{attr}]")
        if res is None:
            return
        for item in res:
            if isinstance(item, element.Tag):
                resource_url = item.attrs.get(attr)
                resource_file_name = self.generate_page_filename(resource_url)
                (mimetype, type) = mimetypes.guess_type(resource_url)
                if (not self.download_links.check_url(resource_url) and
                    not mimetype is None and
                    (
                        mimetype.startswith('audio') or
                        mimetype.startswith('video') or
                        mimetype.startswith('image')
                    )):

                    insert_url = resource_url
                        # ディレクトリの場合
                    if resource_url.startswith('../') or resource_url.startswith('.s/'):
                        urls = url.split('/')
                        if urls[len(urls)-1].count('.') > 0:
                            # ファイル名を削除
                            urls.pop()
                        resource_urls = resource_url.split('/')
                        for dir_name in resource_urls:
                            if dir_name == "..":
                                resource_urls.pop(0)
                                urls.pop()
                        insert_url = '/'.join(urls) + '/' + '/'.join(resource_urls)

                    elif resource_url.startswith('/'):
                        domain = self.DOMAIN_PTN.match(self.url).group()
                        insert_url =  domain + resource_url.lstrip('/')

                    self.download_links.sub_menu.append(model.MenuLink(
                            resource_file_name,
                            insert_url,
                            resource_file_name
                        ))

    def get_generated_link(
            self, search_list: model.MenuList,
            check_url:str
        ) -> model.MenuLink or None:
        """ループ可能なリスト済みチェックメソッド
        メニュー作成済みの場合MenuListを返す
        """
        is_created = None
        for target in search_list.sub_menu:
            if type(target) is model.MenuList:
                is_created = self.get_generated_link( target.sub_menu, check_url)
            if type(target) is model.MenuLink and (target.url == check_url):
                is_created = target
            if not is_created is None:
                print("リンクが存在するかチェック")
                print(f"{target.url} == {check_url}")
                print("結果:True")
                return target
        return is_created

    def get_content(self, html: str):
        """ 記事本文を取得"""
        print("HTMLUtils.getContent コンテンツ分析 開始")
        soup = BeautifulSoup( html, 'html.parser')
        content = soup.select_one(self.generate_selecter())
        return self.generate_content(content, "")

    def generate_content(self, html_item: element.Tag, generated: str):
        """ループ可能なコンテンツ最適化メソッド"""
        res_str = generated
        if html_item is None:
            return ""
        for childe in html_item.childGenerator():
            if isinstance(childe, element.Tag):
                if self.SECTION_TAG.count(childe.name) > 0:
                    if len(childe.contents) == 1:
                        res_str += childe.text
                    else:
                        res_str = self.generate_content(childe, res_str)

                elif self.CONTENT_TAG.count(childe.name) > 0:
                    res_str += "<p>"
                    if const.TAG_FLG:
                        res_str += childe.text
                    else:
                        res_str += childe.getText()
                    res_str += "</p>"

                elif self.LINK_TAG.count(childe.name) > 0:
                    link = self.get_generated_link(self.linkable_pages, self.url)
                    if isinstance(link, model.MenuLink):
                        old_link = self.clear_anchor(childe.attrs.get('href'))
                        res_str += "<div>"
                        res_str += childe.text.replace(old_link, link.file_name)
                        res_str += "</div>"

                elif self.ENABLED_TAG.count(childe.name) > 0:
                    res_str += "<div>"
                    res_str += str(childe)
                    res_str += "</div>"

        return res_str

    def get_title_tag(self, html:str) ->str:
        """タイトル返却"""
        title_tag:element.Tag = BeautifulSoup(html, 'html.parser').select_one("title")
        return title_tag.getText()

    def generate_selecter(self) -> str:
        """コンテンツのCSSセレクタを決定"""
        select_str = ""
        if len(const.CONTENT_TAG) > 0:
            select_str += const.CONTENT_TAG
        if len(const.CONTENT_ID) > 0:
            select_str += '#' + const.CONTENT_ID
        if len(const.CONTENT_CLASS) > 0:
            select_str += '.' + const.CONTENT_CLASS
        return select_str

    def generate_menu_selecter(self) -> str:
        """コンテンツのCSSセレクタを決定"""
        select_str = ""
        if len(const.NAV_TAG) > 0:
            select_str += const.NAV_TAG
        if len(const.NAV_ID) > 0:
            select_str += '#' + const.CONTENT_ID
        if len(const.NAV_CLASS) > 0:
            select_str += '.' + const.CONTENT_CLASS
        return select_str

    def clear_anchor(self, url:str) -> str:
        """アンカーを削除する
        アンカー以外のURLを書き換えたい場合などに使用
        """
        if not url is None and len(url) > 0:
            res = re.sub(self.ANCHOR_PTN, "", url)
            return res
        else :
            return ""

    def generate_page_filename(self, url:str) -> str:
        """Epubに内蔵されるページファイルの名称を設定"""
        # ドメインを削除した文字列
        url_dir = url.split('/')
        link_title = ""
        if len(url_dir) < 1:
            randlst = [random.choice(string.ascii_letters + string.digits) for i in range(10)]
            link_title = link_title.join(randlst)
        else:
            link_title = url_dir[len(url_dir) - 1]
        return link_title

    def generate_filename(self) ->str:
        """Epubのファイル名を設定"""
        match_list = self.DOMAIN_PTN.match(self.url)
        if not match_list is None:
            link_domain = re.sub("https://|http://", "", match_list.group())
            link_domain = re.sub("/", "_", link_domain)
        return link_domain

    def check_domain(self, url:str) ->str:
        """ドメイン名と比較"""
        root_domain = self.generate_filename()
        link_domain = ""
        match_list = self.DOMAIN_PTN.match(url)
        if not match_list is None:
            link_domain = re.sub("https://|http://", "", match_list.group())
            link_domain = re.sub("/", "_", link_domain)
        elif url.startswith('/'):
            return True
        link_domain_split = link_domain.split("_")
        root_domain_split = root_domain.split("_")
        root = root_domain
        target = link_domain
        if len(link_domain_split) > 0:
            target = link_domain_split[0]
        if len(root_domain_split) > 0:
            root = root_domain_split[0]
        return target == root
