<?php

session_start();


error_reporting(E_ALL);
ini_set('display_errors', 'On');



//Load Composer's autoloader

require_once('/usr/share/php/libphp-phpmailer/PHPMailerAutoload.php');



   if(!isset($_POST["client_email"]) || empty($_POST["client_email"])) {
   
    header("location: display.php?email=empty");
    
    }elseif(!isset($_SESSION['email_list']) ||  empty($_SESSION['email_list']))   {

        header("location: display.php?list=empty");
    }

    else{
    
    $mail = new PHPMailer(true);                          // Passing `true` enables exceptions
    try {

    header("location: display.php?email=sent");   
    //Server settings
    $mail->SMTPDebug = 2;                                 // Enable verbose debug output
    $mail->isSMTP();                                      // Set mailer to use SMTP
    $mail->Host = 'smtp.gmail.com';                       // Specify main and backup SMTP servers
    $mail->SMTPAuth = true;                               // Enable SMTP authentication
    $mail->Username = 'BookCrawler10@gmail.com';                 // SMTP username
    $mail->Password = 'fakeepasswordemail';                           // SMTP password
    $mail->SMTPSecure = 'tls';                            // Enable TLS encryption, `ssl` also accepted
    $mail->Port = 587;                                    // TCP port to connect to

    //Recipients
    $mail->setFrom('from@example.com', 'Mailer');
    $mail->addAddress($_POST['client_email'], 'Client User');     // Add a recipient
    // $mail->addAddress('ellen@example.com');               // Name is optional
    $mail->addReplyTo('info@example.com', 'Information');
    $mail->addCC('cc@example.com');
    //$mail->addBCC('bcc@example.com');

    //Attachments
    //$mail->addAttachment('/var/tmp/file.tar.gz');         // Add attachments
    //$mail->addAttachment('/tmp/image.jpg', 'new.jpg');    // Optional name

    //Content
    $mail->isHTML(true);                                  // Set email format to HTML
    $mail->Subject = 'List of Books from Book Crawler Website';

   
    $counter = 0;
    $message = "";



    //show list of books
    foreach ($_SESSION['email_list'] as $key => $value ) {
        $counter += 1;
        $message .=  $counter . ".) " . $value . "\n";
    }


    $mail->Body    =  $message;
    $mail->AltBody = 'AltBody:  \n' . $message;

    $mail->send();

   
    } catch (Exception $e) {
    echo 'Message could not be sent. Mailer Error: ', $mail->ErrorInfo;
    header("location: display.php?email=send_error");

    }

    } //end else statement


?>