document.getElementById('uploadButton').addEventListener('click', function() {
    document.getElementById('fileInput').click();
});


// جاوا اسکریپت برای نمایش متن با کلیک بر روی دکمه
document.getElementById("searchButton").onclick = function() {
    var searchCity = document.getElementById("searchCity");
    if (searchCity.style.display === "none") {
        searchButton.style.display = "none";
        searchCity.style.display = "block"; // نمایش متن
    } else {
        searchCity.style.display = "none"; // مخفی کردن متن
        // searchButton.style.display = "block";
    }
};