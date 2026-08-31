const form = document.getElementById('election-form');

const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);

const dateInput = document.getElementById('date');
const yyyy = tomorrow.getFullYear();
const mm = String(tomorrow.getMonth() + 1).padStart(2, '0');
const dd = String(tomorrow.getDate()).padStart(2, '0');

dateInput.min = `${yyyy}-${mm}-${dd}`;

const fileInput = document.getElementById('image_input');
const preview = document.getElementById('imagePreview');

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];

        if (file && file.type.startsWith('image/')) {
         preview.src = URL.createObjectURL(file);
         preview.style.display = 'block';
    } 
    else {
      preview.src = '';
      preview.style.display = 'none';
    }
  });

  form.addEventListener('submit', async function(e) {
    e.preventDefault();

    const typeRadio = document.querySelector('input[name="type"]:checked');

    const formData = new FormData();
    formData.append('name', document.getElementById('name').value.trim());
    formData.append('description', document.getElementById('description').value.trim());
    formData.append('date', document.getElementById('date').value);
    formData.append('type', typeRadio ? typeRadio.value : '');
    if (fileInput.files[0]) {
        formData.append('picture', fileInput.files[0]);
    }

    try {
        const response = await fetch('/addElection', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if(response.ok){
            window.location.href = `/addCandidates?election_id=${result.election_id}`;
        } else {
            const errorDisplay = document.getElementById('errorMessage');
            errorDisplay.innerText = result.message;
            errorDisplay.style.color = "#c20000";
            
            setTimeout(function() {
                errorDisplay.innerText = "";
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