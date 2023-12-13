function formatDate(date) {
    let day = date.getDate();
    let monthIndex = date.getMonth();
    let year = date.getFullYear();
    return `${monthNames[monthIndex]} ${day}, ${year}`;
}

let date = new Date();
let today = formatDate(date);
let todayEls = document.querySelectorAll('.today');
todayEls.forEach(function(elem) {
    elem.textContent = today;
});

date.setDate(date.getDate() + 1)
let tomorrow = formatDate(date);
let tomorrowEls = document.querySelectorAll('.tomorrow');
tomorrowEls.forEach(function(elem) {
    elem.textContent = tomorrow;
});      