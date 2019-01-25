


var imgArray = ["books.png","openBook.png","nightBook.png"],
    curIndex = 0;
    imgDuration = 3000;

function slideShow() {
    document.getElementById('slider').className += "fadeOut";
    setTimeout(function() {
        document.getElementById('slider').src = imgArray[curIndex];
        document.getElementById('slider').className = "";
    },1000);
    curIndex++;
    if (curIndex == imgArray.length) { curIndex = 0; }
    //recurivsely calls setTimeout ?
    setTimeout(slideShow, imgDuration);
}

function redirect(){
	location.href = "setup.php";
}

slideShow();
