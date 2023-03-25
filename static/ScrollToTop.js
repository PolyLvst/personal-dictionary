// $(window).on('scroll', function() {
// //   scrollFunction();
// });

// function scrollFunction() {
//     if ($(window).scrollTop() > 30) {
//         $("#btn-back-to-top").show();
//     } else {
//         $("#btn-back-to-top").hide();
//     }
// }
// When the user clicks on the button, scroll to the top of the document

function backToTop() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}