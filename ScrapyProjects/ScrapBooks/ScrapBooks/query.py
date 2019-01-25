#!/usr/bin/python
# -*- coding: utf-8 -*-  
from bs4 import BeautifulSoup
import requests
#from googlesearch import search
import json
from MyAdapter import MyAdapter
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from lxml.html import fromstring
from itertools import cycle
import traceback
import time
#import sys
#sys.path.append('/home/edwin/.local/lib/python2.7/site-packages/mechanize')
import mechanize
import os
import MySQLdb

from datetime import datetime

import mechanize




#If we found a match from our first method, where we already have the last name from the SQL database.
match_found = False;



#set up MySQL database 
conn = MySQLdb.connect(host="127.0.0.1",user="root", passwd="fakepassword", db="BookCrawler");
# you must create a Cursor object. It will let you execute all the queries you need  
cur = conn.cursor();


def getGenre():
    with open('/var/www/html/client_data.json') as f:       
        data = json.load(f);
        genre = data["genre"].replace('"', '');
        return genre;


#returns authors last name outlined by user beforehand. Could be blank(dont have a specific author in mind)
def getLastName():
    with open('/var/www/html/client_data.json') as f:
        data = json.load(f);
        lastName = data['lastName'].strip();
        return lastName;
    
def getFirstName():
    with open('/var/www/html/client_data.json') as f:
        data = json.load(f);
        firstName = data['firstName'].strip();
        return firstName;

def getPages():
    with open('/var/www/html/client_data.json') as f:
        data = json.load(f);
        pages = data['pages'].strip();
        return pages;


def getYears():
    with open('/var/www/html/client_data.json') as f:
        data = json.load(f);
        startYear = data['startYr'].strip();
        endYear = data['endYr'].strip();
        return [startYear, endYear];








#SQL Query for all books who DON'T have lastName info, we scrap the web for lastName info so then we can compare to client perference.
def incomplete_books(genre):
    cur.execute("SELECT * FROM %s WHERE BOOK IS NOT NULL" % (genre)); 
    data = cur.fetchall();

    data = list(data);

    try:
        for i in range(50):
            #returns only book title for row index i. Column 6
            title = str(data[i][6]).strip();
            title = title.replace(' ','-');
            googleScrap(title);
      

    except Exception as e:
      print "~~ incomplete_books Exception: " + str(e) + ' ~~';








"""
From SQL database, if certain attributes avavaible are 
not null and they dont match atrributes from client_data.json. Then
we can ignore them in our google query
"""

def nameMatches(genre, name, which_name_bool):

    name_column = '';

    if which_name_bool:
        name_column = 'LastName';
    else:
        name_column = 'FirstName';



    #*** To check possible matches, we use/look at author's last name. Best indiction to go off of. ***
    cur.execute("SELECT * FROM %s WHERE %s = '%s'" % (genre, name_column, name));
    data = cur.fetchall();

    #atleast one element that has same last name 
    if(len(data) > 0):
        for i in range(len(data)):
            #returns only book title for row index i. Column 6
            title = str(data[i][6]).strip();
            title = title.replace(' ','-');
            googleScrap(title);
            






def both_name_matches(genre, firstName, lastName):

    cur.execute("SELECT * FROM %s WHERE FirstName = '%s' and LastName = '%s'" % (genre, firstName, lastName));
    data = cur.fetchall();

    #atleast one element that has same last name 
    if(len(data) > 0):
        for i in range(len(data)):
            #returns only book title for row index i. Column 6
            title = str(data[i][6]).strip();
            title = title.replace(' ','-');
            googleScrap(title);








 # *** MAIN METHOD ***        
def main():

    genre = getGenre();
    lastName = getLastName();
    firstName = getFirstName();


    if firstName and lastName:
        both_name_matches(genre, firstName, lastName); 
    elif lastName:
        #SQL data already knows last name
        nameMatches(genre, lastName, True);
    elif firstName:
        nameMatches(genre, firstName, False);
    else:
        #Author first and last name are blank.
        incomplete_books(genre);

    






def sqlUpdate(title, date,firstName,lastName,pageCount,publisher):
    genre = getGenre();
    
    firstName = firstName.strip();
    lastName = lastName.strip();

    pageCount = str(pageCount);
    pageCount = pageCount.strip();

    title = title.replace("-", " ");
    #take care of apostrophe so we can insert it into SQL database
    title = title.replace("'", "''");
    publisher = publisher.replace("'","''"); 

    pageCount = pageCount.replace(',','');



    try:
        #check if string values arent empty
        if (date):
            date = int(date);
            cur.execute("UPDATE %s SET StartYear = %d WHERE Book = '%s'" % (genre, date, title));
            print 'StartYear has been updated';    
        if(firstName):
            cur.execute("UPDATE %s SET FirstName = '%s' WHERE Book = '%s'" % (genre, firstName, title));
            print 'FirstName has been updated';        
        if(lastName):
            cur.execute("UPDATE %s SET LastName = '%s' WHERE Book = '%s'" % (genre, lastName, title));
            print 'LastName has been updated';
        if(pageCount):
            pageCount = int(pageCount);
            cur.execute("UPDATE %s SET Pages = %d WHERE Book = '%s'" % (genre, pageCount, title));
            print 'Pages has been updated';
        if(publisher):
            cur.execute("UPDATE %s SET Publisher = '%s' WHERE Book = '%s'" % (genre, publisher, title));
            print 'Publisher has been updated';
        #execute all changes to database
        conn.commit();
    except Exception as e:
        print "~~ SQL Exception: " + str(e) + " ~~";





def delete_book(title, genre):
    

    try:

        cur.execute("DELETE FROM %s WHERE Book = '%s'" % (genre, title)); 
        conn.commit();
        print 'DELETED book: ' + title; 
    except Exception as e:
        print '~~ delete_book Exception: ' + str(e);






#arguments are data scraped from google .
#Check to see if we have to replace(attributes in SQL are null) all data before we fully check if it matches client's perference.
def swapData(title, date, firstName, lastName, pageCount, publisher):
   
    genre = getGenre();
    
    title = title.replace('-',' ');

    try:
        print ' || Title: ' + title;
        #gets data from current book we are looking at
        cur.execute("SELECT * FROM %s WHERE Book = '%s'" % (genre,title));
        data = cur.fetchall();
        
            
        sql_firstName = data[0][1];
        sql_lastName = data[0][2];
        sql_year = data[0][3];
        sql_pages = data[0][4];
        sql_publisher = data[0][5];


        #SQL data is NOT None/Empty
        if(sql_firstName):
            firstName = sql_firstName;
        if(sql_lastName):
            lastName = sql_lastName;

        if(sql_publisher):
            publisher = sql_publisher;
    
        if(sql_pages):
            pageCount = sql_pages;

        if(sql_year):
            date = sql_year;


        sqlUpdate(title, date, firstName, lastName, pageCount, publisher);


        #function for to check if we found a book that perefectly macthes client's perference. 
        #filter(firstName, lastName, date, publisher, pageCount,title);

        

    except Exception as e:
        print "## swapData Exception: " + str(e) + " ##";





def googleScrap(title):
    #Restart varaibles, so it doesnt save from last book info session
    
    date = ""
    firstName = ""
    lastName = ""
    pageCount = ""
    publisher = ""   

    playwright = False
    authors = False
    pages_bool = False
    originally_date_bool = False;

    try:
        print '\n';

        print 'Information for book: ' + title;

        chrome = mechanize.Browser()
        chrome.set_handle_robots(False)
        chrome.addheaders = [('User-agent', 
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36')]
        base_url = 'https://www.google.com/search?client=ubuntu&channel=fs&ei=EG4cW6Jii5zmAoHiqqgK&q='
        search_url = base_url +  title.replace(' ', '+') + '+novel';
        print 'Google Search Url: ' + search_url;
        htmltext = chrome.open(search_url)#.read()

      
        
        soup = BeautifulSoup(htmltext, 'lxml');

        #url = soup.find_all('span', class_='st')

        # arr = soup.body.find(text=re.compile('LrzXr'))
        links = soup.find_all('span')



        for ans in links:
            if 'Originally published:' in ans.text:
                fullDate = ans.next_sibling.text
                date = fullDate[-4:]
                print "Date: " + date
                originally_date_bool = True;
                continue;  


            if 'First performance:' in ans.text and not originally_date_bool:
                performance = ans.next_sibling.text;
                date  = performance[-4:]
                print 'First performance: ' + date;
                continue;


            elif 'Playwright:' in ans.text:
                fullName = ans.next_sibling.text.strip()
                firstName = fullName[0:fullName.index(" ")]
                lastName = fullName[fullName.index(" "):len(fullName)]
                print 'First Name from playwright: ' + firstName
                print 'Last Name from playwright: ' + lastName   
                playwright = True
                continue;
                

            elif 'Authors:' in ans.text and not playwright:
                full_authors = ans.next_sibling.text.strip()
                firstName = full_authors[0:full_authors.index(" ")]
                lastName = full_authors[full_authors.index(" "):full_authors.index(",")]
                print "## First Name from ~~Authors: " + firstName
                print "## Last Name from ~~Authors: " + lastName
                authors = True
                continue;
                

            elif 'Author:'in ans.text and not authors and not playwright:  
                fullName = ans.next_sibling.text.strip()
                firstName = fullName[0:fullName.index(" ")]
                lastName = fullName[fullName.index(" "):len(fullName)]
                print 'firstName from Author: ' + firstName
                print 'lastName from Author: ' + lastName   
                #We have our name information. Set flags to True, so we dont scrap our 'name' info.
                authors = True;
                playwright = True;
                continue;
                

            elif 'Pages:' in ans.text:
                fullInfo = ans.next_sibling.strip();
                pageCount = fullInfo[0:fullInfo.index(" ")]   
                print "$$$$ Pages: " + pageCount
                pages_bool = True
                continue;
                

            elif 'Page count:' in ans.text and not pages_bool:
                ageCount = ans.next_sibling
                print "Page Count: " + ageCount.text
                pageCount = ageCount.text  
                continue;

            
            elif 'Publisher' in ans.text:  
                publisher = ans.next_sibling.text.strip();
                print 'Publisher: ' + publisher
                continue;

            else:
                pass




        is_valid =  pages_date_filter(date, pageCount);


        if is_valid:
            title.replace('+', ' ');
            client_firstName = getFirstName();
            swapData(title, date, firstName, lastName, pageCount, publisher);
        else:
            title.replace('+', ' ');
            genre = getGenre();
            delete_book(title, genre);



    except Exception as e:
        print "~~~ Google Scrap Exception: " + str(e) + " ~~~"

        
  


def pages_date_filter(date, pageCount):
    
    client_pages = getPages();
    years = getYears();
    client_startYear = years[0];
    client_endYear = years[1];


    pages_valid = False;
    date_valid = False;


    #both scrapped data is empty. Nothing to compare to client. Might as well remove it
    if not date and not pageCount:
        return False;


    if (pageCount):
        pages_valid = (client_pages >= pageCount);
   

    if (date):
        date_valid = (client_startYear <= date <= client_endYear);

  



    #Comparsion to check if book is valid enough from scraped data.

    #takes care of empty pages boolean condition
    if date_valid and pages_valid:
        return True;
        #date is most important, since thats the only data we can analyze. OR we cant find DATE, so we just remove book
    elif not date_valid:
        return False;
    elif date_valid and not pages_valid:
        return True;
    else:
        return True;











if __name__ == '__main__':  
    #View to see how long it takes for program to run
    startTime = datetime.now();

    s = requests.Session()
    s.mount('https://', MyAdapter())    
    
    #query searches to update and find books that match client's pereference
    main();
    

    print "Time it took to run query.py: " + str(datetime.now() - startTime);

