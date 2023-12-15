function toggleAuthorization(userId, newState) {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/update-authorization", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE) {
            if (this.status !== 200) {
                window.location.reload();  // Reload the page on error
            }
        }
    }
    xhr.send(JSON.stringify({userId: userId, newState: newState}));
}