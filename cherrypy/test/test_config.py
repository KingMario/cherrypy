"""Tests for the CherryPy configuration system."""
from cherrypy.test import test
test.prefer_parent_path()

import StringIO
import cherrypy


def setup_server():
    
    class Root:
        
        _cp_config = {'foo': 'this',
                      'bar': 'that'}
        
        def index(self, key):
            return cherrypy.config.get(key, "None")
        index.exposed = True
        global_ = index
        xyz = index
    
    class Foo:
        
        _cp_config = {'foo': 'this2',
                      'baz': 'that2'}
        
        def index(self, key):
            return cherrypy.config.get(key, "None")
        index.exposed = True
        nex = index
        
        def bar(self, key):
            return cherrypy.config.get(key, "None")
        bar.exposed = True
        bar._cp_config = {'foo': 'this3', 'bax': 'this4'}
    
    class Another:
        
        def index(self, key):
            return str(cherrypy.config.get(key, "None"))
        index.exposed = True
    
    root = Root()
    root.foo = Foo()
    cherrypy.tree.mount(root)
    cherrypy.tree.mount(Another(), "/another")
    cherrypy.config.update({'environment': 'test_suite'})
    
    # Shortcut syntax--should get put in the "global" bucket
    cherrypy.config.update({'luxuryyacht': 'throatwobblermangrove'})


#                             Client-side code                             #

from cherrypy.test import helper

class ConfigTests(helper.CPWebCase):
    
    def testConfig(self):
        tests = [
            ('/',        'nex', 'None'),
            ('/',        'foo', 'this'),
            ('/',        'bar', 'that'),
            ('/xyz',     'foo', 'this'),
            ('/foo/',    'foo', 'this2'),
            ('/foo/',    'bar', 'that'),
            ('/foo/',    'bax', 'None'),
            ('/foo/bar', 'baz', 'that2'),
            ('/foo/nex', 'baz', 'that2'),
            # If 'foo' == 'this', then the mount point '/another' leaks into '/'.
            ('/another/','foo', 'None'),
        ]
        for path, key, expected in tests:
            self.getPage(path + "?key=" + key)
            self.assertBody(expected)


if __name__ == '__main__':
    setup_server()
    helper.testmain()
