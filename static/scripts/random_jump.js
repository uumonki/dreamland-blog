var randomLink = document.getElementById('random-jump');
var anchors = null; // to cache the .anchor elements

randomLink.addEventListener('click', function(e) {
    e.preventDefault();

    // populate the list on the first click
    if (!anchors) anchors = document.querySelectorAll('.anchor');
    const randomIndex = Math.floor(Math.random() * anchors.length);
    window.location.hash = anchors[randomIndex].id;
});