class SiteTagHandler(object):
    path = None

    @staticmethod
    def handle(tag, site_context):
        raise NotImplementedError


class PageTagHandler(object):
    path = None

    @staticmethod
    def handle(tag, site_context, page_contex):
        raise NotImplementedError


def create_dictionary_recursively(dic, path, value):
    paths = path.split('/')[1:]
    for key in paths[:-1]:
        if key not in dic:
            dic[key] = {}
        dic = dic[key]
    dic[paths[-1]] = value


"""
handlers starts here
"""


class DefaultSiteTagHandler(SiteTagHandler):
    @staticmethod
    def handle(tag, site_context):
        create_dictionary_recursively(site_context, tag.path, tag.value)


class DefaultPageTagHandler(SiteTagHandler):
    @staticmethod
    def handle(tag, site_context, page_contex):
        create_dictionary_recursively(page_contex, tag.path, tag.value)


class PostCategoryHandler(DefaultPageTagHandler):
    path = '/category'

    @staticmethod
    def handle(tag, site_context, page_contex):
        if 'category' not in site_context:
            site_context.category = {}
        if tag.value not in site_context.category:
            site_context.category[tag.value] = []
        site_context.category[tag.value].append(page_contex)
