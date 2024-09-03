document.querySelectorAll('.reply-btn').forEach(button => {
    button.addEventListener('click', function() {
        // Find the reply form related to the clicked reply button
        const replyForm = this.nextElementSibling;

        // Toggle the visibility of the reply form
        if (replyForm.style.display === 'none') {
            // Hide all other reply forms first
            document.querySelectorAll('.sendReply').forEach(form => {
                form.style.display = 'none';
            });

            // Show the related reply form
            replyForm.style.display = 'block';
        } else {
            // Hide the form if it's already visible
            replyForm.style.display = 'none';
        }
    });
});

document.querySelectorAll('.send-btn').forEach(button => {
    button.addEventListener('click', function() {
        const replyForm = this.parentElement;
        const replyInput = replyForm.querySelector('.reply-input').value;

        if(replyInput.trim() !== "") {
            // You can add the reply to the comment here, or send it to the server.
            console.log("Reply sent:", replyInput);
            
            // Hide the reply form
            replyForm.style.display = 'none';
        }
    });
});