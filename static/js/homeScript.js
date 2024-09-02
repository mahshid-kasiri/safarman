window.onload = function() {
    scrollToDiv(document.getElementById("myDiv"), 1500);
};

function scrollToDiv(element, duration) {
    var start = window.pageYOffset;
    var end = element.getBoundingClientRect().top + start;
    var distance = end - start;
    var startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        var timeElapsed = currentTime - startTime;
        var run = ease(timeElapsed, start, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }

    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }

    requestAnimationFrame(animation);
}