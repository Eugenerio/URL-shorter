// static/main.js

document.addEventListener('DOMContentLoaded', () => {
    const cleanHistoryBtn = document.getElementById('clean-history-btn');
    if (cleanHistoryBtn) {
        cleanHistoryBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to clean the history? This action cannot be undone.')) {
                cleanHistory();
            }
        });
    }

    function cleanHistory() {
        fetch('/clean-history', {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('An error occurred while cleaning the history.');
            }
        })
        .catch(error => {
            console.error(error);
            alert('An error occurred while cleaning the history.');
        });
    }
});
