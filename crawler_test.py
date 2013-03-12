import unittest
from bs4 import BeautifulSoup
import urllib
import urlparse
import praw
from drone import Crawler

class TestCrawler(unittest.TestCase):

  def setUp(self):
    self.base = 'www.microsoft.com'
    self.crawler = Crawler(self.base) #everytime you run this test you waste some of microsoft's resources =)
  
  def test_convert_base(self):
    self.assertIsInstance(self.crawler.base,urlparse.ParseResult,"must return url objects")

  def test_clean(self):
    if len(self.crawler.pending) > 0:
      self.crawler.clean()
      assertTrue(len(self.crawler.pending) == 0, "clean must delete pending emails")

  def test_get_links_from_url(self):
    links = self.crawler.get_links_from_url(self.crawler.base)

  def test_get_links_from_new_url_only(self):
    self.crawler.get_links_from_url(self.crawler.base)
    self.assertFalse(self.crawler.get_links_from_url(self.crawler.base), "only crawl unvisited urls")

  def test_crunch_links(self):
    html = urllib.urlopen('http://www.google.com').read()
    raw_links = BeautifulSoup(html).find_all('a')
    self.assertIsInstance(self.crawler.crunch_links(raw_links),dict, "must return a dictionary")
    links = self.crawler.crunch_links(raw_links)
    self.assertTrue( links.has_key('emails'),'must have email key')
    self.assertTrue( links.has_key('pending'),'must have email key')
    for link in links.get('pending'):
      self.assertIsInstance(link,urlparse.ParseResult,"must return url objects")

  def test_eat_urls(self):
    self.crawler.clean()
    old_total_urls = len(self.crawler.pending)
    self.crawler.eat_urls([urlparse.urlparse('http://www.somenewlinkyouhaventseenbeforeforsure.com')])
    self.assertTrue(len(self.crawler.pending) > old_total_urls, "new links must be eaten")

  def test_only_eat_new_urls(self):
    self.crawler.clean()
    old_total_urls = len(self.crawler.pending)
    self.crawler.get_links_from_url(urlparse.urlparse('http://www.sameold.com'))
    self.crawler.eat_urls([urlparse.urlparse('www.sameold.com')])
    self.assertTrue(len(self.crawler.pending) == old_total_urls, "only new links must be eaten")

  def test_detect_sqli(self):
    self.assertTrue(self.crawler.detect_sqli(urlparse.urlparse("http://somesite.com/posts.php?id=1337")))
    self.assertFalse(self.crawler.detect_sqli(urlparse.urlparse("http://somesite.com")))

if __name__ == '__main__':
      unittest.main()
