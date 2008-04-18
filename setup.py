from setuptools import setup, find_packages

setup(name='eztranet',

      # Fill in project info below
      version='1.1dev',
      description="",
      long_description="",
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Framework :: Zope3',
                   ],

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
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
                        'zope.formlib',
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
                        'zope.testbrowser'
                        ],
      entry_points = """
      [console_scripts]
      eztranet-debug = eztranet.startup:interactive_debug_prompt
      eztranet-ctl = eztranet.startup:zdaemon_controller
      [paste.app_factory]
      main = eztranet.startup:application_factory
      """
      )
