from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding
from eztranet.project.interfaces import IProjectItem, IProject
from eztranet.interfaces import IEztranetSite
from eztranet.project.project import ProjectItem, ProjectVideo, ProjectImage
from eztranet.comment.comments import Comments, Comment
from tempfile import mkstemp

def fix_annotations(item, newitem=None):
    """fix or copy annotations"""
    if newitem:
        newitem.__annotations__ = item.__annotations__
    annotations = item.__annotations__
    if 'comment.comments' in annotations:
        annotations['eztranet.comment'] = Comments()
        annotations['eztranet.comment'].__setstate__(annotations['comment.comments'].__getstate__())
        if newitem:
            annotations['eztranet.comment'].__parent__ = newitem
        else:
            annotations['eztranet.comment'].__parent__ = item
        for c in annotations['eztranet.comment'].comments:
            comment = annotations['eztranet.comment'].comments[c].__getstate__()
            annotations['eztranet.comment'].comments[c] = Comment('')
            annotations['eztranet.comment'].comments[c].__setstate__(comment)
            annotations['eztranet.comment'].comments[c].__parent__ = annotations['eztranet.comment']
        del annotations['comment.comments']
       
def evolve(context):
    u"""
    evolution script from version 0 to version 1 of the db schema
    (from eztranet 1.0 to eztranet 1.1)
    """

    # Eztranet site
    for site in findObjectsProviding(getRootFolder(context),IEztranetSite):
        if not hasattr(site, 'title'):
            site.title=None

    # Project items
    for item in findObjectsProviding(getRootFolder(context),IProjectItem):
        if type(item) is ProjectVideo:
            newitem = ProjectVideo()
        if type(item) is ProjectImage:
            newitem = ProjectImage()
        # file content
        if item._data._data is not None:
            handle,filename = mkstemp()
            file = open(filename, 'w')
            file.write(item._data._data)
            file.close()
            newitem._data.consumeFile(filename)
        # attributes
        newitem.title = item.title
        newitem.description = item.description
        newitem.mimeType = item.contentType
        newitem.__name__ = item.__name__
        newitem.__parent = item.__parent__
        newitem.parameters = {}
        # annotations
        fix_annotations(item, newitem)

        # parent (must be done at the end)
        parent = item.__parent__
        newitemname = item.__name__
        del parent[newitemname]
        parent[newitemname] = newitem

    # Projects
    for item in findObjectsProviding(getRootFolder(context),IProject):
        # annotations
        fix_annotations(item)
