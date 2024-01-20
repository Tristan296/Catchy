//This transforms the button to a search bar supported by CSS
document.addEventListener('DOMContentLoaded', function () {
    const searchButton = document.getElementById('searchButton');
    const searchBar = document.getElementById('searchBar');
    const searchButtonSubmit = document.getElementById('searchButtonSubmit');
    const backButton = document.getElementById('backButton');

    backButton.addEventListener("click", function () {
        searchButton.classList.toggle('active');
        searchBar.classList.toggle('active', false);
        searchButtonSubmit.classList.toggle('active', false);
        backButton.classList.toggle('active', false);
        

    });

    searchButton.addEventListener('click', function () {
        // Toggle active class to switch between button and search bar
        searchButton.classList.toggle('active');
        searchBar.classList.toggle('active');
        searchButtonSubmit.classList.toggle('active');
        backButton.classList.toggle('active');

        if (searchBar.classList.contains('active')) {
            searchBar.focus(); // Focus on the input field for immediate typing
        }
        
    });

    searchBar.addEventListener('keypress', function (e) {
        // Check if Enter key is pressed to perform the search
        if (e.key === 'Enter') {
            alert('Performing search: ' + searchBar.value);
            searchBar.value = ''; // Clear the input field after search
        }
    });
});