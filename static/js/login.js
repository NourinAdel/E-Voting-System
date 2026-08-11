const loginForm = document.getElementById('loginPage');

loginForm.addEventListener('submit', function(event){
    event.preventDefault(); // Prevents page reloading.
    
    const username = document.getElementById('username').value;
    const plainPassword = document.getElementById('password').value;
    
    fetch('/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: username,
            password: plainPassword
        })
    })

    .then(response => response.json()) // Turn incoming response to JSON format.
    .then(data => {
        if (data.status === 'success'){
            window.location.href = data.redirect_url;
        }

        // If login failed.
        else {
            const errorDisplay = document.getElementById('errorMessage');
            errorDisplay.innerText = data.message;
            errorDisplay.style.color = "#c20000";
            
            setTimeout(function() {
                errorDisplay.innerText = ""; // Erases the text after 5 seconds.
            }, 5000);
        }
    })
    .catch(error => {

    console.error("Something Went Wrong...:", error);

    const errorDisplay = document.getElementById('errorMessage');
    errorDisplay.innerText = "Cannot connect to the server. Please check your internet or try again later.";
    errorDisplay.style.color = "#c20000";

    });

});