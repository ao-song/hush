document.addEventListener('DOMContentLoaded', () => {
    const secretInput = document.getElementById('secret-input');
    const generateLinkBtn = document.getElementById('generate-link-btn');
    const linkOutput = document.getElementById('link-output');
    const shareLinkInput = document.getElementById('share-link');
    const copyLinkBtn = document.getElementById('copy-link-btn');
    const messageElement = document.getElementById('message');
    const createSecretSection = document.getElementById('create-secret-section');
    const viewSecretSection = document.getElementById('view-secret-section');
    const copySecretBtn = document.getElementById('copy-secret-btn');
    const displayedSecret = document.getElementById('displayed-secret');
    const viewMessage = document.getElementById('view-message');

    const backendBaseUrl = ''; // Nginx will proxy requests

    // Function to show messages
    function showMessage(msg, isError = true) {
        messageElement.textContent = msg;
        messageElement.className = isError ? 'error' : 'success';
        messageElement.classList.remove('hidden');
    }

    // Handle generating a new secret link
    if (generateLinkBtn) {
        generateLinkBtn.addEventListener('click', async () => {
            const secret = secretInput.value;
            if (!secret) {
                showMessage('Please enter a secret.');
                return;
            }

            try {
                const response = await fetch(`${backendBaseUrl}/api/create_secret/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ secret: secret }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                const fullLink = `${window.location.origin}${data.link}`;
                shareLinkInput.value = fullLink;
                linkOutput.classList.remove('hidden');
                messageElement.classList.add('hidden'); // Hide previous messages
            } catch (error) {
                console.error('Error creating secret:', error);
                showMessage('Failed to create secret. Please try again.');
            }
        });
    }

    // Handle copying the link to clipboard
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(shareLinkInput.value);
                showMessage('Link copied to clipboard!', false);
            } catch (err) {
                console.error('Failed to copy link: ', err);
                showMessage('Failed to copy link.');
            } finally {
                setTimeout(() => messageElement.classList.add('hidden'), 3000);
            }
        });
    }

    // Handle viewing a secret from a shared link
    const path = window.location.pathname;
    if (path.startsWith('/secret/')) {
        const uniqueId = path.split('/')[2];
        if (uniqueId) {
            createSecretSection.classList.add('hidden');
            viewSecretSection.classList.remove('hidden');

            fetch(`${backendBaseUrl}/api/secret/${uniqueId}`)
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw new Error(err.detail || 'Failed to retrieve secret.'); });
                    }
                    return response.json();
                })
                .then(data => {
                    displayedSecret.textContent = data.secret;
                    copySecretBtn.classList.remove('hidden'); // Show the copy button
                    viewMessage.textContent = 'Secret retrieved successfully!';
                    viewMessage.style.color = '#28a745'; // Green
                })
                .catch(error => {
                    console.error('Error retrieving secret:', error);
                    displayedSecret.textContent = 'N/A';
                    copySecretBtn.classList.add('hidden'); // Hide copy button on error
                    viewMessage.textContent = error.message || 'Failed to retrieve secret. It might be expired or already viewed.';
                    viewMessage.style.color = '#dc3545'; // Red
                });
        }
    }

    // Handle copying the retrieved secret
    if (copySecretBtn) {
        copySecretBtn.addEventListener('click', async () => {
            const secret = displayedSecret.textContent;
            await navigator.clipboard.writeText(secret);
            viewMessage.textContent = 'Secret copied to clipboard!';
            setTimeout(() => { viewMessage.textContent = 'Secret retrieved successfully!'; }, 3000);
        });
    }
});
