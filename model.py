"""モデルクラス"""
class MenuLink:
    """ページ"""
    page_id: str
    url: str
    file_name: str

    def __init__(self, page_id:str, url:str, file_name:str):
    # title
        self.page_id = page_id
        self.url = url
        self.file_name = file_name
    
    def check_url(self, url:str):
        """URLがリストに存在するかチェックする"""
        return self.url == url


class MenuList(MenuLink):
    """目次のセクションに当たる部分"""
    label: str
    sub_menu: list[any]
    tab: int

    def __init__(self, subitem:list, page_id:str, url:str, file_name:str):
        self.label = page_id
        self.sub_menu = subitem
        super().__init__(page_id, url, file_name)

    def check_url(self, url: str):
        if self.url == url:
            return True
        for link in self.sub_menu:
            if link.check_url(url):
                return True
        return False
