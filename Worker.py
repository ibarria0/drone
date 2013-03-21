import threading
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import re
import urllib
import urlparse
from time import sleep
from Form import Form

class WorkThread(threading.Thread):
  def __init__(self, queue, out_queue, base, sqli_queue, forms_queue):
    threading.Thread.__init__(self)
    self.queue = queue
    self.out_queue = out_queue
    self.sqli_queue = sqli_queue
    self.forms_queue = forms_queue 

    self.base = base

    self.seen = [] 
    self.sqli = []
    self.juicy = []

  def run(self):
    while True:
      if self.queue.empty():
        sleep(0.1)
        self.out_queue.join()
        if self.queue.empty():
          return True
      else:
        html = self.queue.get() #get raw html
        self.work(html) #do work
        self.queue.task_done()

  def work(self,html):
      urls = self.crunch_links(self.extract_links(html))
      self.eat_urls(urls)
      self.eat_forms(self.extract_forms(html))

  def extract_links(self,html):
  # raw_links = re.findall(r'href=[\'"]?([^\'" >]+)', html)
    raw_links = BeautifulSoup(html, 'html.parser' ,parse_only=SoupStrainer("a"))
    return [link.get('href') for link in raw_links]

  def extract_forms(self,html):
    raw_forms = BeautifulSoup(html, 'html.parser' ,parse_only=SoupStrainer("form"))
    return raw_forms

  def crunch_links(self,links):
    r_image = re.compile(r".*(jpg|png|gif|JPG|PNG|GIF)$")
    pending = []
    links = filter(None, links) # remove empty objects
    for link in links:
      if not (link.startswith('java') or link.startswith('mailto') or link.startswith("#") or (r_image.match(link))): #if its a url link
        if link.startswith("http"): 
          if self.match_base(urlparse.urlparse(link)): #from same domain
            pending.append(urlparse.urlparse(link))
            continue
          else:
            continue
        if not link.startswith('/'): #local link
          pending.append(urlparse.urlparse(self.base.geturl() + "/" + str(link)))
        else:
          pending.append(urlparse.urlparse(self.base.geturl() + str(link)))
    return pending

  def eat_urls(self,urls):
    if len(urls) > 0:
      for url in urls:
        if self.is_a_new_url(url):
          self.out_queue.put(url)
          self.detect_sqli(url)

  def eat_forms(self,forms):
    for form in forms:
      #do some processing
      form = Form(form)
      self.forms_queue.put(form)

  def is_a_new_url(self,url):
    for seen_url in self.seen:
      if self.match_params(seen_url,url) and self.match_url(seen_url,url):
        return False 
    self.seen.append(url)
    return True

  def match_params(self,url1,url2):
    return set(urlparse.parse_qs(url1.query).keys()) == set(urlparse.parse_qs(url2.query).keys())

  def match_url(self,url1,url2):
    return ((url1.netloc + url1.path) == (url2.netloc + url2.path))

  def match_base(self,url1):
    url2 = self.base
    return ((url1.netloc) == (url2.netloc + url2.path) or (url1.path) == (url2.netloc + url2.path))

  def detect_sqli(self,url):
    if(re.search('.*\?.*=.*',url.geturl())):
      self.sqli_queue.put(url)
      return True
    else:
      return False

  def detect_juicy_files(self,url):
    if(re.search(".*\.(pdf|xls|doc|txt)",url.geturl())):
      self.juicy.append(url)
      return True
    else:
      return False
