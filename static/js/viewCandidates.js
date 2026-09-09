document.addEventListener("DOMContentLoaded", () => {
const voteModal = document.getElementById("vote_modal");
const modalNameSpan = document.getElementById("modal-candidate-name");

voteYesBtn = document.getElementById("voteYesBtn");
voteNoBtn = document.getElementById("voteNoBtn");

const dialog = document.getElementById("modal");
    const logoutBtn = document.getElementById("logoutBtn");
    const yesBtn = document.getElementById("yesBtn");
    const noBtn = document.getElementById("noBtn");

const voteButtons = document.querySelectorAll(".cast-vote-btn");

let selectedCandidateId = null;
let selectedElectionId = null;

voteButtons.forEach(button => {

    button.addEventListener("click", () => {
        const candidateName = button.getAttribute("data-candidate-name");
        selectedElectionId = button.getAttribute("data-election-id");
        selectedCandidateId = button.getAttribute("data-candidate-id");

        modalNameSpan.textContent = candidateName;
        voteModal.showModal();
    }
    );
    });

    if (voteNoBtn){
        voteNoBtn.addEventListener("click", () => {
            voteModal.close();
            selectedCandidateId = null;
            selectedElectionId = null;
        });
    }

    if (voteYesBtn){
        voteYesBtn.addEventListener("click", () => {
        const array = new Uint8Array(16);
        window.crypto.getRandomValues(array);
        const salt = Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');

        // Candidate ID, divider, salt.
        const unencryptedPayload = selectedCandidateId + "|" + salt;
        const commitmentHash = CryptoJS.SHA256(unencryptedPayload).toString();

        const publicKey = document.getElementById("serverPublicKey").value;

        const encryptor = new JSEncrypt();
        encryptor.setPublicKey(publicKey);

        const encryptedPayload = encryptor.encrypt(unencryptedPayload);

            // Package the data into a JSON object
            const voteData = {
                election_id: selectedElectionId,
                commitment_hash: commitmentHash,
                encrypted_payload: encryptedPayload
            };

            // Send the package to Flask backend
            fetch("/cast_vote", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(voteData)
            })
            .then(response => response.json())
            .then(data => {
                console.log("Server responded:", data);
                alert("Your vote has been securely sealed and submitted!");
                
                // Close the modal
                voteModal.close();

                voteButtons.forEach(btn => {
                    const parentDiv = btn.parentElement;
                    btn.remove();
                    const msg = document.createElement("p");
                    msg.textContent = "Vote Cast";
                    msg.style.color = "green";
                    parentDiv.appendChild(msg);
                });

                selectedCandidateId = null;
                selectedElectionId = null;
                

            })
            .catch(error => {
                console.error("Error sending vote:", error);
            });

    });
    }
    
    if (logoutBtn && dialog) {
        logoutBtn.addEventListener("click", async () => {
            dialog.showModal();
        });

        yesBtn.addEventListener("click", async () => {
            try {
                const response = await fetch('/logout', {
                method: 'POST'
            });

            if (response.ok) {
                window.location.href = '/login';
            } 
            else {
                alert('Logout failed. Please try again.');
            }
            } catch (error) {
                console.error('Logout error:', error);
                window.location.href = '/logout';
            }

        });

        noBtn.addEventListener("click", () => {
            dialog.close();
        });
    }
});
