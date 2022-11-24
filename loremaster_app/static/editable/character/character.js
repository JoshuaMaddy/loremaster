$(function () {

    var lightbox = $('.all_images a').simpleLightbox({
        scaleImageToRatio:true,
        heightRatio:0.8
    });

    $('.main_image').on('click', function (evt) {
        lightbox.open();
    })
})