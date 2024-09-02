document.getElementById('registerBtn').disabled = true; // در ابتدا دکمه غیرفعال است

function checkPasswords() {
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const submitBtn = document.getElementById('registerBtn');

    if (password === confirmPassword && password !== '') {
        registerBtn.disabled = false;
    } else {
        registerBtn.disabled = true;
    }
}



