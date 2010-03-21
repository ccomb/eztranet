from setuptools import setup, find_packages

setup(name='eztranet',

      # Fill in project info below
      version='1.3.0dev',
      description="",
      long_description="",
      keywords='eztranet extranet video photo',
      author='Christophe Combelles',
      author_email='ccomb@free.fr',
      url='http://gorfou.fr/site/eztranet.html',
      license='ZPL',
      # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Framework :: Zope3',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: Zope Public License',
                   'Topic :: Multimedia :: Video',
                   ],

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      extras_require={'debug': ['repoze.profile', 'gprof2dot']},
      install_requires=['setuptools',
                        'ZODB3',
                        'ZConfig',
                        'zdaemon',
                        'zope.publisher',
                        'zope.traversing',
                        'zope.app.wsgi>=3.4.0',
                        'zope.app.appsetup',
                        'zope.app.zcmlfiles',
                        # The following packages aren't needed from the
                        # beginning, but end up being used in most apps
                        'zope.annotation',
                        'zope.copypastemove',
                        'zope.i18n',
                        'zope.app.authentication',
                        'zope.app.session',
                        'zope.app.intid',
                        'zope.app.keyreference',
                        'zope.app.catalog',
                        # The following packages are needed for functional
                        # tests only
                        'zope.testing',
                        'zope.app.testing',
                        'zope.app.securitypolicy',
                        'zope.securitypolicy',
                        'zope.contentprovider',
                        'zope.app.file',
                        'zope.app.container',
                        'zope.dublincore',
                        'zope.app.security',
                        'zope.mimetype',
                        'zope.file',
                        'zope.testbrowser',
                        'zope.viewlet',
                        'z3c.layer.pagelet',
                        'hachoir_core',
                        'hachoir_parser',
                        'zope.index',
                        'z3c.pagelet',
                        'z3c.layer.pagelet',
                        'z3c.template',
                        'z3c.macro',
                        'z3c.contents',
                        'z3c.menu.simple',
                        'z3c.form',
                        'z3c.formui',
                        'zc.async[z3]',
                        ],
      entry_points = """
      [console_scripts]
      eztranet-debug = eztranet.startup:interactive_debug_prompt
      eztranet-ctl = eztranet.startup:zdaemon_controller
      [paste.app_factory]
      main = eztranet.startup:application_factory
      """
      )
