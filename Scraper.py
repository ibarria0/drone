import threading
import Queue
from time import sleep
import urllib

class ScrapeThread(threading.Thread):
  def __init__(self, queue, out_queue, bucket, proxy, proxy_port, worker):
    threading.Thread.__init__(self)
    self.proxy = proxy
    self.proxy_port = proxy_port
    self.queue = queue
    self.bucket = bucket
    self.out_queue = out_queue
    self.worker = worker

  def run(self):
    while True:
      if self.queue.empty():
        if self.worker.isAlive():
          continue
        else:
          return True
      else:
        try:
          url = self.queue.get_nowait()
        except Queue.Empty:
          sleep(0.2)
          continue
        self.read_url(url)
        self.queue.task_done()

  def read_url(self,url):
    if self.proxy:
      proxy['http'] = 'http://' + str(self.proxy) + ":" + str(self.proxy_port)
    else:
      proxy = {}
    html = urllib.urlopen(url.geturl(),proxies=proxy).read()
    self.out_queue.put(html)
    self.bucket.put(url)

