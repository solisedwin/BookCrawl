	<?php

	
	session_start();

error_reporting(E_ALL);
ini_set('display_errors', 'On');	




	ignore_user_abort(false);

		//Strings 
	$firstName = preg_replace("/[^a-zA-Z]/", "", $_GET['firstName']);
	$lastName = preg_replace("/[^a-zA-Z]/", "", $_GET['lastName']);
	$publisher = preg_replace("/[^a-zA-Z]/", "", $_GET['publisher']);


	$_SESSION['firstName'] = $firstName;
	$_SESSION['lastName'] = $lastName;
	$_SESSION['publisher'] = $publisher;
	$_SESSION['genre'] = $_GET['genre_choice'];
	$_SESSION['pages'] = $_GET['pages'];

	//Ints
	$_SESSION['startYr'] = $_GET['startYr'];
	$_SESSION['endYr'] = $_GET['endYr'];
	



	#main function that runs all the computations
	function main(){
		
		yearOver();
		createJson();
		sql();
		runLinux();	
	
	}

	

	/*Check inputed year has occured. No
	year is above current year. Or negative
	
	*/
	function yearOver(){

		$yearStartInput = $_GET['startYr'];
		$yearEndInput = $_GET['endYr'];
		$currentYear = date("Y");

		if($yearStartInput > $currentYear){
			header("Location: setup.php?yearRange=startYr");
			die();
		}

		elseif ($yearEndInput > $currentYear) {
			header("Location: setup.php?yearRange=endYr");
			die();	
		}

		else{
			print_r($_SESSION);
		}
	
	}



	

	//Saves clients book preference data in a json format
	function createJson(){

		
		if(file_exists('valid_books.json')){
			unlink('valid_books.json');
		}


		#science-fiction => scienceFiction

		$_SESSION['genre'] = str_replace('-', '', $_SESSION['genre']);
		

		#Penguin Books Publisher => Penguin+Books+Publisher
		if(empty($_SESSION['publisher']) == false){

		$_SESSION['publisher'] = str_replace(' ', '+', $_SESSION['publisher']);
			
		}else{
			$_SESSION['publisher'] = '';
		}




		$data = array("genre"=> $_SESSION['genre'],"firstName"=>$_SESSION['firstName'], "lastName"=>$_SESSION['lastName'],"publisher"=>$_SESSION['publisher'], "startYr"=>$_SESSION['startYr'], "endYr"=>$_SESSION['endYr'], "pages"=> $_SESSION['pages']);
		
		echo '<br>';
		
		$jsonContent = json_encode($data);	

		
		file_put_contents("/var/www/html/BookCrawl/client_data.json", $jsonContent);

	}



	/*
	Checks SQL database to see if we already have previous information 
	that links to client's perference. If not, we create new genre table 
	and scrap the web.
	*/

	function sql(){
		require_once('sql.php');

		echo '<br><br>';

	}

	/*
	Scraps the web for book suggestions. Runs python
	filter program as well to compare data and clients perference. 
	*/
	function runLinux(){

   	#runs albiris spider, gets All possible books. 
    $path = "/var/www/html/BookCrawl/ScrapyProjects/ScrapBooks/";
    chdir($path);
    $as_output = shell_exec("scrapy crawl as 2>&1");
	#echo "<pre> $as_output </pre>";

    #run google search query to collect intial info on books
	$query_path = "/var/www/html/BookCrawl/ScrapyProjects/ScrapBooks/ScrapBooks/";
	chdir($query_path);
	$query_output = shell_exec("python query.py 2>&1");
	

	#filter all the books that correspond with user pereference
	$query_path = "/var/www/html/BookCrawl/ScrapyProjects/ScrapBooks/ScrapBooks/";
	chdir($query_path);
	$filter_output = shell_exec("python filter.py 2>&1");
	


	//Change location to display.php
	$display_path = "/var/www/html/BookCrawl/";	
	chdir($display_path);
	header("location: display.php?stat=done");

	
	exit();

	}



	main();


	?>
