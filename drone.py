import argparse

from Crawler import Crawler

def validate_args(args):
  return args

def parse_args():
  parser = argparse.ArgumentParser(description='Scans a website for vulnerabilities')
  parser.add_argument('base', metavar='base', type=str,help='base URL to start from')
  return validate_args(parser.parse_args())

args = parse_args()
c = Crawler(args.base)
c.start()
c.status()
