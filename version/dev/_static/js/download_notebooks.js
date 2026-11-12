document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('a[href$=".ipynb"]').forEach(function (link) {
        link.setAttribute("download", "");
    });
});
