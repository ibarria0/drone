from bs4 import BeautifulSoup 
import urllib
from google import search
import urlparse
import re
import operator

sqli = []
juicy = []

class Crawler:
  def __init__(self,base):
    self.visited = []
    self.pending = [] 
    self.emails = []
    self.sqli = []
    self.base = base
    self.convert_base()
    
  def detect_sqli(self,url):
    if(re.search('.*\?.*=.*',url.geturl())):
      self.sqli.append(url)
      return True
    else:
      return False

  def convert_base(self):
    if not self.base.startswith('http'):
      self.base = "http://" + self.base
    self.base = urlparse.urlparse(self.base)

  def get_links_from_url(self, url):
    if url not in self.visited:
      html = urllib.urlopen(url.geturl()).read()
      self.visited.append(url)
      raw_links = BeautifulSoup(html).find_all('a')
      return raw_links
    else:
      return []

  def crunch_links(self,links):
    emails = []
    pending = []
    for link in links: 
      if link.has_key('href'): 
        address = link.get('href')
        if not address.startswith('java'):
          if address.startswith('mailto'):
            emails.extend(address)
          elif not address.startswith('http'):
            pending.append(urlparse.urlparse(self.base.geturl() + address))
    return {'emails': emails, 'pending': pending}


  def eat_urls(self,urls):
    for url in urls:
      if self.is_a_new_url(url):
        self.pending.append(url)

  def is_a_new_url(self,url):
    all_urls = self.pending
    for visited_url in all_urls:
      if self.match_params(visited_url,url) and self.match_url(visited_url,url):
        return False 
    return True

  def match_params(self,url1,url2):
    return set(urlparse.parse_qs(url1.query).keys()) == set(urlparse.parse_qs(url2.query).keys())

  def match_url(self,url1,url2):
    return ((url1.netloc + url1.path) == (url2.netloc + url2.path))


  def find_local_links(self,links):
    for link in links:
      if link.has_key('href'): 
        address = link.get('href')
        if address.startswith("http") and address not in self.visited:
          self.pending.append(address)
        elif not address.startswith('javas'):
          if address.startswith('mailto'):
            self.emails.extend(address)
          elif address not in self.visited:
            self.pending.append(urlparse.urljoin("http://" + self.base, address))

  def start(self):
    self.pending.append(self.base)
    while (len(self.pending) > 0):
      new_url =self.pending.pop()
      new_raw_links = self.get_links_from_url(new_url)
      new_crunched_links = self.crunch_links(new_raw_links)
      self.eat_urls(new_crunched_links.get('pending'))
      print len(self.pending)
      print self.sqli

  def clean(self):
    self.visited = []
    self.pending = [] 
    self.emails = []

    

def is_url_new(url1):
  for url2 in sqli:
    if(match_params(url1,url2) and match_url(url1,url2)):
      return False
  return True



def juicy_files(url):
  if(re.search(".*\.(pdf|xls|doc|txt)",url)):
    juicy.append(urlparse.urlparse(url))


def do_checks(url):
  detect_sqli(url)
  juicy_files(url)

#for url in search("bacon", stop=50):

#  do_checks(url)

c = Crawler('http://www.trackpoint.com.pa')
c.start()


