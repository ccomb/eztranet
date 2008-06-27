from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding
from eztranet.project.interfaces import IProjectItem, IProject
from eztranet.interfaces import IEztranetSite
from eztranet.project.project import ProjectItem, ProjectVideo, ProjectImage
from eztranet.comment.comments import Comments, Comment
from tempfile import mkstemp
from zope.component import ComponentLookupError
from zope.interface import Interface
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog.interfaces import ICatalog
import os
import time

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
    root = getRootFolder(context)

    # Eztranet site
    for site in findObjectsProviding(root, IEztranetSite):
        if not hasattr(site, 'title'):
            site.title=None
        # remove the intid and catalog since it creates cyclic refs
        sm = site.getSiteManager()
        sm.unregisterUtility(sm['catalog'], ICatalog)
        sm.unregisterUtility(sm['unique integer IDs'], IIntIds)
        del sm['catalog']
        del sm['unique integer IDs']

    # Projects
    for item in findObjectsProviding(root, IProject):
        # annotations
        fix_annotations(item)
        
    # Project items
    for item in findObjectsProviding(root, IProjectItem):
        # this works only on GNU systems
        while 'ffmpeg' in os.popen('ps -eo comm').read().split():
            time.sleep(2)
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
        newitem.title = item.title.split('\\')[-1]
        newitem.description = item.description
        newitem.mimeType = item.contentType
        newitem.__name__ = item.__name__.split('\\')[-1]
        newitem.__parent = item.__parent__
        newitem.parameters = {}
        # annotations
        fix_annotations(item, newitem)

        # parent (must be done at the end)
        parent = item.__parent__
        newitemname = item.__name__
        del parent[newitemname]
        parent[newitemname] = newitem



