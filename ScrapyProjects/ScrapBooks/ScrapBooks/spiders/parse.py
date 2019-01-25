



def main(filterTitle,dashes,iterations):

	if(filterTitle.count('-') == 1):
		print '*** Inside base case';
		print 'Solution: ' + filterTitle;
		return filterTitle;


	print 'Iteration: ' + str(iterations);

	closestDashIndex = filterTitle.find('-');

	filterTitle = filterTitle[closestDashIndex + 1 :];
	print ' ~~ New Title: ' + filterTitle + " ~~";

	dashes = filterTitle.count('-');

	return main(filterTitle, dashes, iterations + 1);




def getTitle(title, superstring, substring, iterations):
	print '\n'
	print 'Iterations: ' + str(iterations);

	#Only one - means we reached the author
	if(title.count('-') == 1):
		print 'INSIDE BREAK STATEMENT !!!!';
		#The-Wrong-Side-of-Goodbye
		return superstring;
	

	closestDashIndex = title.find('-');
	print 'Closest Dash Index: ' + str(closestDashIndex); 

	
	#The
	substring = title[0 : closestDashIndex]; 

	# ** Add - to show where the spaces are **
	substring = substring + '-';
	#superstring appends saved data from previous iteration
	superstring += substring;

	
	print '## SUPERSTRING: ' + superstring;
	#-Wrong-side-of-goodbye-Micheal-connelly
	title = title[closestDashIndex + 1: ];

	print 'Rest of title: ' + title;

	return getTitle(title,superstring, substring, iterations + 1);






if __name__ == '__main__':
	"""
	title = 'The-Wrong-Side-of-Goodbye-Michael-Connelly';

	authorName = main(title,0,0);

	
	firstName = authorName[0:authorName.find('-')];
	lastName = authorName[authorName.find('-') + 1:];

	print 'First Name: ' + firstName;
	print 'Last Name: ' + lastName;
	
	print '\n -------------------------------------------------';


	onlyTitle = getTitle(title, "","",0);
	onlyTitle = onlyTitle.replace('-',' ');
	print onlyTitle;	
	"""

	spaces_string = '      WHitehodowhitehoodkkk  ';
	spaces_string = spaces_string.strip();

	print ' ' in spaces_string;