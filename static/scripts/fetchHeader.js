//Gets the header.html and loads it each time i call this script to each link. 
//It's better than writing the header which is like 20 lines long each time. With this I just call the JS file as one line
//and I'm good

fetch('~/templates/headerNav.html')
    .then(response => response.text())
    .then(html => { 
        document.querySelector('body').insertAdjacentHTML('afterbegin', html);
});