function showPage(pageId) {
    const pages = document.querySelectorAll('.page');

    pages.forEach(page => {
        page.classList.remove('active');
    });

    document.getElementById(pageId).classList.add('active');
}
// Hier kommt später dein JavaScript hinein.
console.log("Menü geladen");