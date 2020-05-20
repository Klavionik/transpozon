const addToCartURL = document.location.origin + '/cart/add/';

$('#main').on('click', '#addToCart', function () {
    const $element = $(this);
    const productID = $element.data('productId');
    addToCart(productID, $element)
});

function addToCart(productID, $element) {
    $.ajax(addToCartURL + productID,
        {
            type: "GET",
            dataType: 'json',
            success: function (response) {
                console.log('Done!', response);
                $element.popover({
                    content: response.message,
                    placement: 'top',
                    trigger: 'focus'
                });
                $element.popover('show')
            }
        }
    )
}
