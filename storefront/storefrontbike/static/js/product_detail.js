var productapp = new Vue({
    el: '#productapp',
    delimiters: ['[[', ']]'],
    data () {
        return {
            showMessage: false,
            mainImage: mainImageProductDetail,
            images : imagesProductDetail
        }
    },
    mounted(){
        console.log('Vue instance mounted for cart');
    },
    methods: {
        changeMainImage (image) {
            this.mainImage = image;
        },
        addToCart(product_id) {
            console.log('Product_id:', product_id);

            var data = {
                'product_id': product_id, 
                'update': false,
                'quantity': 1
            };

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/api/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin',
                body: JSON.stringify(data)
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    this.showMessage = true;
                    store.commit('increment', 1);

                    setTimeout(() => {
                        this.showMessage = false;
                    }, 2000);
                } else {
                    alert(data.error || 'Error adding to cart');
                }
            })
            .catch(function (error) {
                console.log('Error:', error);
            });
        }
    }
});