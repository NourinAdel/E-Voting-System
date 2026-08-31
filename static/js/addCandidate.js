const form = document.getElementById("candidate-form");
const originalFieldset = document.getElementById("fieldset");
const addAnotherBtn = document.getElementById("addAnother");
let candidateCount = 1;
const maxCandidates = 5;

// Function to handle preview for any file input
function setupImagePreview(fieldset) {
    const fileInp = fieldset.querySelector('input[type="file"]');
    const imgPrev = fieldset.querySelector('img');
    const placeholder = fieldset.querySelector('.placeholder-text');

    if (fileInp && imgPrev) {
        fileInp.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                imgPrev.src = URL.createObjectURL(file);
                imgPrev.style.display = 'block';
                if (placeholder) placeholder.style.display = 'none';
            }
        });
    }
}

// Initialize preview on original fieldset
setupImagePreview(originalFieldset);

addAnotherBtn.addEventListener("click", () => {
    if (candidateCount < maxCandidates) {
        candidateCount++;

        const newFieldset = originalFieldset.cloneNode(true);
        newFieldset.removeAttribute("id");
        newFieldset.querySelector("legend").textContent = `Candidate ${candidateCount}`;

        // Reset values; maintain name="names[]", name="descriptions[]", name="images[]"
        newFieldset.querySelectorAll("input[type='text'], textarea").forEach((input) => {
            input.value = "";
        });

        const fileInput = newFieldset.querySelector("input[type='file']");
        if (fileInput) fileInput.value = "";

        const imgPreview = newFieldset.querySelector("img");
        const placeholder = newFieldset.querySelector(".placeholder-text");
        if (imgPreview) {
            imgPreview.src = "";
            imgPreview.style.display = "none";
        }
        if (placeholder) placeholder.style.display = "inline";

        setupImagePreview(newFieldset);
        form.insertBefore(newFieldset, addAnotherBtn);
    } else {
        alert("You can add up to 5 candidates only.");
    }
});

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fieldsets = form.querySelectorAll("fieldset");
    if (fieldsets.length < 2 || fieldsets.length > 5) {
        alert("You must provide between 2 and 5 candidates.");
        return;
    }

    const formData = new FormData(form);

    const urlParams = new URLSearchParams(window.location.search);
    const electionId = urlParams.get('election_id');

    if (!electionId) {
        alert("Missing Election ID in the URL. Please create an election first.");
        return;
    }

    if (!formData.get('election_id') && electionId) {
        formData.append('election_id', electionId);
    }

    try {
        const response = await fetch("/addCandidates", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            window.location.href = "/adminDashboard";
        } else {
            alert(result.error || "Failed to submit candidates.");
        }
    } catch (error) {
        console.error("Error submitting form:", error);
        alert("A network error occurred. Please try again.");
    }
});