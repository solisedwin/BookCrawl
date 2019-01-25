<?php  

ini_set('display_errors','On');
ini_set('error_reporting',E_ALL);	



class SQL {

private $conn;

	
	//default constructor. Sets up the connection to private varaible for whole class.
	function __construct($servername,$username,$password, $database){
			
		$this->conn =  mysqli_connect($servername, $username, $password, $database);

			if(!$this->conn){
				die(' 	Connection failed: ' . mysqli_connect_error());
			}else{
				echo ' Connected successfully';
			}
		
	}


//closes mysql conneciton
function closeConnection(){
	mysqli_close($this->conn);

}


function query($query){
	return mysqli_query($this->conn, $query);
}



function createTable($genre){

	$query = 'CREATE TABLE ' . $genre . '(
	ID int PRIMARY KEY AUTO_INCREMENT NOT NULL, 
	FirstName varchar(20) NULL,
 	LastName varchar(20)	NULL,
 	StartYear int(4) NULL,
 	Pages int(4) NULL,
 	Publisher varchar(40) NULL,
 	Book varchar(100) NOT NULL,
 	Image varchar(150) NULL	
 	);';
 	

 	$output = $this->query($query);

 	echo "<br>";

}


/*Check if client's genre choice is already made,
if not, we make a new table based on genre choice */
function tableCheck(){


	//Read genre client choose, from saved json file 
	$file = file_get_contents('client_data.json');
	$json_file = json_decode($file);
	$client_genre = $json_file->genre;
	

	$query = "SHOW TABLES;";
	$output = $this->query($query);
	
	$bool_tableExist = False;

	if($output && $output->num_rows > 0){
		$rows = $output->fetch_assoc();

		foreach ($rows as $value) {
			//Table already exist
			if($client_genre == $value){
				$bool_tableExist = True;	
				break;
			}

		}


	}//end if statement


	//Table doesnt exist for the genre choosen
	if(!$bool_tableExist){
		$this->createTable($client_genre);
	}


	return $client_genre;

}

function currentData(){
	echo 'Here is where we check back on our old data to seee if we get some matches';
}



function dataAmount($genre){
	$query = 'SELECT COUNT(*) total FROM ' . $genre;

	$output = $this->query($query);
	$rows = $output->fetch_assoc();
	$num_of_rows =  $rows['total'];
	echo ' ' . $num_of_rows . ' ';

	$_SESSION['scrap'] = 'Y';

	/*
	//We check SQL table for info
	if($num_of_rows > 140){
		currentData();
	}
	//We need to scrap more data 
	else{
		$_SESSION['scrap'] = 'Y';
	}
	*/

}



//End of SQL class 
}

$sql_obj = new SQL('localhost','root','fakepasswordgithubexample','BookCrawler');
$genre = $sql_obj->tableCheck();
$sql_obj->dataAmount($genre);






?>

