import os
import re


class SiteProcessor(object):
    @staticmethod
    def process(site):
        raise NotImplementedError


class PageProcessor(object):
    @staticmethod
    def process(site, page):
        raise NotImplementedError


"""
processors start here
"""


class PostOrderedByDate(SiteProcessor):
    @staticmethod
    def process(site):
        print 'posts ordered'


class FixPostDateAndPath(PageProcessor):
    @staticmethod
    def process(site, page):
        if page.is_post:
            file_name = os.path.basename(page.original_file_path)
            html_name = os.path.splitext(file_name)[0] + ".html"
            m = re.match(r'(\d{4}-\d{2}-\d{2})-(.*)', html_name)
            if m is None:
                raise Exception('invalid file name')
            if not hasattr(page, 'date'):
                page.date = m.group(1)
            post_name = m.group(2)
            # if not specified in the meta data
            if page.path is None:
                from settings import POSTS_DIR
                path = os.path.join(POSTS_DIR, page.date, post_name)
                page.path = path
        else:
            if page.path is None:
                from settings import _SITE_DIR
                page.path = os.path.join(os.path.splitext(page.original_file_path[len(_SITE_DIR) + 1:])[0] + '.html')


class SortPostsByDateProcessor(SiteProcessor):
    @staticmethod
    def process(site):
        site.posts.sort(key=lambda x: x.date, reverse=True)
        print site.posts
