<!DOCTYPE html>

<?php
session_start();

error_reporting(E_ALL);
ini_set('display_errors', 'On');	
?>
<html>
<head>
	<meta charset="utf-8">
	<title>Book Crawl Display</title>
	<link rel="stylesheet" type="text/css" href="display.css">
	

</head>
<body>

<!-- Alert Box that message has been sent --> 
<?php

$fullUrl =  $fullUrl = "http://" . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];


if(strpos($fullUrl, 'email=sent') == true){

	echo '<script language="javascript">';
	echo 'alert("Email has been sent")';
	echo '</script>';
}


?>




 


<header id = "header">

	<h1>Book Crawler</h1>
	<img src="logo.png" height="150" width="150" id="logo">

	<div id = "header_line"> </div>


	<?php

	$file = file_get_contents('valid_books.json');
	$contents = json_decode($file);

	$counter = 0;


	foreach ($contents as $key) {
		$counter += 1 ;
	 }

	echo  "<span id = counter_span>	<b>	<p> Books Found: " . $counter . "</p> </b> </span>";
	

	?>




	
</header>



<!--- Display All Book Recommendations and their covers -->


	<div class="books_container">



	<?php


	$images_list = array();




	$file = file_get_contents('valid_books.json');
	$book_choices = json_decode($file, true);

	foreach ($book_choices as $key => $value) {

	$img_src =  $value[0]['src'];
	$book_img = "";


	//in case we couldnt find a book cover online
	if(empty($img_src)){

		$book_img = 'bookcover.png';

	}else{
		$book_img = $img_src;
	}

	array_push($images_list, $book_img);

}





	//Gets information from each book (publisher, author, date, pages)
	$file = file_get_contents('valid_books.json');
	$json_file = json_decode($file,true);

	
	$counter = 1;

	$email_book_list = array();


	foreach ($json_file as $key => $value) {


		$amazon_title_dash = $key;

		$key = str_replace('-', ' ', $key);
		array_push($email_book_list, $key);



		$book_img = array_pop($images_list);



		echo "

		<div class =  'book_layering'>

		<b>	$counter .) </b>

		<img src = $book_img alt = 'Book Cover' onclick= window.open('https://www.amazon.com/s/ref=nb_sb_ss_c_1_4?url=search-alias%3Daps&field-keywords=$amazon_title_dash+novel')	
		 class = 'bookCover'>

		";





		echo '<div  class = book_information>';

		echo '<i> Title: ' . $key . '<br>';
		echo '	First Name: ' . $value[0]['firstName'] . '<br>';
		echo 'Last Name: ' . $value[0]['lastName'] . '<br>';
		echo 'Publisher: ' . $value[0]['publisher'] . '<br>';
		echo 'Year: ' . $value[0]['year'] . '<br>';
		echo 'Pages: ' . $value[0]['pages'] . '<br> </i>';
		

		echo '</div>';

		echo '</div>';

		$counter +=  1;

	}

	//Saves book title for when we email them to client
	$_SESSION['email_list'] = $email_book_list;	


	?>


	</div>









<div class="client_info">
	
<?php

	echo "<b> User Info: </b> <br>";

	$file = file_get_contents('client_data.json');
	$json_file = json_decode($file,true);


	//Read client's data (pereference)
	foreach ($json_file as $key => $value) {

		$value2 = "";

		if(empty($value)){
			$value2 = 'N/A';
		}

		else if (strpos($value, 'eFiction') == true){


				$value2 = 'Science Fiction';
		}

		else{
			$value2 = $value;
		}
		

		echo $key . ': ' . $value2 . '<br>';
		
	}



?>

</div>

<br>







<!-- Footer so client can send an email of the results to themeselves -->

<div id = 'email_footer'>
	<b> <p id = 'email_label'>Email Yourself The Results </p> </b> 

	<div id = 'email_content'>
	<br>
	 <form action="email.php" method="post">
	 	<input type="email" name="client_email" placeholder="Your Email Address"> <br> <br> 
	
	 <?php  

	 //http://127.0.0.1/display.php?email=empty
	 $fullUrl = "http://" . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];


	 if(strpos($fullUrl, 'email=empty') == true){
	 	echo "<p  class = 'error'> **Error!	Email is empty! ** </p>";
	 }else if (strpos($fullUrl, 'email=send_error') == true){

	echo "<p  class = 'error'> **Error!	Email cant be sent. Does email exist? ** </p>";
	
	}else{

	}



	 ?>
		<input type="submit" value="Submit">
 
	 </form>

	 <!-- Email Content div end -->
	</div>

	<!-- Footer div tag ends -->	
</div>





</body>
</html>