document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const age = parseInt(document.getElementById('age').value, 10);

    if (isNaN(age) || age < 13) {
        const errorDisplay = document.getElementById('errorMessage');
        errorDisplay.innerText = 'You must be at least 13 years old to register.';
        errorDisplay.style.color = "#c20000";
            
            setTimeout(function() {
                errorDisplay.innerText = ""; // Erases the text after 5 seconds.
            }, 5000);
        return;
    }

    const genderSelected = document.querySelector('input[name="gender"]:checked');

    const formData = {
        username: document.getElementById('username').value.trim(),
        password: document.getElementById('password').value,
        dob: document.getElementById('DOB').value,
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('telephone').value.trim(),
        gender: genderSelected ? genderSelected.value : ''

    };

    try {
        const response = await fetch('/api/signUp', {
            method: 'POST',
            headers: {'Content-Type' : 'application/json'},
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if(response.ok){
            window.location.href = '/login';
        } else {
            const errorDisplay = document.getElementById('errorMessage');
            errorDisplay.innerText = result.message;
            errorDisplay.style.color = "#c20000";
            
            setTimeout(function() {
                errorDisplay.innerText = ""; // Erases the text after 5 seconds.
            }, 5000);
        }
    } catch(error){
        const errorDisplay = document.getElementById('errorMessage');
            errorDisplay.innerText = 'Unable to connect to the server. Please try again.';
            errorDisplay.style.color = "#c20000";
            
            setTimeout(function() {
                errorDisplay.innerText = "";
            }, 5000);
    }
});


document.addEventListener('DOMContentLoaded', function() {
    const dobInput = document.getElementById('DOB');
    const ageInput = document.getElementById('age');

    function calculateAndSetAge() {
        if (!dobInput.value) {
            ageInput.value = '';
            return;
        }

        const [year, month, day] = dobInput.value.split('-').map(Number);
        const today = new Date();
        
        let age = today.getFullYear() - year;
        const monthDiff = today.getMonth() - (month - 1);

        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < day)) {
            age--;
        }

        ageInput.value = age >= 0 ? age : '';
        console.log("Calculated Age:", ageInput.value); // Debug log
    }

    dobInput.addEventListener('input', calculateAndSetAge);
    dobInput.addEventListener('change', calculateAndSetAge);
});