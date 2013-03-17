import unittest
from bs4 import BeautifulSoup
import urllib
import urlparse
import praw
from Crawler import Crawler

class TestCrawler(unittest.TestCase):

  def setUp(self):
    self.base = 'localhost'
    self.crawler = Crawler(self.base) #everytime you run this test you waste some of microsoft's resources =)
  
  def test_convert_base(self):
    self.assertIsInstance(self.crawler.base,urlparse.ParseResult,"must return url objects")

  def test_clean(self):
      self.crawler.peding = [1]
      self.crawler.clean()
      self.assertTrue(len(self.crawler.pending) == 0, "clean must delete pending emails")

  def test_get_links_from_url(self):
    links = self.crawler.get_links_from_url(self.crawler.base)

  def test_get_links_from_new_url_only(self):
    self.crawler.get_links_from_url(self.crawler.base)
    self.assertFalse(self.crawler.get_links_from_url(self.crawler.base), "only crawl unvisited urls")

  def test_crunch_links(self):
    raw_links = self.crawler.get_links_from_url(self.crawler.base) 
    self.assertIsInstance(self.crawler.crunch_links(raw_links),dict, "must return a dictionary")
    links = self.crawler.crunch_links(raw_links)
    self.assertTrue( links.has_key('emails'),'must have email key')
    self.assertTrue( links.has_key('pending'),'must have email key')
    for link in links.get('pending'):
      self.assertIsInstance(link,urlparse.ParseResult,"must return url objects")
  
  def test_crunch_links_skip_images(self):
    pending_urls = self.crawler.crunch_links(["image.jpg"]).get('pending')
    self.assertTrue(len(pending_urls) == 0, "must skip images")


  def test_eat_urls(self):
    self.crawler.clean()
    old_total_urls = len(self.crawler.pending)
    self.crawler.eat_urls([urlparse.urlparse('http://www.somenewlinkyouhaventseenbeforeforsure.com')])
    self.assertTrue(len(self.crawler.pending) > old_total_urls, "new links must be eaten")

  def test_only_eat_new_urls(self):
    self.crawler.clean()
    links = self.crawler.get_links_from_url(self.crawler.base)
    self.crawler.eat_urls(self.crawler.crunch_links(links).get('pending'))
    old_total_urls = len(self.crawler.pending)
    links = self.crawler.get_links_from_url(self.crawler.base)
    self.crawler.eat_urls(self.crawler.crunch_links(links).get('pending'))
    self.assertTrue(len(self.crawler.pending) == old_total_urls, "only new links must be eaten")

  def test_detect_sqli(self):
    self.assertTrue(self.crawler.detect_sqli(urlparse.urlparse("http://somesite.com/posts.php?id=1337")), "must detect simple parameter injection")
    self.assertFalse(self.crawler.detect_sqli(urlparse.urlparse("http://somesite.com")), "must not show false positives")

  def test_detect_juicy_files(self):
    self.assertTrue(self.crawler.detect_juicy_files(urlparse.urlparse("http://somesite.com/passwords.pdf")), "must detect pdf files")
    self.assertTrue(self.crawler.detect_juicy_files(urlparse.urlparse("http://somesite.com/passwords.xls")), "must detect xls files")
    self.assertTrue(self.crawler.detect_juicy_files(urlparse.urlparse("http://somesite.com/passwords.doc")), "must detect doc files")
    self.assertTrue(self.crawler.detect_juicy_files(urlparse.urlparse("http://somesite.com/passwords.txt")), "must detect txt files")
    self.assertFalse(self.crawler.detect_sqli(urlparse.urlparse("http://somesite.com")), "must not show false positives")

  def test_detect_form(self):
    self.assertTrue(self.crawler.detect_form("<form action='bacon'>"))

if __name__ == '__main__':
      unittest.main()
