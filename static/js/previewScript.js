window.addEventListener('message', function(event) {
    const imageURL = event.data;
    document.getElementById('previewImage').src = imageURL;
}) ;

document.getElementById('sendPostData').addEventListener('click', function() {
    window.close();
});




