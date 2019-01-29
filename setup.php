<!DOCTYPE html>

<?
session_start();

?>

<html>
<head>

	<meta charset="utf-8">
	<title>Book Web Crawler</title>
	<link rel="stylesheet" type="text/css" href="setup.css">

</head>
<body>


	<!-- Header -->

	<header class="header">

		<image  src = "logo.png" id = "logo">

		</header>


		<div id = 'main_info'>


		<!-- Website's privacy policy -->
		<div id = 'privacy'>
			
			<center><i>	<b> Privacy Policy </b>	</i></center>
			<hr>

			<p>
				BookCrawl doesnt save any data whatsoever. Which includes but is not limited to
				client's location, cookies, email, client machine, or even book perference. All data is erased after the 
				end of every session. We protect and understand the importance of security. 

			</p>	


		</div>




		<!-- Container for information -->
	

		<div class="container">
			<p>If your not quite sure about the information or dont care for a perference. Then feel free to <b>leave the specfic input empty. </b> </p> <br>

			<!-- Genre options -->
	<form action="data.php" method="GET">

				<center>


				<span class="genreSpan">
					<p><b>Genre  </b> </p>					
					<select id="genres" name="genre_choice"></select>

				</span>
				<br>

				<!-- Author name -->
				<span>
					<p><strong>Author's Information </strong> </p>
					<input type="text" name="firstName" id="first" placeholder="Author First Name">
					<input type="text" name="lastName" id="last" placeholder="Author Last Name">

				</span> <br>


				<!-- Year range of book -->

				<span>


					<p><strong>Year Range of Book</strong></p>
					<p>From Year</p><input type="number" name="startYr" required="required">
					<p>To Year</p><input type="number" name="endYr" required="required"> 

<!-- Check URL if header function is invoked. We go to
	data.html and check URL to see/display specific error --> 

	<?php
	session_start();
	$fullUrl = "http://" . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];

	//Check whats the error message depending on what we added to URL
	if(strpos($fullUrl,"yearRange=startYr") == true){
		echo "<p class = 'error'>  Error! " . $_SESSION['startYr'] . " is greater than " . date("Y") . "which isnt possible.
		Enter a lower start year  </p> ";

	}

	elseif (strpos($fullUrl,"yearRange=endYr") == true) {
		echo "<p class = 'error'>  Error! " . $_SESSION['endYr'] . " is greater than " . date("Y") . " which isnt possible. Enter a lower end year  </p> ";
	}
	elseif (strpos($fullUrl, "yearRange=empty") == true) {
		echo "<p class = 'error'>  Error! One of the years input is empty </p> ";
			
	}	
	else{
		
	}

	?>


</span>
<br>	

<!-- Size of book -->
<span>
	<p><strong>Max Book Page Length</strong></p>	

	<input type="number" name="pages" required="required">
</span> <br> 

<!-- Specific Book Publisher -->
<span>
	<p><strong>Book Publisher</strong></p>	
	<input type="text" name="publisher" placeholder="Penguin Random House">

</span> <br>


<!-- Buttons to sumbit data and clear data to reinput data -->

<span id="buttons">

	<input type="submit" name="loadBtn" value="Search me a book!">

</form>

<button type="button" title="Clear All Data." style="border-radius: 10px"  onclick="clearData()" >Reset Data</button> 
</span>

</div>

</center>



	<div class="info">
	

		<p> Process might take some time to load. Usually takes 6-10 mintues. <br> 
		Please wait while website collects data. <br>
		<b> * Note ! The more info you provide, the more quicker will the program run * </b> 
		</p>



	</div>

<!-- main_info div -->
</div>	



<br><br><br><br>




<!-- footer that contains site info --> 
<footer id = 'footer'>
	
	<i>	<h4>Special thanks to the following websites. <br> Allowing us to scrap through their data.</h4> <i>


	<div id = 'sources_div'>

	<?php  

	$arr = array('alibris.com','book-genres.com','fictiondb.com', 'amazon.com', 'bing/images', 'goodreads.com');

	$counter = 0;
		foreach ($arr as $key => $value) {
			if($counter >=2 ){
					echo "<br>";
					$counter = 0;
			}

			echo "<h2> $value </h2>";
			$counter += 1;
		}



	?>

</div>



</footer>









<script type="text/javascript">


//Clear All Data To input a new book search
function clearData(){

//Start at index 2 to not clear feedback button. Minus one b/c we dont want to clear  reset data button info
var allInput = document.getElementsByTagName("input");
for(var i = 2; i < allInput.length -1; i++){
	console.log("Index: " + i + " " + allInput[i].value);
	allInput[i].value = "";
	}

}


//Add genres to drop-down menu via for loop
function genreMaker() {
	var	menu = document.getElementById("genres");
	var genreArr = new Array(
		'Satire',
		'Drama',
		'Adventure',
		'Romance',
		'Mystery', 
		'Horror',
		'Health',
		'Children',
		'Religion',
		'Science',
		'Science-Fiction',
		'History',
		'Math',
		'Poetry',
		'Cookbooks',
		'Biographies',
		'Autobiographies',
		'Fantasy');

	//Runs through array and adds values to genre select tag
	for(var i = 0; i < genreArr.length; i++){

		var opt= document.createElement("option");
		//Each option value is the genre name itself. Easier to find later
		opt.value = genreArr[i];
		opt.innerHTML = genreArr[i];
		//Add new option to menu
		menu.appendChild(opt);

	}
}

genreMaker();

</script>


</body>
</html>