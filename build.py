#!/usr/bin/python

# Copyright (c) 2007 Henri Sivonen
#
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import os
import shutil
import urllib
import re
import md5
import zipfile
import sys
from sgmllib import SGMLParser

javacCmd = 'javac'
jarCmd = 'jar'
javaCmd = 'java'
javadocCmd = 'javadoc'
svnCmd = 'svn'

buildRoot = '.'
svnRoot = 'http://svn.versiondude.net/whattf/'
portNumber = '8888'
useAjp = 0
log4jProps = 'validator/log4j.properties'
heapSize = '64'
html5specLink = 'http://www.whatwg.org/specs/web-apps/current-work/'
html5specLoad = 'http://about.validator.nu/spec.html'
ianaLang = 'http://www.iana.org/assignments/language-subtag-registry'
aboutPage = 'http://about.validator.nu/'
microsyntax = 'http://wiki.whatwg.org/wiki/MicrosyntaxDescriptions'
stylesheet = None
script = None
serviceName = 'Validator.nu'
maxFileSize = 2048
usePromiscuousSsl = 0
genericHost = ''
html5Host = ''
parsetreeHost = ''
genericPath = '/'
html5Path = '/html5/'
parsetreePath = '/parsetree/'

dependencyPackages = [
  ("http://www.nic.funet.fi/pub/mirrors/apache.org/commons/codec/binaries/commons-codec-1.3.zip", "c30c769e07339390862907504ff4b300"),
  ("http://mirror.eunet.fi/apache/httpcomponents/commons-httpclient/binary/commons-httpclient-3.1.zip", "1752a2dc65e2fb03d4e762a8e7a1db49"),
  ("http://www.nic.funet.fi/pub/mirrors/apache.org/commons/logging/binaries/commons-logging-1.1.zip", "cc4d307492a48e27fbfeeb04d59c6578"),
  ("http://download.icu-project.org/files/icu4j/3.8.1/icu4j-3_8_1.jar", "16db643b3a65c5fe1c78954be60241b8"),
  ("http://download.icu-project.org/files/icu4j/3.8.1/icu4j-charsets-3_8_1.jar", "ea30850dbbc32a8e879ab0f01698bc92"),
  ("http://switch.dl.sourceforge.net/sourceforge/jena/iri-0.5.zip", "87b0069e689c22ba2a2b50f4d200caca"),
  ("http://dist.codehaus.org/jetty/jetty-6.1.7/jetty-6.1.7.zip", "22b79a589bce55bc05f14fc974a24adf"),
  ("http://mirror.eunet.fi/apache/logging/log4j/1.2.14/logging-log4j-1.2.14.zip", "6c4f8da1fed407798ea0ad7984fe60db"),
  ("http://mirror.eunet.fi/apache/xml/xerces-j/Xerces-J-bin.2.9.0.zip", "a3aece3feb68be6d319072b85ad06023"),
  ("http://ftp.mozilla.org/pub/mozilla.org/js/rhino1_6R5.zip", "c93b6d0bb8ba83c3760efeb30525728a"),
  ("http://download.berlios.de/jsontools/jsontools-core-1.5.jar", "1f242910350f28d1ac4014928075becd"),
  ("http://hsivonen.iki.fi/code/antlr.jar", "9d2e9848c52204275c72d9d6e79f307c"),
  ("http://www.cafeconleche.org/XOM/xom-1.1.jar", "6b5e76db86d7ae32a451ffdb6fce0764"),
  ("http://www.slf4j.org/dist/slf4j-1.4.3.zip", "5671faa7d5aecbd06d62cf91f990f80a"),
  ("http://www.nic.funet.fi/pub/mirrors/apache.org/commons/fileupload/binaries/commons-fileupload-1.2-bin.zip", "6fbe6112ebb87a9087da8ca1f8d8fd6a"),
#  ("http://mirror.eunet.fi/apache/xml/xalan-j/xalan-j_2_7_1-bin.zip", "99d049717c9d37a930450e630d8a6531"),
  ("http://mirror.eunet.fi/apache/ant/binaries/apache-ant-1.7.0-bin.zip" , "ac30ce5b07b0018d65203fbc680968f5"),
  ("http://surfnet.dl.sourceforge.net/sourceforge/iso-relax/isorelax.20041111.zip" , "10381903828d30e36252910679fcbab6"),
  ("http://ovh.dl.sourceforge.net/sourceforge/junit/junit-4.4.jar", "f852bbb2bbe0471cef8e5b833cb36078"),
  ("http://dist.codehaus.org/stax/jars/stax-api-1.0.1.jar", "7d436a53c64490bee564c576babb36b4"),
  ("http://jdom.org/dist/binary/jdom-1.1.zip", "4073be59361ef017a04f9a67c7be8d98"),
  ("http://kent.dl.sourceforge.net/sourceforge/dom4j/dom4j-1.6.1.jar", "4d8f51d3fe3900efc6e395be48030d6d"),
]

# Unfortunately, the packages contain old versions of certain libs, so 
# can't just autodiscover all jars. Hence, an explicit list.
dependencyJars = [
  "commons-codec-1.3/commons-codec-1.3.jar",
  "commons-httpclient-3.1/commons-httpclient-3.1.jar",
  "commons-logging-1.1/commons-logging-1.1.jar",
  "commons-logging-1.1/commons-logging-adapters-1.1.jar",
  "commons-logging-1.1/commons-logging-api-1.1.jar",
  "icu4j-charsets-3_8_1.jar",
  "icu4j-3_8_1.jar",
  "iri-0.5/lib/iri.jar",
  "jetty-6.1.7/lib/servlet-api-2.5-6.1.7.jar",
  "jetty-6.1.7/lib/jetty-6.1.7.jar",
  "jetty-6.1.7/lib/jetty-util-6.1.7.jar",
  "jetty-6.1.7/lib/ext/jetty-ajp-6.1.7.jar",
  "jetty-6.1.7/lib/ext/jetty-java5-threadpool-6.1.7.jar",
  "logging-log4j-1.2.14/dist/lib/log4j-1.2.14.jar",
  "rhino1_6R5/js.jar",
  "xerces-2_9_0/xercesImpl.jar",
  "xerces-2_9_0/xml-apis.jar",
  "xerces-2_9_0/serializer.jar",
  "jsontools-core-1.5.jar",
  "antlr.jar",
  "xom-1.1.jar",
  "slf4j-1.4.3/slf4j-log4j12-1.4.3.jar",
 # "slf4j-1.4.3/slf4j-api-1.4.3.jar",
  "commons-fileupload-1.2/lib/commons-fileupload-1.2.jar",
#  "xalan-j_2_7_1/xalan.jar",
  "junit-4.4.jar",
  "isorelax.jar",
  "apache-ant-1.7.0/lib/ant.jar",
  "apache-ant-1.7.0/lib/ant-launcher.jar",
  "stax-api-1.0.1.jar",
  "jdom-1.1/build/jdom.jar",
  "dom4j-1.6.1.jar",
]

moduleNames = [
  "build",
  "syntax",
  "util",
  "htmlparser",
  "xmlparser",
  "onvdl",
  "validator",
]

directoryPat = re.compile(r'^[a-zA-Z0-9_-]+/$')
leafPat = re.compile(r'^[a-zA-Z0-9_-]+\.[a-z]+$')

class UrlExtractor(SGMLParser):
  def __init__(self, baseUrl):
    SGMLParser.__init__(self)
    self.baseUrl = baseUrl
    self.leaves = []
    self.directories = []
    
  def start_a(self, attrs):
    for name, value in attrs:
      if name == "href":
        if directoryPat.match(value):
          self.directories.append(self.baseUrl + value)
        if leafPat.match(value):
          self.leaves.append(self.baseUrl + value)    
    
def runCmd(cmd):
  print cmd
  os.system(cmd)

def execCmd(cmd, args):
  print "%s %s" % (cmd, " ".join(args))
  if os.execvp(cmd, [cmd,] + args):
    print "Command failed."
    sys.exit(2)

def removeIfExists(filePath):
  if os.path.exists(filePath):
    os.unlink(filePath)

def removeIfDirExists(dirPath):
  if os.path.exists(dirPath):
    shutil.rmtree(dirPath)

def ensureDirExists(dirPath):
  if not os.path.exists(dirPath):
    os.makedirs(dirPath)

def findFilesWithExtension(directory, extension):
  rv = []
  ext = '.' + extension 
  for root, dirs, files in os.walk(directory):
    for file in files:
      if file.endswith(ext):
        rv.append(os.path.join(root, file))
  return rv

def findFiles(directory):
  rv = []
  for root, dirs, files in os.walk(directory):
    for file in files:
      candidate = os.path.join(root, file)
      if candidate.find("/.svn") == -1:
        rv.append(candidate)
  return rv


def jarNamesToPaths(names):
  return map(lambda x: os.path.join(buildRoot, "jars", x + ".jar"), names)

def runJavac(sourceDir, classDir, classPath):
  sourceFiles = findFilesWithExtension(sourceDir, "java")
  f = open("temp-javac-list", "w")
  f.write("\n".join(sourceFiles))
  f.close()
  runCmd("'%s' -nowarn -classpath '%s' -sourcepath '%s' -d '%s' %s"\
		% (javacCmd, classPath, sourceDir, classDir, "@temp-javac-list"))
  removeIfExists("temp-javac-list")

def copyFiles(sourceDir, classDir):
  files = findFiles(sourceDir)
  for f in files:
    destFile = os.path.join(classDir, f[len(sourceDir)+1:])
    head, tail = os.path.split(destFile)
    if not os.path.exists(head):
      os.makedirs(head)
    shutil.copyfile(f, destFile)

def runJar(classDir, jarFile, sourceDir):
  classFiles = findFiles(classDir)
  classList = map(lambda x: 
                    "-C '" + classDir + "' '" + x[len(classDir)+1:] + "'", 
                  classFiles)
  f = open("temp-jar-list", "w")
  f.write("\n".join(classList))
  f.close()
  runCmd("'%s' cf '%s' %s" 
    % (jarCmd, jarFile, "@temp-jar-list"))
  removeIfExists("temp-jar-list")

def buildModule(rootDir, jarName, classPath):
  sourceDir = os.path.join(rootDir, "src")
  classDir = os.path.join(rootDir, "classes")
  distDir = os.path.join(rootDir, "dist")
  jarFile = os.path.join(distDir, jarName + ".jar")
  removeIfExists(jarFile)
  removeIfDirExists(classDir)
  ensureDirExists(classDir)
  ensureDirExists(distDir)
  runJavac(sourceDir, classDir, classPath)
  copyFiles(sourceDir, classDir)
  runJar(classDir, jarFile, sourceDir)
  ensureDirExists(os.path.join(buildRoot, "jars"))
  shutil.copyfile(jarFile, os.path.join(buildRoot, "jars", jarName + ".jar"))

def dependencyJarPaths():
  dependencyDir = os.path.join(buildRoot, "dependencies")
  extrasDir = os.path.join(buildRoot, "extras")
  # XXX may need work for Windows portability
  pathList = map(lambda x: os.path.join(dependencyDir, x), dependencyJars)
  ensureDirExists(extrasDir)
  pathList += findFilesWithExtension(extrasDir, "jar")
  return pathList

def buildUtil():
  classPath = os.pathsep.join(dependencyJarPaths())
  buildModule(
    os.path.join(buildRoot, "util"), 
    "io-xml-util", 
    classPath)

def buildDatatypeLibrary():
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["onvdl-whattf"]))
  buildModule(
    os.path.join(buildRoot, "syntax", "relaxng", "datatype", "java"), 
    "html5-datatypes", 
    classPath)

def buildNonSchema():
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["html5-datatypes",
                                                "onvdl-whattf"]))
  buildModule(
    os.path.join(buildRoot, "syntax", "non-schema", "java"), 
    "non-schema", 
    classPath)

def buildXmlParser():
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["htmlparser", "io-xml-util"]))
  buildModule(
    os.path.join(buildRoot, "xmlparser"), 
    "hs-aelfred2", 
    classPath)

def buildHtmlParser():
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["io-xml-util"]))
  buildModule(
    os.path.join(buildRoot, "htmlparser"), 
    "htmlparser", 
    classPath)

def buildSaxon():
  classPath = os.pathsep.join(dependencyJarPaths())
  buildModule(
    os.path.join(buildRoot, "onvdl", "saxon"), 
    "saxon-whattf", 
    classPath)

def buildOnvdl():
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["saxon-whattf"]))
  buildModule(
    os.path.join(buildRoot, "onvdl"), 
    "onvdl-whattf", 
    classPath)


def buildValidator():
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["non-schema", 
                                                "io-xml-util",
                                                "htmlparser",
                                                "hs-aelfred2",
                                                "html5-datatypes",
                                                "onvdl-whattf"]))
  buildModule(
    os.path.join(buildRoot, "validator"), 
    "validator", 
    classPath)

def buildTestHarness():
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["non-schema", 
                                                "io-xml-util",
                                                "htmlparser",
                                                "hs-aelfred2",
                                                "onvdl-whattf"]))
  buildModule(
    os.path.join(buildRoot, "syntax", "relaxng", "tests", "jdriver"), 
    "test-harness", 
    classPath)

def runValidator():
  ensureDirExists(os.path.join(buildRoot, "logs"))
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["non-schema", 
                                                "io-xml-util",
                                                "htmlparser",
                                                "hs-aelfred2",
                                                "html5-datatypes",
                                                "validator",
                                                "onvdl-whattf",
                                                "saxon-whattf"]))
  args = [
    '-Xms%sm' % heapSize,
    '-Xmx%sm' % heapSize,
    '-XX:ThreadStackSize=2048',
    '-cp',
    classPath,
    '-Dnu.validator.servlet.log4j-properties=' + log4jProps,
    '-Dnu.validator.servlet.presetconfpath=validator/presets.txt',
    '-Dnu.validator.servlet.cachepathprefix=local-entities/',
    '-Dnu.validator.servlet.cacheconfpath=validator/entity-map.txt',
    '-Dnu.validator.servlet.version=3',
    '-Dnu.validator.servlet.service-name=' + serviceName,
    '-Dorg.whattf.datatype.lang-registry=' + ianaLang,
    '-Dnu.validator.servlet.about-page=' + aboutPage,
    '-Dnu.validator.servlet.style-sheet=' + stylesheet,
    '-Dnu.validator.servlet.script=' + script,
    '-Dnu.validator.spec.microsyntax-descriptions=' + microsyntax,
    '-Dnu.validator.spec.html5-load=' + html5specLoad,
    '-Dnu.validator.spec.html5-link=' + html5specLink,
    '-Dnu.validator.servlet.max-file-size=%d' % (maxFileSize * 1024),
    '-Dorg.mortbay.http.HttpRequest.maxFormContentSize=%d' % (maxFileSize * 1024),
    '-Dnu.validator.servlet.host.generic=' + genericHost,
    '-Dnu.validator.servlet.host.html5=' + html5Host,
    '-Dnu.validator.servlet.host.parsetree=' + parsetreeHost,
    '-Dnu.validator.servlet.path.generic=' + genericPath,
    '-Dnu.validator.servlet.path.html5=' + html5Path,
    '-Dnu.validator.servlet.path.parsetree=' + parsetreePath,
  ]

  if usePromiscuousSsl:
    args.append('-Dnu.validator.xml.promiscuous-ssl=true')  

  args.append('nu.validator.servlet.Main')
  
  if useAjp:
    args.append('ajp')
  args.append(portNumber)
  execCmd(javaCmd, args)

def fetchUrlTo(url, path, md5sum=None):
  # I bet there's a way to do this with more efficient IO and less memory
  print url
  f = urllib.urlopen(url)
  data = f.read()
  f.close()
  if md5sum:
    m = md5.new(data)
    if md5sum != m.hexdigest():
      print "Bad MD5 hash for %s." % url
      sys.exit(1)
  head, tail = os.path.split(path)
  if not os.path.exists(head):
    os.makedirs(head)
  f = open(path, "wb")
  f.write(data)
  f.close()

def spiderApacheDirectories(baseUrl, baseDir):
  f = urllib.urlopen(baseUrl)
  parser = UrlExtractor(baseUrl)
  parser.feed(f.read())
  f.close()
  parser.close()
  for leaf in parser.leaves:
    fetchUrlTo(leaf, os.path.join(baseDir, leaf[7:]))
  for directory in parser.directories:
    spiderApacheDirectories(directory, baseDir)

def downloadLocalEntities():
  ensureDirExists(os.path.join(buildRoot, "local-entities"))
  if not os.path.exists(os.path.join(buildRoot, "local-entities", "syntax")):
    # XXX not portable to Windows
    os.symlink(os.path.join("..", "syntax"), 
               os.path.join(buildRoot, "local-entities", "syntax"))
  if not os.path.exists(os.path.join(buildRoot, "local-entities", "schema")):
    # XXX not portable to Windows
    os.symlink(os.path.join("..", "validator", "schema"), 
               os.path.join(buildRoot, "local-entities", "schema"))
  if not os.path.exists(os.path.join(buildRoot, "validator", "schema", "html5")):
    # XXX not portable to Windows
    os.symlink(os.path.join("..", "..", "syntax", "relaxng"), 
               os.path.join(buildRoot, "validator", "schema", "html5"))
  f = open(os.path.join(buildRoot, "validator", "entity-map.txt"))
  try:
    for line in f:
      url, path = line.strip().split("\t")
      if not (path.startswith("syntax/") or path.startswith("schema/")):
        # XXX may not work on Windows
        if not os.path.exists(os.path.join(buildRoot, "local-entities", path)):
          fetchUrlTo(url, os.path.join(buildRoot, "local-entities", path))
  finally:
    f.close()

def downloadOperaSuite():
  return
  operaSuiteDir = os.path.join(buildRoot, "opera-tests")
  validDir = os.path.join(operaSuiteDir, "valid")
  invalidDir = os.path.join(operaSuiteDir, "invalid")
  if not os.path.exists(operaSuiteDir):
    os.makedirs(operaSuiteDir)
    os.makedirs(validDir)
    os.makedirs(invalidDir)
    spiderApacheDirectories("http://tc.labs.opera.com/html/", validDir)

def zipExtract(zipArch, targetDir):
  z = zipfile.ZipFile(zipArch)
  for name in z.namelist():
    file = os.path.join(targetDir, name)
    # is this portable to Windows?
    if not name.endswith('/'):
      head, tail = os.path.split(file)
      ensureDirExists(head)
      o = open(file, 'wb')
      o.write(z.read(name))
      o.flush()
      o.close()

def downloadDependency(url, md5sum):
  dependencyDir = os.path.join(buildRoot, "dependencies")
  ensureDirExists(dependencyDir)
  path = os.path.join(dependencyDir, url[url.rfind("/") + 1:])
  if not os.path.exists(path):
    fetchUrlTo(url, path, md5sum)
    if path.endswith(".zip"):
      zipExtract(path, dependencyDir)

def downloadDependencies():
  for url, md5sum in dependencyPackages:
    downloadDependency(url, md5sum)

def buildAll():
  buildSaxon()
  buildOnvdl()
  buildUtil()
  buildDatatypeLibrary()
  buildNonSchema()
  buildHtmlParser()
  buildXmlParser()
  buildTestHarness()
  buildValidator()

def checkout():
  # XXX root dir
  for mod in moduleNames:
    runCmd("'%s' co '%s' '%s'" % (svnCmd, svnRoot + mod + '/trunk/', mod))

def runTests():
  classPath = os.pathsep.join(dependencyJarPaths() 
                              + jarNamesToPaths(["non-schema", 
                                                "io-xml-util",
                                                "htmlparser",
                                                "hs-aelfred2",
                                                "html5-datatypes",
                                                "test-harness",
                                                "onvdl-whattf",
                                                "saxon-whattf"]))
  runCmd("'%s' -cp %s org.whattf.syntax.Driver" % (javaCmd, classPath))

def splitHostSpec(spec):
  index = spec.find('/')
  return (spec[0:index], spec[index:])

def printHelp():
  print "Usage: python build/build.py [options] [tasks]"
  print ""
  print "Options:"
  print "  --svn=/usr/bin/svn         -- Sets the path to the svn binary"
  print "  --java=/usr/bin/java       -- Sets the path to the java binary"
  print "  --jar=/usr/bin/jar         -- Sets the path to the jar binary"
  print "  --javac=/usr/bin/javac     -- Sets the path to the javac binary"
  print "  --javadoc=/usr/bin/javadoc -- Sets the path to the javadoc binary"
  print "  --jdk-bin=/j2se/bin        -- Sets the paths for all JDK tools"
  print "  --log4j=log4j.properties   -- Sets the path to log4 configuration"
  print "  --port=8888                -- Sets the server port number"
  print "  --ajp=on                   -- Use AJP13 instead of HTTP"
  print "  --promiscuous-ssl=on       -- Don't check SSL/TLS certificate trust chain"
  print "  --heap=64                  -- Sets the heap size in MB"
  print "  --name=Validator.nu        -- Sets the service name"
  print "  --html5link=http://www.whatwg.org/specs/web-apps/current-work/"
  print "                                Sets the link URL of the HTML5 spec"
  print "  --html5load=http://www.whatwg.org/specs/web-apps/current-work/"
  print "                                Sets the load URL of the HTML5 spec"
  print "                                By default the same as --html5link="
  print "  --iana-lang=http://www.iana.org/assignments/language-subtag-registry"
  print "                                Sets the URL for language tag registry"
  print "  --about=http://about.validator.nu/"
  print "                                Sets the URL for the about page"
  print "  --stylesheet=http://about.validator.nu/style.css"
  print "                                Sets the URL for the style sheet"
  print "                                Defaults to --about= plus style.css"
  print "  --script=http://about.validator.nu/script.js"
  print "                                Sets the URL for the style sheet"
  print "                                Defaults to --about= plus script.js"
  print "  --microsyntax=http://wiki.whatwg.org/wiki/MicrosyntaxDescriptions"
  print "                                Sets the URL for microformat"
  print "                                descriptions"
  print ""
  print "Tasks:"
  print "  checkout -- Checks out the source from SVN"
  print "  dldeps   -- Downloads missing dependency libraries and entities"
  print "  dltests  -- Downloads the external test suite if missing"
  print "  build    -- Build the source"
  print "  test     -- Run tests"
  print "  run      -- Run the system"
  print "  all      -- checkout dldeps dltests build test run"

argv = sys.argv[1:]
if len(argv) == 0:
  printHelp()
else:
  for arg in argv:
    if arg.startswith("--svn="):
      svnCmd = arg[6:]
    elif arg.startswith("--java="):
      javaCmd = arg[7:]
    elif arg.startswith("--jar="):
      jarCmd = arg[6:]
    elif arg.startswith("--javac="):
      javacCmd = arg[8:]
    elif arg.startswith("--javadoc="):
      javadocCmd = arg[10:]
    elif arg.startswith("--jdk-bin="):
      jdkBinDir = arg[10:]
      javaCmd = os.path.join(jdkBinDir, "java")
      jarCmd = os.path.join(jdkBinDir, "jar")
      javacCmd = os.path.join(jdkBinDir, "javac")
      javadocCmd = os.path.join(jdkBinDir, "javadoc")
    elif arg.startswith("--svnRoot="):
      svnRoot = arg[10:]
    elif arg.startswith("--port="):
      portNumber = arg[7:]
    elif arg.startswith("--log4j="):
      log4jProps = arg[8:]
    elif arg.startswith("--heap="):
      heapSize = arg[7:]
    elif arg.startswith("--html5link="):
      html5specLink = arg[12:]
    elif arg.startswith("--html5load="):
      html5specLoad = arg[12:]
    elif arg.startswith("--iana-lang="):
      ianaLang = arg[12:]
    elif arg.startswith("--about="):
      aboutPage = arg[8:]
    elif arg.startswith("--microsyntax="):
      microsyntax = arg[13:]
    elif arg.startswith("--stylesheet="):
      stylesheet = arg[14:]
    elif arg.startswith("--script="):
      script = arg[9:]
    elif arg.startswith("--name="):
      script = arg[7:]
    elif arg.startswith("--genericpath="):
      (genericHost, genericPath) = splitHostSpec(arg[14:])
    elif arg.startswith("--html5path="):
      (html5Host, html5Path) = splitHostSpec(arg[12:])
    elif arg.startswith("--parsetreepath="):
      (parsetreeHost, parsetreePath) = splitHostSpec(arg[16:])
    elif arg == '--ajp=on':
      useAjp = 1
    elif arg == '--ajp=off':
      useAjp = 0
    elif arg == '--promiscuous-ssl=on':
      usePromiscuousSsl = 1
    elif arg == '--promiscuous-ssl=off':
      usePromiscuousSsl = 0
    elif arg == '--help':
      printHelp()
    elif arg == 'dldeps':
      downloadDependencies()
      downloadLocalEntities()
    elif arg == 'dltests':
      downloadOperaSuite()
    elif arg == 'checkout':
      checkout()
    elif arg == 'build':
      buildAll()
    elif arg == 'test':
      runTests()
    elif arg == 'run':
      if not html5specLoad:
        html5specLoad = html5specLink
      if not stylesheet:
        stylesheet = aboutPage + 'style.css'
      if not script:
        script = aboutPage + 'script.js'
      runValidator()
    elif arg == 'all':
      checkout()
      downloadDependencies()
      downloadLocalEntities()
      downloadOperaSuite()
      buildAll()
      runTests()
      if not html5specLoad:
        html5specLoad = html5specLink
      if not stylesheet:
        stylesheet = aboutPage + 'style.css'
      if not script:
        script = aboutPage + 'script.js'
      runValidator()
    else:
      print "Unknown option %s." % arg

