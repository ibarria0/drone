import re

class Form:
  def __init__(self,html):
    self.html = html
    self.inputs = []
    self.process()
  
  def process(self):
    self.action = re.findall(r'action=[\'"]?([^\'"]+)',self.html)

  def __str__(self):
    return str(self.html)
    
