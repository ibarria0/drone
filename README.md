Drone
==========================
A very basic attack vector scanner for web based applications.

It will not do any injection, only scraping and parsing.



Dependencies
-------------------------------
* BeautifulSoup 4 (bs4)


Features
----------------------------
* use robots.txt
* HTTP proxy support
* skips urls with same base and params (see tests)
* skips image files
* collects forms (skips forms with same action AND same inputs)
* threaded
* does not perform any injection


Detection (possible injection)
--------------------------
* urls with parameters
* forms


To Do
----------------------------
* more detection
* dorking


Usage
-----------------------------
    python drone.py [-h] [--proxy PROXY] [--proxy_port PROXY_PORT] [--robots] base_url


