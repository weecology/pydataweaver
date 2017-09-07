from __future__ import print_function
from future import standard_library
standard_library.install_aliases()



class Vector(object):
    """GIS vector data"""

    def __init__(self, title="", description="", name="", urls=dict(),
                 tables=dict(), ref="", public=True, addendum=None, citation="Not currently available",
                  version="", encoding="",message="", **kwargs):

        self.title = title
        self.name = name
        self.filename = __name__
        self.description = description
        self.urls = urls

