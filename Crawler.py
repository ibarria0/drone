import urllib
from google import search
import urlparse
import re
import operator
from time import sleep
from Form import Form
import sys

class Crawler:
  def __init__(self,base,proxy=False,proxy_port=False,robots=False):
    self.visited = []
    self.pending = [] 
    self.emails = []
    self.sqli = []
    self.forms = []
    self.juicy = []
    self.base = base
    self.convert_base()
    self.robots = robots
    self.proxy = proxy
    self.proxy_port = proxy_port
    

  def check_proxy(self):
    proxy = {}
    proxy['http'] = 'http://' + str(self.proxy) + ":" + str(self.proxy_port)
    html = urllib.urlopen('http://icanhazip.com',proxies=proxy).read()
    html_no_proxy = urllib.urlopen('http://icanhazip.com').read()
    print "####Checking Proxy####"
    print "Using IP: " + html.strip()
    print "Original IP: " + html_no_proxy
    sleep(3)


  def detect_sqli(self,url):
    if(re.search('.*\?.*=.*',url.geturl())):
      self.sqli.append(url)
      return True
    else:
      return False

  def detect_form(self,html):
    forms = re.findall('\<form.*',html)
    if len(forms) > 0:
      for i in forms:
        self.forms.append(Form(i))
      return True
    else:
      return False

  def detect_juicy_files(self,url):
    if(re.search(".*\.(pdf|xls|doc|txt)",url.geturl())):
      self.juicy.append(url)
      return True
    else:
      return False

  def convert_base(self):
    if not self.base.startswith('http'):
      self.base = "http://" + self.base
    self.base = urlparse.urlparse(self.base)

  def get_links_from_url(self, url, proxy={}):
    if self.proxy:
      proxy['http'] = 'http://' + str(self.proxy) + ":" + str(self.proxy_port)
    if url not in self.visited:
      html = urllib.urlopen(url.geturl(),proxies=proxy).read()
      self.visited.append(url)
      self.detect_form(html)
      raw_links = re.findall(r'href=[\'"]?([^\'" >]+)', html)
      return raw_links
    else:
      return []

  def update_status(self):
    sys.stdout.write("\rUrls Visited: %d | latest: %s " % (len(self.visited) , self.visited[-1]))
    sys.stdout.flush()

  def crunch_links(self,links):
    r_image = re.compile(r".*(jpg|png|gif|JPG|PNG|GIF)$")
    emails = []
    pending = []
    for link in links: 
      if not link.startswith('java') and not link.startswith("#") and not (r_image.match(link)):
        if link.startswith('mailto'):
          emails.extend(link)
        elif not link.startswith('http'):
          if not link.startswith('/'):
            pending.append(urlparse.urlparse(self.base.geturl() + "/" + link))
          else:
            pending.append(urlparse.urlparse(self.base.geturl() + link))
    return {'emails': emails, 'pending': pending}


  def eat_urls(self,urls):
    for url in urls:
      if self.is_a_new_url(url):
        self.pending.append(url)
        self.detect_sqli(url)
        self.detect_juicy_files(url)

  def is_a_new_url(self,url):
    all_urls = self.pending + self.visited
    for visited_url in all_urls:
      if self.match_params(visited_url,url) and self.match_url(visited_url,url):
        return False 
    return True

  def match_params(self,url1,url2):
    return set(urlparse.parse_qs(url1.query).keys()) == set(urlparse.parse_qs(url2.query).keys())

  def match_url(self,url1,url2):
    return ((url1.netloc + url1.path) == (url2.netloc + url2.path))

  def crawl_url(self,url):
    new_raw_links = self.get_links_from_url(url)
    new_crunched_links = self.crunch_links(new_raw_links)
    self.eat_urls(new_crunched_links.get('pending'))

  def start(self):
    self.pending.append(self.base)
    if self.proxy:
      self.check_proxy()
    if self.robots:
      self.pending.append(urlparse.urlparse(self.base.geturl() + "/robots"))
    while (len(self.pending) > 0):
      new_url =self.pending.pop()
      self.crawl_url(new_url)
      self.update_status()
    sys.stdout.write('\r')
    sys.stdout.flush()


  def clean(self):
    self.visited = []
    self.pending = [] 
    self.emails = []

  def status(self):
    print "################"
    print "##Drone Status##"
    print "################"
    print "visited urls: " + str(len(self.visited))
    print "possible sqli found: " + str(len(self.sqli))
    print "files found: " + str(len(self.juicy))
    print
    if len(self.sqli) > 0:
      print "##Possible SQLi##"
      for i in self.sqli:
        print "sqli: " + i.geturl()
    print
    if len(self.juicy) > 0:
      print "##Possible Juicy Files##"
      for i in self.juicy:
        print "juicy: " + i.geturl()
    print
    if len(self.forms) > 0:
      print "##Forms Detected##"
      for i in self.forms:
        print "forms: " + str(i)
    



