const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const popupEl = document.getElementById('popup')
const copyLinkBtnEl = document.getElementById('copy-link-btn');
const copyImgBtnEl = document.getElementById('copy-image-btn')
const shareContentEl = document.getElementById('content-to-share');
// monthNames declared in blog.html

var imgBlob = null;

// function that converts yyyymmdd to MMM (d)d, yyyy
function formatDateFromNumber(yyyymmdd) {
    const year = yyyymmdd.substring(0, 4);
    const month = yyyymmdd.substring(4, 6);
    const day = yyyymmdd.substring(6, 8);
    return `${monthNames[parseInt(month) - 1]} ${parseInt(day, 10)}, ${year}`;
}

function showPopup(el) {
    // show popup for wrapper closest to el
    // copy content of closest wrapper
    const wrapper = el.closest('.wrapper');
    console.log(el)
    shareContentEl.innerHTML = wrapper.innerHTML;
    console.log(wrapper.classList)
    if (wrapper.classList.contains('left')) {
        shareContentEl.classList.remove('right-share');
        shareContentEl.classList.add('left-share');
    } else {
        shareContentEl.classList.remove('left-share');
        shareContentEl.classList.add('right-share');
    }
    popupEl.style.display = 'block';
    // store id of closest anchor
    const anchor = el.closest('.entry').querySelector('.anchor')
    copyLinkBtnEl.setAttribute('data-anchor-id', anchor.id);
    if (isMobile) {
        copyLinkBtnEl.textContent = 'share dream';
        copyImgBtnEl.textContent = 'share image';
    } else {
        copyLinkBtnEl.textContent = 'copy link';
        copyImgBtnEl.textContent = 'copy image';
    }
    toggleCopyImgBtn(false);
    html2canvas(shareContentEl).then(canvas => {
        const croppedCanvas = document.createElement('canvas');
        const ctx = croppedCanvas.getContext('2d');
        croppedCanvas.width = canvas.width - 1;
        croppedCanvas.height = canvas.height;
        ctx.drawImage(canvas, 0, 0, croppedCanvas.width, croppedCanvas.height, 0, 0, croppedCanvas.width, croppedCanvas.height);

        croppedCanvas.toBlob(blob => {
            imgBlob = blob;
            toggleCopyImgBtn(true);
        });
    });
}

function closePopup() {
    popupEl.style.display = 'none';
    imgBlob = null;
}

function toggleCopyImgBtn(enabled) {
    if (enabled) {
        copyImgBtnEl.disabled = false;
        copyImgBtnEl.style.opacity = '1';
    } else {
        copyImgBtnEl.disabled = true;
        copyImgBtnEl.style.opacity = '0.5';
    }
}

document.querySelectorAll('.share-btn').forEach(button => {
    button.addEventListener('click', function() { showPopup(this) });
});

document.addEventListener('long-press', function(e) {
    if (window.matchMedia("(hover: none)").matches) {
        wrapper = e.target.closest('.wrapper.shareable');
        if (wrapper) showPopup(wrapper);
    }
});

document.querySelector('.close-btn').addEventListener('click', closePopup);

window.onclick = function(event) {
    if (event.target == popupEl) closePopup();
};

copyLinkBtnEl.addEventListener('click', function() {
    const entryId = this.getAttribute('data-anchor-id');
    const urlToCopy = window.location.href.split('#')[0] + '#' + entryId;
    if (!isMobile) {
        navigator.clipboard.writeText(urlToCopy).then(() => {
            this.textContent = 'link copied!';
        }).catch(err => {
            console.error('Error in copying text: ', err);
        });
        return;
    } else {
        navigator.share({
            title: 'dreamland',
            text: 'what did i dream on ' + formatDateFromNumber(entryId) + '?',
            url: urlToCopy
        }).catch(err => {
            console.error('Error in sharing text: ', err);
        })
    }
});

copyImgBtnEl.addEventListener('click', function() {
    if (imgBlob) {
        if (!isMobile) {
            const item = new ClipboardItem({ "image/png": imgBlob });
            navigator.clipboard.write([item]).then(() => {
                this.textContent = 'image copied!';
            }).catch(err => {
                console.error('Error in copying image: ', err);
            });
        } else {
            const file = new File([imgBlob], 'dream.png', { type: 'image/png' });
            navigator.share({
                files: [file]
            }).catch(err => {
                alert(err);
                console.error('Error in sharing image: ', err);
            })
        }
    }
});

/*!
 * long-press-event - v2.4.6
 * Pure JavaScript long-press-event
 * https://github.com/john-doherty/long-press-event
 * @author John Doherty <www.johndoherty.info>
 * @license MIT
 */
!function(e,t){"use strict";var n=null,a="PointerEvent"in e||e.navigator&&"msPointerEnabled"in e.navigator,i="ontouchstart"in e||navigator.MaxTouchPoints>0||navigator.msMaxTouchPoints>0,o=a?"pointerdown":i?"touchstart":"mousedown",r=a?"pointerup":i?"touchend":"mouseup",m=a?"pointermove":i?"touchmove":"mousemove",u=a?"pointerleave":i?"touchleave":"mouseleave",s=0,c=0,l=10,v=10;function f(e){p(),e=function(e){if(void 0!==e.changedTouches)return e.changedTouches[0];return e}(e),this.dispatchEvent(new CustomEvent("long-press",{bubbles:!0,cancelable:!0,detail:{clientX:e.clientX,clientY:e.clientY,offsetX:e.offsetX,offsetY:e.offsetY,pageX:e.pageX,pageY:e.pageY},clientX:e.clientX,clientY:e.clientY,offsetX:e.offsetX,offsetY:e.offsetY,pageX:e.pageX,pageY:e.pageY,screenX:e.screenX,screenY:e.screenY}))||t.addEventListener("click",function e(n){t.removeEventListener("click",e,!0),function(e){e.stopImmediatePropagation(),e.preventDefault(),e.stopPropagation()}(n)},!0)}function d(a){p(a);var i=a.target,o=parseInt(function(e,n,a){for(;e&&e!==t.documentElement;){var i=e.getAttribute(n);if(i)return i;e=e.parentNode}return a}(i,"data-long-press-delay","700"),10);n=function(t,n){if(!(e.requestAnimationFrame||e.webkitRequestAnimationFrame||e.mozRequestAnimationFrame&&e.mozCancelRequestAnimationFrame||e.oRequestAnimationFrame||e.msRequestAnimationFrame))return e.setTimeout(t,n);var a=(new Date).getTime(),i={},o=function(){(new Date).getTime()-a>=n?t.call():i.value=requestAnimFrame(o)};return i.value=requestAnimFrame(o),i}(f.bind(i,a),o)}function p(t){var a;(a=n)&&(e.cancelAnimationFrame?e.cancelAnimationFrame(a.value):e.webkitCancelAnimationFrame?e.webkitCancelAnimationFrame(a.value):e.webkitCancelRequestAnimationFrame?e.webkitCancelRequestAnimationFrame(a.value):e.mozCancelRequestAnimationFrame?e.mozCancelRequestAnimationFrame(a.value):e.oCancelRequestAnimationFrame?e.oCancelRequestAnimationFrame(a.value):e.msCancelRequestAnimationFrame?e.msCancelRequestAnimationFrame(a.value):clearTimeout(a)),n=null}"function"!=typeof e.CustomEvent&&(e.CustomEvent=function(e,n){n=n||{bubbles:!1,cancelable:!1,detail:void 0};var a=t.createEvent("CustomEvent");return a.initCustomEvent(e,n.bubbles,n.cancelable,n.detail),a},e.CustomEvent.prototype=e.Event.prototype),e.requestAnimFrame=e.requestAnimationFrame||e.webkitRequestAnimationFrame||e.mozRequestAnimationFrame||e.oRequestAnimationFrame||e.msRequestAnimationFrame||function(t){e.setTimeout(t,1e3/60)},t.addEventListener(r,p,!0),t.addEventListener(u,p,!0),t.addEventListener(m,function(e){var t=Math.abs(s-e.clientX),n=Math.abs(c-e.clientY);(t>=l||n>=v)&&p()},!0),t.addEventListener("wheel",p,!0),t.addEventListener("scroll",p,!0),t.addEventListener(o,function(e){s=e.clientX,c=e.clientY,d(e)},!0)}(window,document);
  