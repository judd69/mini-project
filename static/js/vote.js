/**
 * SecureVote — Voting Page Interactivity
 *
 * Handles candidate selection, double-click prevention,
 * AJAX vote submission, and success modal display.
 */

let selectedCandidateId = null;
let isSubmitting = false;

/**
 * Select a candidate card. Only one can be selected at a time.
 * Triggers ripple effect and updates the submit button state.
 */
function selectCandidate(cardElement, candidateId) {
    if (isSubmitting) return;

    // Deselect all
    document.querySelectorAll('.candidate-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Select this one
    cardElement.classList.add('selected');
    selectedCandidateId = candidateId;

    // Create ripple effect
    createRipple(cardElement, event);

    // Enable submit button
    const btn = document.getElementById('submit-vote-btn');
    const btnText = document.getElementById('btn-text');
    btn.disabled = false;
    btn.classList.remove('opacity-50', 'cursor-not-allowed');
    btn.classList.add('opacity-100', 'cursor-pointer');
    btnText.textContent = 'Confirm & Cast Vote';
}

/**
 * Create a ripple animation at the click position.
 */
function createRipple(element, e) {
    // Remove old ripples
    element.querySelectorAll('.ripple').forEach(r => r.remove());

    const ripple = document.createElement('span');
    ripple.classList.add('ripple');

    const rect = element.getBoundingClientRect();
    if (e && e.clientX) {
        ripple.style.left = (e.clientX - rect.left) + 'px';
        ripple.style.top = (e.clientY - rect.top) + 'px';
    } else {
        ripple.style.left = '50%';
        ripple.style.top = '50%';
    }

    element.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
}

/**
 * Submit the vote via AJAX with double-click prevention.
 */
function submitVote() {
    if (isSubmitting || !selectedCandidateId) return;

    isSubmitting = true;

    const btn = document.getElementById('submit-vote-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');

    // Show loading state
    btn.disabled = true;
    btn.classList.add('cursor-not-allowed');
    btnText.textContent = 'Casting your vote...';
    btnSpinner.classList.remove('hidden');

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Get election ID from URL
    const pathParts = window.location.pathname.split('/');
    const electionId = pathParts[pathParts.indexOf('elections') + 1];

    // Build form data
    const formData = new FormData();
    formData.append('candidate_id', selectedCandidateId);
    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch(`/elections/${electionId}/cast/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success modal
            showSuccessModal(data);
        } else {
            // Show error
            btnText.textContent = data.error || 'Something went wrong';
            btnSpinner.classList.add('hidden');
            btn.classList.remove('cursor-not-allowed');
            btn.classList.add('bg-rose-600');

            setTimeout(() => {
                btnText.textContent = 'Confirm & Cast Vote';
                btn.classList.remove('bg-rose-600');
                btn.disabled = false;
                isSubmitting = false;
            }, 3000);
        }
    })
    .catch(error => {
        console.error('Vote submission error:', error);
        btnText.textContent = 'Network error — please retry';
        btnSpinner.classList.add('hidden');

        setTimeout(() => {
            btnText.textContent = 'Confirm & Cast Vote';
            btn.disabled = false;
            isSubmitting = false;
        }, 3000);
    });
}

/**
 * Show the success modal with vote confirmation details.
 */
function showSuccessModal(data) {
    const modal = document.getElementById('success-modal');
    const messageEl = document.getElementById('success-message');
    const hashEl = document.getElementById('ballot-hash-display');
    const redirectLink = document.getElementById('success-redirect');

    messageEl.textContent = data.message;
    hashEl.textContent = data.ballot_hash;
    redirectLink.href = data.redirect_url;

    modal.classList.remove('hidden');
    modal.classList.add('flex');

    // Auto-redirect after 5 seconds
    setTimeout(() => {
        window.location.href = data.redirect_url;
    }, 5000);
}
