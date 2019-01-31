#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from ScrapBooks.items import ScrapbooksItem
from scrapy.http.request import Request
import json
import MySQLdb
import re
import requests
from bs4 import BeautifulSoup



class AlibrisspiderSpider(scrapy.Spider):



    
    #get genre
    with open('/var/www/html/BookCrawl/client_data.json') as f:
        data = json.load(f);
        genre = data["genre"].replace('"', '');





    #set up MySQL database 
    conn = MySQLdb.connect(host="127.0.0.1",user="root", passwd="fakepasswordforgithub", db="BookCrawler");
    # you must create a Cursor object. It will let you execute all the queries you need  
    cur = conn.cursor();



    def getLastName(self):
        with open('/var/www/html/BookCrawl/client_data.json') as f:
            data = json.load(f);
            lastName = data["lastName"].replace('"','');
            return lastName.strip();


    def getFirstName(self):
        with open('/var/www/html/BookCrawl/client_data.json') as f:
            data = json.load(f);
            firstName = data['firstName'].replace('"','');
            return firstName.strip();



    def getYears(self):
        with open('/var/www/html/BookCrawl/client_data.json') as f:
            data = json.load(f);
            startYear = data['startYr'].strip();
            endYear = data['endYr'].strip();
            return [startYear, endYear];





    def insertInfo(self,title,firstName,lastName):


        if firstName == 'NULL':
            firstName = None;
        if lastName == 'NULL':
            lastName = None;


        print "Filtered: " + title; 
        print 'Author First Name: ' + firstName;
        print 'Author Last Name: ' + lastName;
        print '\n';

        self.cur.execute("SELECT COUNT(1) FROM %s WHERE Book = '%s'" % (self.genre,self.conn.escape_string(title)));       

        count = self.cur.fetchone()[0];
        #get value from tuple
        print "$$$ Count: " + str(count) + " $$$"

        #check if book is already in the database
        if (count > 0):
            print '@@@ Book title is already in database. @@@';
        
        else:
            try:
                self.cur.execute("INSERT INTO %s(FirstName,LastName,Book) VALUES('%s', '%s', '%s');" % (self.genre, firstName, lastName, self.conn.escape_string(title)));
                print title + " is added to the database !!!";
                self.conn.commit();

            except Exception as e:
                print "~~ insertInfo Exception: " + str(e) + " ~~";
            




    def insertInfo_date (self,title,firstName,lastName, date):

        if firstName == 'NULL':
            firstName = None;
        if lastName == 'NULL':
            lastName = None;


        self.cur.execute("SELECT COUNT(1) FROM %s WHERE Book = '%s'" % (self.genre,self.conn.escape_string(title)));       

        count = self.cur.fetchone()[0];
        #get value from tuple
        print "$$$ Count: " + str(count) + " $$$"

        #check if book is already in the database
        if (count > 0):
            print '@@@ Book title is already in database. @@@';
        
        else:
            try:
                self.cur.execute("INSERT INTO %s(FirstName,LastName,Book, StartYear) VALUES('%s', '%s', '%s', %d);" % (self.genre, firstName, lastName, self.conn.escape_string(title) , date));
                print title + " is added to the database !!!";
                self.conn.commit();

            except Exception as e:
                print "~~ insertInfo_date Exception: " + str(e) + " ~~";
            



    name = 'as'
    
    allowed_domains = ['alibris.com','fictiondb.com', 'goodreads.com']

    custom_settings = {
    "DOWNLOAD_DELAY": 4,
    "CONCURRENT_REQUESTS_PER_DOMAIN": 2
    }



    #Websites to scrap for book genres

    #https://www.alibris.com/search/books/subject/Mystery?qsort=&page=1
    """
    start_urls = ['https://www.alibris.com/search/books/subject/' + genre + '?qsort=&page=' + str(pageCounter),
    'https://www.fictiondb.com/search/searchresults.htm?srchtxt=' + genre + '&styp=5',
    'https://www.goodreads.com/genres/' + genre];
    """



    def start_requests(self):
        start_urls = [];

        
        webpage_genre = '';

        if 'eFic' in self.genre:
            webpage_genre = 'Science+Fiction';
        else:
            webpage_genre = self.genre;




        for i in range(1,19):
            a_url = 'https://www.alibris.com/search/books/subject/' + webpage_genre + '?qsort=&page=' + str(i);
            start_urls.append(a_url);
        

        start_urls.append('https://www.fictiondb.com/search/searchresults.htm?srchtxt=' + webpage_genre + '&styp=5');    
        start_urls.append('https://www.goodreads.com/genres/' + webpage_genre);   
    

        for url in start_urls:
            print 'Current URL: ' + url;
            request = scrapy.Request(url, callback = self.parse)
            yield request 
                



    #Parse dates from each book. If date doesnt exist, then we append list with a '0'. To indicate to skip over when we read it later.
    def extract_dates(self, dates):


        date_list = [];
        date_del_counter = 0;
        i = 0;


        while i < len(dates):


            d = dates[i].strip();
            d = d.replace('"','');
            d = str(d);
            
            if  re.search('[a-zA-Z]', str(d)) and len(d) > 4 :
                date_list.append(str(d[-4:]));
                i += 1;
                continue;
            elif len(d) == 4 and re.search(r'\d', str(d)):
                date_list.append(d);
                i += 1;
                continue;
            else:
                try:
                    d2 = str(dates[i + 1]);
                    d3 = str(dates[i + 2]);
                    d4 = str(dates[i + 3]);


                    if (d.isspace() or d is None or not d) and (d2.isspace()) and (d3.isspace()) and (d4.isspace()):
                        
                        date_list.append(0);
                        i += 2;
                        continue;

                    
                    i += 1;    


                except Exception as e:
                    print '~~ dates[n] Exception: ' + str(e);
                    i +=1;

        return date_list;    






    def parse(self, response):


        if('https://www.alibris.com/search/books/' in response.url):
            print "----------------------------------------- BookLink ----------------------------"
            for bl in response.xpath('//*[@id="selected-works"]/ul/li/a/@href').extract():
                #parse info(book title, author first and last name).Then inserts into SQL data 


                self.parse_bookLink(bl);
                yield ScrapbooksItem(bookLink=bl);
            
        elif('https://www.fictiondb.com/search/' in response.url):

            bookTitle = response.xpath('/html/body/div[2]/div/section[2]/div/div/div[1]/div/div/table/tbody/tr/td/h5/a/span/text()').extract();
            authorName = response.xpath('/html/body/div[2]/div/section[2]/div/div/div[1]/div/div/table/tbody/tr/td/a/text()').extract();
            dates = response.xpath('/html/body/div[2]/div/section[2]/div/div/div[1]/div/div/table/tbody/tr/td/text()').extract();

            
            print 'bookTitle list length: ' + str(len(bookTitle));
            print 'authorName list length: ' + str(len(authorName));


            date_list = self.extract_dates(dates);


            loop_counter = 0;
            dateCounter = 0;

            for index in range(len(bookTitle)):
                try:

                    bt = bookTitle[index];
                    an = authorName[index];                
                    date = date_list[dateCounter];
                    dateCounter += 1;   
        
                    print '\n';
                    

                    #no date avaibale, we must shift array(skip book)
                    if (date == 0):
                        print '## continue if statement for title: ' + str(bt);
                        print '## continue if statment date: ' + str(date);
                        #dateCounter += 1;
                        index += 1;
                        continue;
                        

                    #HMED-171    
                    if ('-' in date):
                        print '## - is in date. Cant extract date';
                        dateCounter += 1;
                        continue;




                    print '## Date: ' + str(date) + ' for ' + str(bt);


                    year_valid = self.validDates(date); 

                    #parsed date is valid for client's year perference.
                    if year_valid:
                        self.parseFullInfo(bt, an, date);
                    else:
                        print '## Else statement since date isnt valid for clients perference.';

                    
                    loop_counter += 1;
        

                    if (loop_counter < len(bookTitle)):
                        yield ScrapbooksItem(bookTitle =  bt)   
                    else:
                       
                        break;
                except Exception as e:
                    print '~~ bookTitle loop Exception: ' + str(e);


      
        elif('https://www.goodreads.com/' in response.url):
            print '------------------------- Good Reads -------------------------------';

            for bi in response.xpath('//img[@class="bookImage"]//@alt'):
                bi = str(bi).strip();

                bookTitle = '';

                if '(' in bi:
                    bookTitle = bi[bi.index('data=u') + 6 : bi.index('(') - 1];
                else:
                   bookTitle = bi[bi.index('data=u') + 6 :len(bi) - 1];

                bookTitle  = bookTitle.replace("'",'');
                bookTitle  = bookTitle.replace('"','');
            
                print 'Book Image Title: ' + bookTitle;

                self.insertInfo(bookTitle, '', '');
                yield ScrapbooksItem(bookImage = bi);

        else:
            pass;








    def validDates(self,parse_date):
        client_years = self.getYears();
        startYear = client_years[0];
        endYear = client_years[1];

        return (startYear <= parse_date) and (parse_date <= endYear);







    def parse_bookLink(self,bl):
        bl = bl.strip();
            
        #Just get the title. From the first to second foward slash 

        filterTitle = '';

        for c in bl[1:]:
            if c == '/':
                break
            else:
                filterTitle += c;

        #for instance, bl = ' The-Wrong-Side-of-Goodbye-Michael-Connelly '        
        #Extract book author and title. Find second to last  (-) , index of (-) onward is authors full name

        authorName = self.parse_author_name(filterTitle, 0);

        #Get first & last name of author

        firstName = authorName[0:authorName.find('-')];
        firstName = firstName.strip();
        lastName = authorName[authorName.find('-') + 1:];
        lastName = lastName.strip();

        title = self.getTitle(str(bl) , "", "");

        title = title.replace('-', ' ');
        title = title.strip();

       
        print 'alibris book: ' + str(bl);
        print 'Author First Name: ' + firstName;
        print 'Author Last Name: ' + lastName;


        client_firstName = self.getFirstName();
        client_lastName = self.getLastName();
        
        


        #Compares client data to data scraped, to see if we should add it to the SQL database.
        if client_lastName.lower() == lastName.lower():
            self.insertInfo(title,firstName, lastName);
        elif client_firstName.lower() == firstName.lower():
            self.insertInfo(title,firstName, lastName);
        #Both first and last name given by client are empty strings. So we just add to the database.    
        elif not client_firstName and not client_lastName:
            self.insertInfo(title, firstName, lastName);
        
        #Both first and last names dont equal information given from client_data.json    
        else:
            pass;






    def getTitle(self,title, superstring, substring):
        #Only one - means we reached the author
        if(title.count('-') == 1):
            #To remove the first '/'
            superstring = superstring[1:];
            return superstring;
        

        closestDashIndex = title.find('-');
        
        #The
        substring = title[0 : closestDashIndex]; 

        # ** Add - to show where the spaces are **
        substring = substring + '-';
        #superstring appends saved data from previous iteration
        superstring += substring;
        
        #-Wrong-side-of-goodbye-Micheal-connelly
        title = title[closestDashIndex + 1: ];
        return self.getTitle(title,superstring, substring);



        
    def parse_author_name(self,filterTitle, dashes):
        if(filterTitle.count('-') == 1):
            return filterTitle;

        closestDashIndex = filterTitle.find('-');
        filterTitle = filterTitle[closestDashIndex + 1 :];
        dashes = filterTitle.count('-');

        return self.parse_author_name(filterTitle, dashes);




    def parseFullInfo(self,title, fullName, date):

        print 'Inside parseFullInfo method';
        correct_date = True;


        try:
            if date > 0:
                date = int(date);
        except Exception as e:
            print '~~ int(date) Exception ' + str(e) + ' ~~';
            correct_date = False;



        #A person wrote the book

        if(',' in fullName) and correct_date:
            fullName = str(fullName).strip();

            lastName = fullName[0: fullName.index(',')];
            lastName = lastName.strip();
            firstName = fullName[fullName.index(',') + 1 : ];
            firstName = firstName.strip();

            client_firstName = self.getFirstName();
            client_lastName = self.getLastName();

            print 'fictiondb book title: ' + title;
            print 'fictiondb first name: ' + firstName; 
            print 'fictiondb last name: ' + lastName; 
            print 'fictiondb date: ' + str(date);


            print 'Client First Name: ' + client_firstName;
            print 'Client Last Name: ' + client_lastName;


            #Compares client data to data scraped, to see if we should add it to the SQL database.
            if client_lastName.lower() == lastName.lower():
                self.insertInfo_date(title,firstName, lastName, date);
            elif client_firstName.lower() == firstName.lower():
                self.insertInfo_date(title,firstName, lastName, date);
            #Both first and last name given by client are empty strings. So we just add to the database.    
            elif not client_firstName and not client_lastName:
                self.insertInfo_date(title, firstName, lastName, date);
            #Both first and last names dont equal information given from client_data.json   
            else:
                pass;




        

            

         
  

