from setuptools import setup, find_packages
import os

version = '0.5.6.dev0'

setup(name='z3c.soap',
      version=version,
      description="Soap using ZSI in Zope 2",
      long_description=open(os.path.join("z3c", "soap",
                                         "README.txt")).read() + "\n" +
                       open(os.path.join("z3c", "soap",
                                         "mem.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Framework :: Zope :: 3",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Libraries :: Python Modules"],
      keywords='Zope2 SOAP ZSI',
      author='Jean-Francois Roche',
      author_email='jfroche@affinitic.be',
      url='https://github.com/zopefoundation/z3c.soap',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(test=['zope.testing',
                                'zope.app.testing',
                                'zope.app.folder',
                                'zope.app.publication[test]']),
      install_requires=[
          'setuptools',
          'Products.PluggableAuthService',
          'ZSI'],)
