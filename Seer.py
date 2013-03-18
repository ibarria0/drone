import threading
from Form import Form
import re
import urllib
import urlparse

class SeerThread(threading.Thread):
  def __init__(self, queue, out_queue):
    threading.Thread.__init__(self)
    self.queue = queue  #detect_queue
    self.out_queue = out_queue #sqli_queue

  def run(self):
    while True:
      link = self.queue.get()
      self.out_queue.put(raw_links)

      #signals to queue job is done
      self.queue.task_done()

