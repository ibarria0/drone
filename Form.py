from bs4 import BeautifulSoup

class Form:
  def __init__(self,html):
    self.html = html
    self.inputs = []
    self.action = ""
    self.process()

  def process(self):
    self.inputs.extend(self.html.findAll('input'))
    self.action = self.html.get('action')

  def __str__(self):
    return str(self.action) + " [" + str(len(self.inputs)) + " inputs]"

  def __eq__(self, other):
    return (set(self.inputs) == set(other.inputs)) and (self.action == other.action)

  def __ne__(self, other):
    return (set(self.inputs) != set(other.inputs)) or (self.action != other.action)

