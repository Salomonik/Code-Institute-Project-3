document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.materialboxed');
    M.Materialbox.init(elems);

    var carouselElems = document.querySelectorAll('.carousel');
    M.Carousel.init(carouselElems, {
        fullWidth: true,
        indicators: true
    });
});
