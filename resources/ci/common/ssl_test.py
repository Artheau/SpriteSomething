import importlib.metadata
import os
import re
import subprocess
import sys
import warnings

import certifi
import http.client
import requests
import ssl
from urllib.request import urlopen
from urllib3.connectionpool import InsecureRequestWarning

def get_module_version(mod):
  try:
    return importlib.metadata.version(mod)
  except importlib.metadata.PackageNotFoundError as e:
    # print(e)
    pass
  except Exception as e:
    import pkg_resources
    return pkg_resources.get_distribution(mod).version

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

URLS = {
  "z3r": {
    "301":    { "expected": "200", "url": "https://alttpr.com/sprites" },
    "403":    { "expected": "403", "url": "https://alttpr-assets.s3.us-east-2.amazonaws.com/001.link.1.zspr" },
    "301.2":  { "expected": "200", "url": "https://alttpr-assets.s3.us-east-2.amazonaws.com/4slink-armors.1.zspr" },
    "497":    { "expected": "200", "url": "http://alttpr.com/sprites" }
  },
  "mm1": {
    "200": { "expected": "200", "url": "http://smalttpr.mymm1.com/sprites" },
    "404": { "expected": "404", "url": "http://mike.mymm1.com/moo" },
    "505": { "expected": "200", "url": "https://smalttpr.mymm1.com/sprites" }
  }
}

heading = (
  "%s-%s-%s"
  %
  (
    os.path.splitext(sys.executable.split(os.path.sep).pop())[0],
    sys.version.split(" ")[0],
    sys.platform
  )
)

rpad = len("websockets | 2020.01.01")
lpad = int(rpad / 2) + 2

print('/' + ('=' * rpad) + '\\')
print('|' + heading.center(rpad) + '|')
print('|' + ('=' * rpad) + '|')

freeze = subprocess.check_output(
  [
    sys.executable,
    "-m",
    "pip",
    "freeze"
  ]
).decode("utf-8")
freeze = freeze.split("\n")
i = 0
for mod in freeze:
  freeze[i] = mod.strip()
  if freeze[i] == "":
    del freeze[i]
  i += 1
results = []
curd = {}
for mod in freeze:
  k,v = mod.split("==", 1)
  if k in curd:
    results.append(curd)
    curd = {}
  curd[k] = v
results.append(curd)
freeze = results[0]

freeze = {k:v for (k,v) in freeze.items() if k in [
  "certifi",
  "requests",
  "ssl",
  "urllib",
  "urllib.request",
  "urllib3",
  "urllib3.request",
  "websockets"
]}

for (name, mod) in sys.modules.copy().items():
  if get_module_version(mod.__name__):
    freeze[mod.__name__] = get_module_version(mod.__name__)

for (mod, version) in sorted(freeze.items()):
  print(f"|{mod.ljust(len('websockets'), ' ')} | {version.ljust(len('2020.01.01'))}|")

print('\\' + ('=' * len("websockets | 2020.01.01")) + '/')

print("")

# Unverified Context
unverified = ssl._create_unverified_context()

# Default Context
default = ssl.create_default_context()

for c in default.get_ca_certs():
  for u in c["subject"]:
    if "ISRG" in u[0][1]:
      print("Found LetsEncrypt ISRG root!")

print("OpenSSL version: ", ssl.OPENSSL_VERSION)

print("")

noheader = [
  "Accept-Ranges",
  "Cache-Control",
  "Connection",
  "ETag",
  "Keep-Alive",
  "Last-Modified",
  "Server",
  "Set-Cookie",
  "Transfer-Encoding",
  "x-amz-request-id",
  "x-amz-id-2"
]

line = ""
line = '/' + ('=' * 65) + '='
print(line)

line = ""
line += (
  '|' + "Module".ljust(25, ' ') +
  '|' + "SSL Context" +
  '|' + "HTTP Expected" +
  '|' + "HTTP Resolved" +
  '|'
)
print(line)

line = ""
line += '|' + ('=' * 65) + '=' + "\n"
line += '|' + "urllib.request.urlopen()".ljust(25, ' ')

i = 0
for (ctxLabel, context) in {
    "None": None,
    "Unverified": unverified,
    "Default": default,
    "Certifi": default
  }.items():

  if i > 0:
    line += (
      '|' + ('-' * 65) + '-'
    ) + "\n"
    line += (
      '|' + (25 * ' ')
    )
  i += 1
  line += '|' + ctxLabel.ljust(len("SSL Context"), ' ')

  j = 0
  for (site, accessCodes) in URLS.items():
    for (shortCode, siteData) in accessCodes.items():
      expectedCode = siteData["expected"]
      url = siteData["url"]

      if j > 0:
        line += (
          '|' + (25 * ' ') +
          '|' + (len("SSL Context") * ' ')
        )
      j += 1

      rpad = len("HTTP Expected")
      lpad = int(rpad / 2) + 2
      try:
        if ctxLabel == "Certifi":
          context = ssl.create_default_context(cafile=certifi.where())
        if context:
          req = urlopen(url, context=context)
        else:
          req = urlopen(url)
        headers = req.headers.items()
        headers = dict(headers)
        for toPop in noheader:
          if toPop in headers.keys():
            headers.pop(toPop)
        line += ("|%s|%s" % (
          expectedCode.center(rpad),
          str(req.getcode()).center(rpad)
        ))
      except Exception as e:
        matches = re.match(r"(?:[^\d]*)([\d]{3})(?:.*)", e.__str__())
        if matches:
          line += ("|%s|%s" % (
            expectedCode.center(rpad),
            matches.groups()[0].center(rpad)
          ))
        else:
          line += ("|%s|%s" % (
            "???".center(rpad),
            "???".center(rpad)
          ))
      line += '|' + url
      print(line)

      line = ""


line = ""
line += '|' + ('=' * 65) + '=' + "\n"
line += '|' + "requests.get()".ljust(25, ' ')

i = 0
for (ctxLabel, context) in {
    "None": None,
    "False": False,
    "Certifi": certifi.where()
  }.items():

  if i > 0:
    line += (
      '|' + ('-' * 65) + '-'
    ) + "\n"
    line += (
      '|' + (25 * ' ')
    )
  i += 1
  line += '|' + ctxLabel.ljust(len("SSL Context"), ' ')

  j = 0
  for (site, accessCodes) in URLS.items():
    for (shortCode, siteData) in accessCodes.items():
      expectedCode = siteData["expected"]
      url = siteData["url"]

      if j > 0:
        line += (
          '|' + (25 * ' ') +
          '|' + (len("SSL Context") * ' ')
        )
      j += 1

      try:
        if context is not None:
          req = requests.get(url, verify=context)
        else:
          req = requests.get(url)
        headers = req.headers.items()
        headers = dict(headers)
        for toPop in noheader:
          if toPop in headers.keys():
            headers.pop(toPop)
        line += ("|%s|%s|%s" % (
          expectedCode.center(rpad),
          str(req.status_code).center(rpad),
          url
        ))
      except Exception as e:
        matches = re.match(r"(?:[^\d]*)([\d]{3})(?:.*)", e.__str__())
        if matches:
          line += ("|%s|%s" % (
            expectedCode.center(rpad),
            matches.groups()[0].center(rpad)
          ))
        else:
          line += ("|%s|%s" % (
            "???".center(rpad),
            "???".center(rpad)
          ))
          line += '|' + url
      print(line)
      line = ""
print('\\' + (65 * '=') + '=')

# conn = http.client.HTTPSConnection("smalttpr.mymm1.com")
# conn.request("GET", "/sprites/")
# resp = conn.getresponse()
# print(resp.getheaders())
# print(resp.status)
# print(resp.reason)
# content = resp.read()
# conn.close()
# text = content.decode("utf-8")
