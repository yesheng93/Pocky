class TagHandler(object):
    path = None

    @staticmethod
    def handle(tag, context):
        raise NotImplementedError


class DefaultTagHandler(TagHandler):
    @staticmethod
    def handle(tag, site_context):
        create_dictionary_recursively(site_context, tag.path, tag.value)


DefaultPogeTagHandler = DefaultTagHandler
DefaultSiteTagHandler = DefaultTagHandler


def create_dictionary_recursively(dic, path, value):
    paths = path.split('/')[1:]
    for key in paths[:-1]:
        if key not in dic:
            dic[key] = {}
        dic = dic[key]
    dic[paths[-1]] = value


class PostCategoryHandler(TagHandler):
    path = '/category'

    @staticmethod
    def handle(tag, post_context):
        site = post_context.site
        if 'category' not in site:
            site.category = {}
        if tag.value not in site.category:
            site.category[tag.value] = []
        site.category[tag.value].append(post_context)
