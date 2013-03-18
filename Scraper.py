import threading
import urllib

class ScrapeThread(threading.Thread):
  def __init__(self, queue, out_queue, bucket, proxy, proxy_port):
    threading.Thread.__init__(self)
    self.proxy = proxy
    self.proxy_port = proxy_port
    self.queue = queue
    self.bucket = bucket
    self.out_queue = out_queue

  def run(self):
    while True:
      url = self.queue.get()
      self.read_url(url)
      self.queue.task_done()
      if self.queue.empty():
        return True

  def read_url(self,url):
    if self.proxy:
      proxy['http'] = 'http://' + str(self.proxy) + ":" + str(self.proxy_port)
    else:
      proxy = {}
    html = urllib.urlopen(url.geturl(),proxies=proxy).read()
    self.out_queue.put(html)
    self.bucket.put(url)

