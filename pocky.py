import distutils.dir_util
import errno
import os
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
page_handlers = register_handlers(settings.page_handlers)

print 'handler registered'
print site_handlers
print page_handlers


class Dict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


class Site(Dict):
    def __init__(self):
        self.posts = []
        self.pages = []

    def _collect_from_dir(self, dir, is_post=False):
        for _page in os.listdir(dir):
            path = os.path.join(dir, _page)
            page = Page()
            page._site = self
            page.is_post = is_post
            page.load_from_path(path)
            page.load_yaml_tag()
            page.run_processor()
            if is_post:
                self.posts.append(page)
            else:
                self.pages.append(page)

    def collect_poges(self):
        print 'collecting poges'
        self._collect_from_dir(_POSTS_DIR, is_post=True)
        self._collect_from_dir(_SITE_DIR, is_post=False)
        print '{} posts and {} pages collected'.format(len(self.posts), len(self.pages))

    def run_processor(self):
        for processor in settings.site_processors:
            processor.process(self)

    def generate_site(self):
        print 'generating files'
        for poges in self.posts + self.pages:
            poges.render(site=self)
            poges.save_to_file()
        print 'files generated'

    def configuration(self):
        with open('_config.yml') as f:
            # use safe_load instead load
            dataMap = yaml.safe_load(f)
            for tag in generate_tag_from_dict(dataMap, []):
                self._handle_tag(tag)
        print 'finishedloading'

    def _handle_tag(self, tag):
        handler = site_handlers[tag.path] if tag.path in site_handlers else settings.default_site_handlers
        handler.handle(tag, self)


class Tag(object):
    def __init__(self, path=None, value=None):
        self.path = path
        self.value = value

    def __repr__(self):
        return str(self.path) + '  ' + str(self.value)


def generate_tag_from_dict(dic, tag_containers, root=''):
    for k, v in dic.iteritems():
        new_root = root + '/' + k
        if isinstance(v, dict):
            generate_tag_from_dict(v, tag_containers, new_root)
        else:
            tag_containers.append(Tag(new_root, v))
    return tag_containers


class Page(Dict):
    def __init__(self):
        self.content = None
        self.rendered_content = None
        self.path = None
        self.layout = None
        self._site = None
        self.is_post = False

    def load_from_path(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.load_from_string(f.read())
            # actual path could be specified in meta data
            self.original_file_path = path

    def load_from_string(self, s):
        md = markdown.Markdown(extensions=['markdown.extensions.meta', 'markdown.extensions.codehilite',
                                           'markdown.extensions.fenced_code'])
        self.content = md.convert(s)
        self.yaml = s.split('---')[1]

    def load_yaml_tag(self):
        meta_map = yaml.safe_load(self.yaml)
        for tag in generate_tag_from_dict(meta_map, []):
            self._handle_tag(tag)

    def run_processor(self):
        for processor in settings.page_processors:
            processor.process(self._site, self)

    def _handle_tag(self, tag):
        handler = page_handlers[tag.path] if tag.path in page_handlers else settings.default_page_handlers
        handler.handle(tag, self._site, self)

    def render(self, site):
        # some content its self might contain template, such as index.html
        rtemplate = Environment(loader=BaseLoader).from_string(self.content)
        self.rendered_content = rtemplate.render(site=site)
        while self.layout is not None:
            template = ENV.get_template("{}.html".format(self.layout))
            self.layout = None
            self.rendered_content = template.render(site=site, content=self.rendered_content,
                                                    **{k: w for k, w in self.iteritems() if k != 'content'})
            md = markdown.Markdown(extensions=['markdown.extensions.meta', 'markdown.extensions.codehilite',
                                               'markdown.extensions.fenced_code'])
            self.rendered_content = md.convert(self.rendered_content)
            new_meta = clean_dict(md.Meta)
            for tag in generate_tag_from_dict(new_meta, []):
                self._handle_tag(tag)

    def save_to_file(self):
        save_path = os.path.join(SITE_DIR, self.path)
        if not os.path.exists(os.path.dirname(save_path)):
            try:
                os.makedirs(os.path.dirname(save_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(save_path, "w", encoding="utf-8") as output:
            output.write(self.rendered_content)

    def __repr__(self):
        return self.title


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
    clean_dir_and_move_assets()
    site = Site()
    site.configuration()
    site.collect_poges()
    site.run_processor()
    site.generate_site()
    print site
    return site
