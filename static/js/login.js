document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('login-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // Perform AJAX request to Flask backend for login
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/dashboard';
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
