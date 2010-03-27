Description
===========

Eztranet is an open-source application dedicated to private online video management.
Its main goal is to be easy and lightweight for the end user. It has been used
in production since 2007.

Current features:
-----------------

    - hierarchical storage with folders and files
    - can store several gigs of videos efficiently and safely
    - basic account management (admin/user)
    - basic permission management (read/modify)
    - video and photo upload with progress bar
    - multiple upload capability
    - simple wysiwyg editor for text areas
    - automatic transcoding of videos into flv
    - comments
    - automatic but configurable thumbnails

Technical details:
------------------

Eztranet is built on top of Zope 3.4, with additional components such as
z3c.form, z3c.pagelet, zc.async, and hachoir. Storage is handled by a blob-based
ZODB. This application is (doc)tested as much as possible. Migration to
BlueBream 1.0 is on the way. This application is currently tested only on Linux.

Demo
====

An online demo is avalaible here: http://eztranet.gorfou.fr
You can login with an administrator account: admin / eztranet

Installation and startup
========================

First install Python2.5 and ffmpeg with flv support
Download and extract the latest release on http://gorfou.fr/eztranet/
Then:

$ python2.5 bootstrap.py
$ ./bin/buidout
$ ./bin/eztranet-ctl fg

Contribute
==========

A clone is hosted on bitbucket: http://bitbucket.org/ccomb/eztranet/

Commercial Support
==================

Please contact us at: info gorfou.fr or http://gorfou.fr

