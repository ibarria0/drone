import unittest
from bs4 import BeautifulSoup
import urllib
import urlparse
import Queue
from Worker import WorkThread

class TestWorker(unittest.TestCase):

  def setUp(self):
    self.base = urlparse.urlparse('localhost')
    self.url_queue = Queue.Queue()
    self.html_queue = Queue.Queue()
    self.sqli_queue = Queue.Queue()
    self.visited_queue = Queue.Queue()
    self.worker = WorkThread(self.html_queue, self.url_queue,self.base, self.sqli_queue)
    self.html = "<p>This is not a link</p><a href='vacaloca'>Moo</a><a href='/vacaloca?fail=1'>Moo</a><div id='href'>www.thisisalinknotinalink.com</div><a href='/vacaloca?fail=1&cat=2'>Moo</a><a href='/vacaloca?fail=1'>Moo</a><a href='http://localhost/vacaloca'>Moo</a><a href='/vacaloca'>Moo</a><h2>And also not this</h2><span>seriously, move on</span><a href='javascript:sillyjs()'>Click Me</a><a href='#datdiv'>DatDiv</a>"

  def test_extract_links(self):
    links = self.worker.extract_links(self.html)
    self.assertTrue(len(links) == 8,"must extract all <a> and skip non <a> ") #extract only and all links
    self.assertTrue(links[0] == 'vacaloca', "must return href string") #return only href part

  def test_crunch_links(self):
    self.assertTrue(len(self.worker.crunch_links(["mailto:moo@moo.com"])) == 0, "must skip email links" )
    self.assertTrue(len(self.worker.crunch_links(["javascript:moo()"])) == 0, "must skip javascript links" )
    self.assertTrue(len(self.worker.crunch_links(["#moo_div"])) == 0, "must skip id links" )
    self.assertTrue(len(self.worker.crunch_links(["http://remote.com"])) == 0, "must skip remote links" ) 
    self.assertTrue(len(self.worker.crunch_links(["http://localhost/happy.php?fail=1"])) == 1, "must not skip local links" ) 

  def test_is_a_new_url(self):
    url = urlparse.urlparse("http://www.bacon.com/")
    self.worker.seen = [url]
    self.assertFalse(self.worker.is_a_new_url(url), "must return False for already seen urls")
    self.assertTrue(self.worker.is_a_new_url(urlparse.urlparse("http://www.pancakes.com")), "must return True for new urls")

  def test_match_url(self):
    url_1 = urlparse.urlparse("http://www.bacon.com/")
    url_2 = urlparse.urlparse("http://www.pancakes.com/")
    self.assertFalse(self.worker.match_url(url_1,url_2), "must return False for different urls")
    self.assertTrue(self.worker.match_url(url_1, url_1), "must return True for matching urls")

  def test_match_params(self):
    url_1 = urlparse.urlparse("http://www.bacon.com/?id=1")
    url_2 = urlparse.urlparse("http://www.bacon.com/?id=1&moo=2")
    self.assertTrue(self.worker.match_params(url_1, url_1), "must return True for matching params")
    self.assertFalse(self.worker.match_params(url_1, url_2), "must return False for non matching params")

  def test_match_base(self):
    self.worker.base = urlparse.urlparse("localhost")
    url_1 = urlparse.urlparse("http://localhost/?id=1")
    url_2 = urlparse.urlparse("http://www.bacon.com/?id=1&moo=2")
    self.assertTrue(self.worker.match_base(url_1), "must return True for urls of same base")
    self.assertFalse(self.worker.match_base(url_2), "must return False for urls of different base") 

  def test_detect_sqli(self):
    self.assertTrue(self.worker.detect_sqli(urlparse.urlparse("http://somesite.com/posts.php?id=1337")), "must detect simple parameter injection")
    self.assertFalse(self.worker.detect_sqli(urlparse.urlparse("http://somesite.com")), "must not show false positives")

  def test_detect_juicy_files(self):
    self.assertTrue(self.worker.detect_juicy_files(urlparse.urlparse("http://somesite.com/passwords.pdf")), "must detect pdf files")
    self.assertTrue(self.worker.detect_juicy_files(urlparse.urlparse("http://somesite.com/passwords.xls")), "must detect xls files")
    self.assertTrue(self.worker.detect_juicy_files(urlparse.urlparse("http://somesite.com/passwords.doc")), "must detect doc files")
    self.assertTrue(self.worker.detect_juicy_files(urlparse.urlparse("http://somesite.com/passwords.txt")), "must detect txt files")
    self.assertFalse(self.worker.detect_sqli(urlparse.urlparse("http://somesite.com")), "must not show false positives")

  def test_eat_urls(self):
    self.worker.seen = [] # clear seen urls
    crunched_links = self.worker.crunch_links(self.worker.extract_links("<a href='/onelink'>one love</a>"))
    self.worker.eat_urls(crunched_links)
    self.assertTrue(self.url_queue.qsize() == 1 , "must add new links to url_queue")

  def test_work(self):
    self.worker.seen = [] # clear seen urls
    self.worker.work(self.html)
    self.assertTrue(self.url_queue.qsize() > 0 , "must add new links to url_queue")


if __name__ == '__main__':
      unittest.main()
