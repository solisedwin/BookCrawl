  # -*- coding: utf-8 -*-
import scrapy
import sys
sys.path.append('/var/www/html/ScrapyProjects/ScrapBooks/ScrapBooks')
#from query import extract
import requests
import json
from itertools import cycle
from lxml.html import fromstring
import traceback

#to fix/scrap last url in info method 
from scrapy.selector import Selector
from bs4 import BeautifulSoup

import MySQLdb


class AmazonSpider(scrapy.Spider):




  #set up, not methods. Important information for the spider
  name = 'az'
  allowed_domains = ["amazon.com"]

  custom_settings = {
  "DOWNLOAD_DELAY": 4,
  "CONCURRENT_REQUESTS_PER_DOMAIN": 2
  }


  
  #set up MySQL database 
  conn = MySQLdb.connect(host="127.0.0.1",user="root", passwd="fakepasswordforgit", db="BookCrawler");
  # you must create a Cursor object. It will let you execute all the queries you need  
  cur = conn.cursor();


  def getGenre(self):
    with open('/var/www/html/BookCrawl/client_data.json') as f: 
      data = json.load(f);
      genre = data["genre"].replace('"', '');
      return genre;


  def getLastName(self):
    with open('/var/www/html/BookCrawl/client_data.json') as f:
      data = json.load(f);
      lastName = data["lastName"].replace('"', '');
      return lastName.strip();


  def getFirstName(self):
    with open('/var/www/html/BookCrawl/client_data.json') as f:
      data = json.load(f);
      firstName = data["firstName"].replace('"','');
      return firstName.strip();


  def getPages(self):
    with open('/var/www/html/BookCrawl/client_data.json') as f:
        data = json.load(f);
        pages = data['pages'].strip();
        return pages;


  def getYears(self):
    with open('/var/www/html/BookCrawl/client_data.json') as f:
      data = json.load(f);
      startYear = data['startYr'].strip();
      endYear = data['endYr'].strip();
      return [startYr, endYr];


  def getPublisher(self):
    with open('/var/www/html/BookCrawl/client_data.json') as f:
        data = json.load(f);
        publisher = data['publisher'].strip();
        return publisher;    





  def sql_booklist(self,genre, name_query):

    print 'Inside sql_booklist method';

    query = "SELECT * FROM %s WHERE BOOK IS NOT NULL " % (genre);
    query = query + name_query;
    

    self.cur.execute(query);
    data = self.cur.fetchall();

    data = list(data);
    books = [];
    print 'Length of data: ' + str(len(data));


    try:
      for i in range(len(data)):
        #returns only book title for row index i. Column 6
        title = str(data[i][6]).strip();
        title = title.replace(' ','-');
        books.append(title);
          
      return books;
    except Exception as e:
      print ('~~ sql_booklist Exception: ' + str(e));






  def sqlInsert(self,firstName, lastName, year, page, parse_publisher, book):
    genre = self.getGenre();
    book = book.replace("'",'');
    book  = book.replace('"','');

    try:
      if (firstName):
        self.cur.execute("UPDATE %s SET FirstName = '%s' WHERE BOOK = '%s'" % (genre, firstName, book));
        print 'First Name successfully updated for ' + book;

      if (lastName):
        self.cur.execute("UPDATE %s SET LastName = '%s' WHERE BOOK = '%s'" % (genre, lastName, book));
        print 'Last Name successfully updated for ' + book;

      #check that each value isnt null      
      if (year):
        year = int(year);
        self.cur.execute("UPDATE %s SET StartYear = %d WHERE BOOK = '%s'" % (genre, year, book));
        print 'Year successfully updated for ' + book;

      if (page):
        page = int(page);
        self.cur.execute("UPDATE %s SET Pages = %d WHERE BOOK = '%s'" % (genre, page, book)); 
        print 'Page successfully updated for ' + book;
      
      if (parse_publisher):
        self.cur.execute("UPDATE %s SET Publisher = '%s' WHERE BOOK = '%s'" % (genre, parse_publisher, book)); 
        print 'Publisher successfully updated for ' + book;

      self.conn.commit();
    except Exception as e:
      print ('~~ SQL Insert Exception: ' + str(e));






  # *** First method that excecutes, OVERRIDES the start_urls ***

  def start_requests(self):
    print "@@@@@@@@@@@@@@@@@@@@@ In start_requests method  @@@@@@@@@@@@@@@@@@@@@@@@@"

    genre = self.getGenre();
  
    client_lastName = self.getLastName();
    client_firstName = self.getFirstName();

    
    if client_firstName:
      query = " AND FirstName = '%s'" % (client_firstName);
    else:
      query =  " AND FirstName IS NOT NULL";



    if client_lastName:
      query =  " AND LastName = '%s'" % (client_lastName); 
    else:
      query =  " AND LastName IS NOT NULL";



    if client_firstName and client_lastName:
      query = " AND FirstName = '%s' AND LastName = '%s' " % (client_firstName, client_lastName); 

    # both authors names were left blank
    #if not client_firstName and not client_lastName:
      #check unempty pages and years

      



  

    #all books that mathch if author names are empty or not. Minmize our searches
    books = self.sql_booklist(genre, query);
  
    amazon_url = 'https://www.amazon.com/s/ref=nb_sb_ss_c_1_4?url=search-alias%3Daps&field-keywords=';
  
    for b in books:
      print b + '\n';
      #full url including book we need for info on.
      url = amazon_url + b;
      request = scrapy.Request(url, callback = self.parse ,  meta={'book': b})
      yield request 
    






  def parse(self, response):
    print ' &&&& Inside parse method &&&&';
    book = response.meta.get('book');

    for base_url in (response.xpath("/html/body/div[1]/div[2]/div/div[3]/div[2]/div/div[4]/div[1]/div/ul/li[2]/div/div/div/div[2]/div[1]/div[1]/a/@href")):
      #stepping inside link
      new_url = response.urljoin(base_url.extract())     

      print "New Url: " + str(new_url)
      yield scrapy.Request(new_url, callback=self.parseInfo, meta={'book': book});






  def author_parse(self,response):
    #author name
    authorName = response.xpath('//a[@class="a-link-normal contributorNameID"]/text()').extract();
    authorName = str(authorName);
      
    print 'Author full info: ' + authorName;
 
    firstName = authorName[authorName.index('u') + 1 : authorName.index(' ')];
    lastName = authorName[authorName.index(' ') + 1: authorName.index(']') ];
   
    names = [firstName , lastName];
    return  names;   





  def year_parse(self,response):
    #Year book was made
    unparsed_year = response.xpath('//span[@class="a-size-medium a-color-secondary a-text-normal"]/text()').extract();
    unparsed_year = str(unparsed_year).strip(); 
    year = unparsed_year[-6:];
    year = year[0 : len(year) - 2];
    return year;



  def publisher_parse(self,response):

    #Get book publisher
    publisher = response.xpath('//*[@class="content"]/ul/descendant::li[2]/text()').extract();
    publisher = str(publisher).strip();
      

    if(';' in publisher):
      parse_publisher = publisher[4: publisher.index(';')];
      return parse_publisher;
    else:
      parse_publisher = publisher[0:publisher.index('(')];
      parse_publisher = parse_publisher[4:];
      return parse_publisher;





  def page_parse(self,response):
    #Number of pages
    info = response.xpath('//*[@class="content"]/ul/descendant::li[1]/text()[1]').extract();
    info =  str(info).strip();
    page =  info[info.index('pages') - 4 : info.index('pages')];
    page = page.strip();
    return page;






  def parseInfo(self, response):

    book = response.meta.get('book');
    book = book.replace('-',' ');
    
    firstName = "";
    lastName = "";
    year = "";
    page = "";
    publisher = "";


    client_not_match = False;


    client_firstName = self.getFirstName();
    client_lastName = self.getLastName();



    #We scrap first and last name, then check if they equal client info.Lastly check if any digits are inside the name strings
    try:
      names = self.author_parse(response);
      firstName = names[0];
      lastName = names[1];

      firstName = firstName.replace("'",'');
      firstName  = firstName.replace('"','');
      firstName = firstName.strip();

      lastName = lastName.replace("'",'');
      lastName  = lastName.replace('"','');
      lastName = lastName.strip();

      if client_lastName and client_lastName != lastName:
        client_not_match = True;
        raise ValueError('Scraped Last Name doesnt equal client last name perference'); 


      if client_firstName and client_firstName != firstName:
        client_not_match = True;
        raise ValueError('Scraped First Name doesnt equal client first name perference');



      #Check if string names contain any digits. 
      first_bool = any(char.isdigit() for char in firstName);
      last_bool =  any(char.isdigit() for char in lastName);



      if first_bool or last_bool:
        raise ValueError('Names contain numbers');


      print 'First Name: ' + firstName;
      print 'Last Name: ' + lastName;



    except Exception as e:
      print '~~ Names Exception: ' + str(e);
      firstName = '';
      lastName = '';





    if not client_not_match:

      try:
        year = self.year_parse(response);
        year_bool = any(char.isalpha() for char in year);

        if year_bool:
          raise ValueError('Year has alpha in it. Not fully int');

        print 'Year: ' + year;
      except Exception as e:
        print '~~ Year Exception: ' + str(e);
        year = '';



      try:
        page = self.page_parse(response);
        page_bool = any(page.isalpha() for char in page);

        if page_bool:
          raise ValueError('Page has alpha in it. Not fully int');

        print 'Number of Pages: ' + page;
      except Exception as e:
        print '~~ Page Exception: ' + str(e);
        page = '';



      try:
        publisher = self.publisher_parse(response);
        print 'Publisher: ' + publisher;
      except Exception as e:
        print '~~ Publisher Exception: ' + str(e);
        publisher = '';


        
      self.sqlInsert(firstName, lastName, year, page, publisher, book);

    #No point of scraping anymore. First/last name doesnt match with client's info
    else:
      pass;





"""

  custom_settings = {
      'HTTPPROXY_ENABLED': True
  }

  rotate_user_agent = True
  

    proxies = self.get_proxies()
    proxy_pool = cycle(proxies)   
    proxyNow = next(proxy_pool)
    

    proxies={"http": proxy, "https": proxy}
    request.meta['proxy'] = proxy

      


#yield scrapy.Request(url=u, callback=self.parse, meta={'proxy': proxy})


  
  """
  
