from osbot_utils.type_safe.Type_Safe    import Type_Safe
from osbot_utils.utils.Http             import url_join_safe
from sg_send_qa.browser.QA_Browser      import QA_Browser

URL__SG_SEND__LOCALHOST = "http://localhost:10062/en-gb/"

class SG_Send__Browser__Pages(Type_Safe):
    qa_browser : QA_Browser

    def chrome(self):
        return self.qa_browser.chrome()
 
    def open(self, path):
        url  = self.url__for_path(path)
        page = self.qa_browser.open(url)
        return page

    def page(self):
        return self.qa_browser.page()

    def url__target_server(self):
        return URL__SG_SEND__LOCALHOST

    def url__for_path(self, path):
        return url_join_safe(self.url__target_server(), path)


    # --- pages

    def page__browse(self):
        return self.open("browse")

    def page__download(self):
        return self.open("download")

    def page__gallery(self):
        return self.open("gallery")

    def page__root(self):
        return self.open("")

