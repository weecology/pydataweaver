
class Script(object):
    """This class represents a database toolkit script. Scripts should inherit
    from this class and execute their code in the download method."""

    def __init__(self, title="", description="", name="", urls=dict(),
                 tables=dict(), ref="", public=True, addendum=None, citation="Not currently available",
                 retriever_minimum_version="", version="", encoding="",message="", **kwargs):

        self.title = title
        self.name = name
        self.filename = __name__
        self.description = description
        self.urls = urls
        self.tables = tables
        self.ref = ref
        self.public = public
        self.addendum = addendum
        self.citation = citation
        self.keywords = []
        self.retriever_minimum_version = retriever_minimum_version
        self.encoding = encoding
        self.version = version
        self.message=message
        for key, item in list(kwargs.items()):
            setattr(self, key, item[0] if isinstance(item, tuple) else item)
