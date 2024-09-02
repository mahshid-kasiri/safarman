document.getElementById('uploadButton').addEventListener('click', function() {
    document.getElementById('fileInput').click();
});


document.getElementById('fileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // // تنظیمات عرض و ارتفاع پنجره
            // const width = 1000;  // عرض مورد نظر
            // const height = 600;  // ارتفاع مورد نظر
            
            // // محاسبه موقعیت افقی و عمودی برای وسط
            // const left = (window.screen.width - width) / 2;
            // const top = (window.screen.height - height) / 2;
            
            // باز کردن پنجره جدید با ویژگی‌های مشخص
            const previewWindow = window.open('preview.html', '_blank');
            
            previewWindow.onload = function() {
                previewWindow.postMessage(e.target.result, '*');
            };
        };
        reader.readAsDataURL(file);
    }
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