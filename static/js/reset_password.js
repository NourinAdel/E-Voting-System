const resetPage = document.getElementById('resetPage')

resetPage.addEventListener('submit', function(event){

    event.preventDefault();   

    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;

    if(password !== confirm_password){
        const errorDisplay = document.getElementById('errorMessage');
        errorDisplay.innerText = "Both passwords must match."
        errorDisplay.style.color = "#c20000";

        setTimeout(function() {
        errorDisplay.innerText = ""; // Erases the text after 5 seconds.
        }, 5000);
    }
    // TO-DO: Password length and symbols validation
    else{
            fetch(window.location.href, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                password: password
            })
        })

        .then(response => response.json()) // Turn incoming response to JSON format.
        .then(data => {
            if (data.status === 'success'){
                const messageDisplay = document.getElementById('errorMessage');
                
                messageDisplay.innerHTML = "Password changed correctly! <a href='/' style='color:rgb(222, 196, 241); font-weight: bold;'>Click here to login.</a>";                messageDisplay.style.color = "#43007a";
                messageDisplay.className = "flash info";


                
                // Disable the input boxes
                document.getElementById('password').disabled = true;
                document.getElementById('confirm_password').disabled = true;
                
                // Disable the submit button
                const submitButton = document.querySelector('button[type="submit"]');
                submitButton.disabled = true;
                submitButton.style.cursor = "not-allowed";
            }

            // If failed.
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
    }


})