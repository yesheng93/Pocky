import SocketServer
import os
import posixpath
import urllib
from SimpleHTTPServer import SimpleHTTPRequestHandler

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from pocky import SITE_DIR, _POSTS_DIR, ASSETS_DIR, _SITE_DIR, build_site


class RootedHttpRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # http://louistiao.me/posts/python-simplehttpserver-recipe-serve-specific-directory/
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = SITE_DIR
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path


class FileChangeHandler(PatternMatchingEventHandler):
    patterns = ["*.*"]

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print event.src_path, event.event_type  # print now only for degug
        build_site()
        print 'finished rebuild'

    def on_any_event(self, event):
        self.process(event)


PORT = 9999


def run_server(handler_class=RootedHttpRequestHandler, server_class=SocketServer.TCPServer):
    m = handler_class.extensions_map
    m[''] = 'text/plain'
    m.update(dict([(k, v + ';charset=UTF-8') for k, v in m.items()]))
    server_class.allow_reuse_address = True
    httpd = server_class(("", PORT), handler_class)
    print "Serving at port", PORT
    httpd.serve_forever()
    httpd.shutdown()


def serve():
    observer = Observer()
    for path in [_POSTS_DIR, ASSETS_DIR, _SITE_DIR]:
        observer.schedule(FileChangeHandler(), path=path)
    observer.start()

    try:
        build_site()
        run_server()
    except KeyboardInterrupt:
        print '...shutting down'
        observer.stop()
    observer.join()
    print 'done'


if __name__ == '__main__':
    serve()
