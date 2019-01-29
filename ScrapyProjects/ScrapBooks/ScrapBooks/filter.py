
import json
import MySQLdb
import mechanize
from bs4 import BeautifulSoup



conn = MySQLdb.connect(host="127.0.0.1",user="root", passwd="fakepasswordgithub", db="BookCrawler");
# you must create a Cursor object. It will let you execute all the queries you need  
cur = conn.cursor();



def getGenre():
    with open('/var/www/html/BookCrawl/client_data.json') as f:       
        data = json.load(f);
        genre = data["genre"].replace('"', '');
        return genre.strip();



def getLastName():
    with open('/var/www/html/BookCrawl/client_data.json') as f:
        data = json.load(f);
        lastName = data['lastName'].strip();
        return lastName;
    
def getFirstName():
    with open('/var/www/html/BookCrawl/client_data.json') as f:
        data = json.load(f);
        firstName = data['firstName'].strip();
        return firstName;

def getPages():
    with open('/var/www/html/BookCrawl/client_data.json') as f:
        data = json.load(f);
        pages = data['pages'].strip();
        return int(pages);


def getYears():
    with open('/var/www/html/BookCrawl/client_data.json') as f:
        data = json.load(f);
        startYear = data['startYr'].strip();
        endYear = data['endYr'].strip();
        return [int(startYear), int(endYear)];




def getPublisher():
    with open('/var/www/html/BookCrawl/client_data.json') as f:
        data = json.load(f);
        publisher = data['publisher'].strip();
        return publisher;







def valid_books_json(title, firstName, lastName, year, publisher, pages, src):
    print 'Inside valid_books.json'


    if not (firstName) or None:
        firstName = 'N/A';
    if not (lastName) or None:
        lastName = 'N/A';
    if not(year) or None:
        year = 'N/A';
    if not (publisher) or None:
        publisher = 'N/A';
    if not (pages) or None:
        pages = 'N/A';




    try:
        with open('/var/www/html/BookCrawl/valid_books.json') as infile:
            data = json.load(infile)
    except Exception as e:
        data = {}
    if not data:
        data = {} 

    data[title] = []

    data[title].append({
        'src' : src ,
        'firstName' : firstName  ,
        'lastName' : lastName ,
        'year' : year, 
        'publisher'  : publisher ,
        'pages' : pages 

    })

    with open('/var/www/html/BookCrawl/valid_books.json','w+') as outfile:
      json.dump(data,outfile , default = set_default)




def set_default(obj):
    if isinstance(obj,set):
        return list(obj) 





#Searches bing images for book cover. If not found, the we search amazon website
def searchImg(title,lastName):
    title = title.replace(',','')
    title = title.strip();

    try:

       
        base_url = 'https://www.bing.com/images/search?q=' + title.replace(' ', '+') + "+Novel";
        search_url = base_url 
        
        print 'Search Url: ' + search_url + '\n';


        br = mechanize.Browser();
        br.set_handle_robots(False)
        br.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36')]
        response = br.open(search_url).read();
        
        soup = BeautifulSoup(response, 'html.parser');

        img_list = list(soup.findAll('img'));

        #print img_list[len(img_list) - 4]['src'];        

        title_temp = title.replace(' ', '+') + "+Novel";
        
       

        counter = 1;

        #Find src with title inside of string. All images gathered from Bing
        for image_tag in img_list:
            src = image_tag['src']; 
            #our query is in one of the https image src
            if title_temp in src and 'https://' in src:
                print "Book Cover Src: " + src;
                return src;
        


         #Search amazon for book cover, if none was found in Bing Images
         #We only get accurate pictures if last name of author is known. (Not NUll)
       
        return "";
        return amazonImg(title,lastName);
        
    except Exception as e:
        print "~~ searchImg Exception: " + str(e) + " ~~"
        #return amazonImg(title,lastName);
        return "";






def amazonImg(title,lastName):
    print "@@@@ Inside amazon image method @@@@"
    try:

        chrome = mechanize.Browser()
        chrome.set_handle_robots(False)
        chrome.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36')]
        base_url = 'https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Dstripbooks&field-keywords=' + title.replace(' ', '+') + '+novel+' + lastName;
        search_url = base_url 
        print "Search Url: " + search_url
        htmltext = chrome.open(search_url).read()
        

        soup = BeautifulSoup(htmltext, 'lxml')

        imgTags = soup.find_all('img' , {'class': 's-access-image cfMarker'})


        for i in imgTags:
            if "https" in i['src']:
                print 'Amazon Book Cover: ' +  i['src']
                return i['src'];
                break;

    except Exception as e:
        print "~~ amazonImg Exception: " + str(e) + " ~~";
        return "";





def final_choices():

    genre = getGenre();
    firstName = getFirstName();
    lastName = getLastName();
    pages = getPages();
    years = getYears();
    publisher = getPublisher();


    startYr = years[0];
    endYr = years[1];

    #SELECT * FROM `Fantasy`WHERE (877 >= Pages and Book IS NOT NULL AND ( StartYear <= 1900 <= 2017) AND FirstName = 'Janelle') 
    #SELECT * FROM `Fantasy`WHERE (877 >= Pages and Book IS NOT NULL AND ( StartYear <= 1900 <= 2017) AND FirstName IS NOT NULL) 
    #SELECT * FROM Fantasy WHERE (877 >= Pages AND Book IS NOT NULL AND (StartYear <= 1900 <= 2017) AND FirstName IS NOT NULL AND LastName = 'Denison' AND Publisher IS NOT NULL);

    query = "SELECT * FROM %s WHERE (%d >= Pages) AND Book IS NOT NULL AND (StartYear <= %d <= %d)" % (genre, pages, startYr, endYr);


    if firstName:
        query += " AND FirstName = '%s'" % (firstName);
    else:
        query +=  " AND FirstName IS NOT NULL";


    if lastName:
        query +=  " AND LastName = '%s'" % (lastName); 
    else:
        query +=  " AND LastName IS NOT NULL";


    if publisher:
        query += " AND Publisher = '%s'" % (publisher);
    else:
        query +=  '';


    print "Query: " + query;

    cur.execute(query);
    data = cur.fetchall();
    data = list(data);  


    for i in range(len(data)):

        firstName = data[i][1];
        lastName = data[i][2];
        year = data[i][3];
        pages = data[i][4];
        publisher = data[i][5];
        title = data[i][6];


        #WE GOT A MATCH !! A BOOK RECOMMENDATION BASED ON CLIENT PERFERENCE
        print '\n ****** MATCH !!! BOOK RECOMMENDATION IS: ' + title + " by " + firstName + " " + lastName + '*******\n';

        #scraps amazon and bings image database. Match picture to book
        #image_src = searchImg(title,lastName);

        #Save valid book along with its image(if one is found)
        valid_books_json(title, firstName, lastName, year, publisher, pages, "");

   





def empty_table(genre):
    cur.execute("TRUNCATE TABLE %s " % (genre));
    conn.commit();
    print genre + " table has been emptied";





def sql_extract(genre, query):
    cur.execute("SELECT * FROM %s WHERE BOOK IS NOT NULL %s" % (genre, query)); 
    data = cur.fetchall();

    data = list(data);

    try:
        #50 is our limit for amount of books we show. EVEN IF we have few valid books based on author's name
        for i in range(35):
            #returns only book title for row index i. Column 6
            title = str(data[i][6]).strip();
            title = title.replace(' ','-');
        

            sql_firstName = data[i][1];
            sql_lastName = data[i][2];  
            sql_year = data[i][3];
            sql_pages = data[i][4];
            sql_publisher = data[i][5];

            image_src = searchImg(title, sql_lastName); 
            valid_books_json(title, sql_firstName, sql_lastName, sql_year, sql_publisher, sql_pages, image_src);

    except Exception as e:
      print "~~ sql_extract Exception: " + str(e) + ' ~~';









def main():
    #final_choices();

    genre = getGenre();
    firstName = getFirstName();
    lastName = getLastName();

    if not firstName and not lastName:
        query = 'AND StartYear IS NOT NULL';

        sql_extract(genre , query);
    elif firstName:
        query = " AND FirstName = '%s'" % (firstName);
        sql_extract(genre, query);
    elif lastName:
        query = " AND LastName = '%s'" % (lastName);
        sql_extract(genre, query);
    else:
        pass;


    empty_table(genre);








if __name__ == '__main__':
    main();