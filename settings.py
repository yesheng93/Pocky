import handlers
from processors import FixPostDateAndPath, SortPostsByDateProcessor

default_site_handlers = handlers.DefaultSiteTagHandler
site_handlers = [
    handlers.DefaultSiteTagHandler
]

default_page_handlers = handlers.DefaultPageTagHandler

page_handlers = [
    handlers.DefaultPageTagHandler,
    handlers.PostCategoryHandler
]
site_processors = [
    SortPostsByDateProcessor
]

page_processors = [
    FixPostDateAndPath
]

POSTS_DIR = 'posts'

_POSTS_DIR = '_posts'

_SITE_DIR = '_site'

SITE_DIR = 'site'

TEMPLATE_DIR = '_layout'

ASSETS_DIR = '_assets'
