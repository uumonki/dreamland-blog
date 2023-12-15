const monthNames = ["jan", "feb", "mar", "apr", "may", "june", "july", "aug", "sept", "oct", "nov", "dec"];

function formatDate(date) {
    let day = date.getDate();
    let monthIndex = date.getMonth();
    let year = date.getFullYear();
    return `${monthNames[monthIndex]} ${day}, ${year}`;
}

// function that converts yyyymmdd to MMM (d)d, yyyy
function formatDateFromNumber(yyyymmdd) {
    const year = yyyymmdd.substring(0, 4);
    const month = yyyymmdd.substring(4, 6);
    const day = yyyymmdd.substring(6, 8);
    return `${monthNames[parseInt(month) - 1]} ${parseInt(day, 10)}, ${year}`;
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