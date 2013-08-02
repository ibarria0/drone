#!/usr/bin/python
import argparse

from Crawler import Crawler

def validate_args(args):
  return args

def parse_args():
  parser = argparse.ArgumentParser(description='Scans a website for vulnerabilities')
  parser.add_argument('base', metavar='base', type=str,help='base URL to start from')
  parser.add_argument('--proxy', dest='proxy', type=str, default=False)
  parser.add_argument('--proxy_port', dest='proxy_port', type=int, default=False)
  parser.add_argument('--robots', dest='robots', action='store_const',const="True", default=False, help="Use robots.txt (Default=False)")
  return validate_args(parser.parse_args())

args = parse_args()
c = Crawler(args.base,args.proxy,args.proxy_port,args.robots)
c.start()
