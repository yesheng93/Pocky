import handlers

default_site_handlers = handlers.DefaultSiteTagHandler
site_handlers = [
    handlers.DefaultSiteTagHandler
]

default_post_handlers = handlers.DefaultPogeTagHandler

post_handlers = [
    handlers.DefaultPogeTagHandler,
    handlers.PostCategoryHandler
]

POSTS_DIR = 'posts'

_POSTS_DIR = '_posts'

_SITE_DIR = '_site'

SITE_DIR = 'site'

TEMPLATE_DIR = '_layout'

ASSETS_DIR = '_assets'
