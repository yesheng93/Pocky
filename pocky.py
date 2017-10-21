import distutils.dir_util
import errno
import os
import re
import shutil
from io import open

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, BaseLoader

import settings

ENV = Environment(loader=FileSystemLoader(settings.TEMPLATE_DIR))
POSTS_DIR = settings.POSTS_DIR
_POSTS_DIR = settings._POSTS_DIR
_SITE_DIR = settings._SITE_DIR
SITE_DIR = settings.SITE_DIR
TEMPLATE_DIR = settings.TEMPLATE_DIR
ASSETS_DIR = settings.ASSETS_DIR


def register_handlers(handlers):
    return {handler.path: handler for handler in handlers}


site_handlers = register_handlers(settings.site_handlers)
posts_handlers = register_handlers(settings.post_handlers)

print 'handler registered'
print site_handlers
print posts_handlers


class Dict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


class SiteContext(Dict):
    def __init__(self):
        self.site = Dict(posts=[], pages=[])
        self.posts = self.site.posts
        self.pages = self.site.pages

    def collect_pages(self):
        del self.pages[:]
        for _page in os.listdir(_SITE_DIR):
            path = os.path.join(_SITE_DIR, _page)
            page = Poge(site=self)
            page.load_from_path(path)
            page.site = self
            page.fix_page_path()
            self.pages.append(page)

    def collect_posts(self):
        del self.posts[:]
        for _post in os.listdir(_POSTS_DIR):
            path = os.path.join(_POSTS_DIR, _post)
            post = Poge(site=self)
            post.load_from_path(path)
            post.fix_post_path()
            self.posts.append(post)

    def collect_poges(self):
        print 'collecting poges'
        self.collect_pages()
        self.collect_posts()
        print '{} posts and {} pages collected'.format(len(self.posts), len(self.pages))

    def generate_site(self):
        print 'generating files'
        for poges in self.posts + self.pages:
            poges.render(site=self)
            poges.save_to_file()
        print 'files generated'

    def load_context_from_config(self):
        with open('_config.yml') as f:
            # use safe_load instead load
            dataMap = yaml.safe_load(f)
            for tag in generate_tag_from_dict(dataMap):
                self._handle_tag(tag)

    def _handle_tag(self, tag):
        handler = site_handlers[tag.path] if tag.path in site_handlers else settings.default_site_handlers
        handler.handle(tag, self)


class Tag(object):
    def __init__(self, path=None, value=None):
        self.path = path
        self.value = value

    def __repr__(self):
        return str(self.path) + '  ' + str(self.value)


def generate_tag_from_dict(dic, tag_containers=[], root=''):
    for k, v in dic.iteritems():
        new_root = root + '/' + k
        if isinstance(v, dict):
            generate_tag_from_dict(v, tag_containers, new_root)
        else:
            tag_containers.append(Tag(new_root, v))
    return tag_containers


class Poge(Dict):
    def __init__(self):
        self.content = None
        self.rendered_content = None
        self.path = None
        self.layout = None

    def load_from_string(self, s):
        md = markdown.Markdown(extensions=['markdown.extensions.meta', 'markdown.extensions.codehilite',
                                           'markdown.extensions.fenced_code'])
        self.content = md.convert(s)
        self.load_context(s)

    def load_from_path(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.load_from_string(f.read())
            self.md_path = path

    # due to markdown's terrible implementation of yaml metadata
    def load_context(self, s):
        meta = s.split('---')[1]
        dataMap = yaml.safe_load(meta)
        for tag in generate_tag_from_dict(dataMap):
            self._handle_tag(tag)

    def _handle_tag(self, tag):
        handler = posts_handlers[tag.path] if tag.path in posts_handlers else settings.default_post_handlers
        handler.handle(tag, self)

    def fix_post_path(self):
        if self.path is None:
            file_name = os.path.basename(self.md_path)
            file_name = os.path.splitext(file_name)[0] + ".html"
            m = re.match(r'(\d{4}-\d{2}-\d{2})-(.*)', file_name)
            if m is None:
                print 'invalid filename'
            date = m.group(1)
            post_name = m.group(2)
            path = os.path.join(POSTS_DIR, date, post_name)
            self.path = path

    def fix_page_path(self):
        if self.path is None:
            self.path = os.path.join(os.path.splitext(self.md_path[len(_SITE_DIR) + 1:])[0] + '.html')

    def render(self, site):
        return
        # some content its self might contain template, such as index.html
        rtemplate = Environment(loader=BaseLoader).from_string(self.content)
        self.rendered_content = rtemplate.render(site=site)
        while self.layout is not None:
            template = ENV.get_template("{}.html".format(self.layout))
            self.layout = None
            self.rendered_content = template.render(content=self.rendered_content,
                                                    **{k: w for k, w in self.iteritems() if k != 'content'})
            md = markdown.Markdown(extensions=['markdown.extensions.meta', 'markdown.extensions.codehilite',
                                               'markdown.extensions.fenced_code'])
            self.rendered_content = md.convert(self.rendered_content)
            self.update(clean_dict(md.Meta))

    def save_to_file(self):
        return
        save_path = os.path.join(SITE_DIR, self.path)
        if not os.path.exists(os.path.dirname(save_path)):
            try:
                os.makedirs(os.path.dirname(save_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(save_path, "w", encoding="utf-8") as output:
            output.write(self.rendered_content)



def clean_dict(dic):
    for k, v in dic.iteritems():
        if isinstance(v, list) and len(v) == 1:
            dic[k] = v[0]
    return dic


def clean_dir_and_move_assets():
    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    # https://stackoverflow.com/questions/9160227/dir-util-copy-tree-fails-after-shutil-rmtree
    distutils.dir_util._path_created = {}
    distutils.dir_util.copy_tree(ASSETS_DIR, SITE_DIR)


def build_site():
    site = SiteContext()
    site.load_context_from_config()

    site.collect_poges()
    site.generate_site()
    print site
