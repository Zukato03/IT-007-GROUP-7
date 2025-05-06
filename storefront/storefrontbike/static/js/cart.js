var productapp = new Vue({
    el: '#cartapp',
    delimiters: ['[[', ']]'],
    store: store,
    data() {
        return {
            errors: [],
            first_name: userData.first_name,  
            last_name: userData.last_name,
            email: userData.email,
            contact_number: userData.contact_number,
            address: userData.address,
            zip_code: userData.zip_code,
            coupon_value: 0,
            coupon_code: '',
            showCouponCodeError: false,
            selectedProducts: [],
            products: []
        };
    },
    computed: {
        numItems: function() {
            return store.state.numItems
        },
        totalCost: function () {
            return store.state.totalCost
        },
        totalCostWithCoupon: function () {
            if (this.coupon_value > 0) {
                return store.state.totalCost * (parseInt(this.coupon_value) / 100);
            } else {
                return store.state.totalCost;
            }
        }
    },
    mounted() {
        this.fetchCartItems();
    },
    methods: {
        validateForm() {
            this.errors = []; 

            if (!this.first_name) {
                this.errors.push('First name is empty');
            }
            if (!this.last_name) {
                this.errors.push('Last name is empty');
            }
            if (!this.email) {
                this.errors.push('Email is empty');
            }
            if (!this.contact_number) {
                this.errors.push('Contact Number is empty');
            }
            if (!this.address) {
                this.errors.push('Address is empty');
            }
            if (!this.zip_code) {
                this.errors.push('Zip Code is empty');
            }

            if (this.errors.length > 0) {
                return; 
            }

            return this.errors.length;
        },
        fetchCartItems() {
            fetch('/api/cart-items/', {
                method: 'GET',
                 credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);  
                this.products = data.cart_items;

                let numItems = 0;
                let totalCost = 0;

                data.cart_items.forEach(item => {
                    numItems += item.quantity;
                    totalCost += parseFloat(item.total_price);
                });

                store.commit('setCart', {
                    numItems: numItems,
                    totalCost: totalCost.toFixed(2)
                });

                return this.products;
            })
            .catch(error => {
                console.error('Error fetching cart items:', error);
                this.products = [];
            });
        },
        applyCoupon() {
            if (this.coupon_code !== '') {
                fetch('/api/can_use/?coupon_code_get=' + this.coupon_code, {
                    method: 'GET'
                })
                .then((response) => {
                    return response.json();
                    console.log('Returned');
                })
                .then((data) => {
                    if (data.amount) {
                        this,showCouponCodeError = false
                        this.coupon_value = parseInt(data.amount)
                    } else {
                        this.coupon_value = 0
                        this.showCouponCodeError = true
                    }
                })
            } else {
                this.showCouponCodeError = true
            }
        },
        buy(paymentMethod) {
            if (this.validateForm() !== 0) {
                return; 
            }

            if (this.selectedProducts.length === 0) {
                alert('Please select at least one product to purchase.');
                return;
            }

            var data = {
                'first_name': this.first_name,
                'last_name': this.last_name,
                'email': this.email,
                'contact_number': this.contact_number,
                'address': this.address,
                'zip_code': this.zip_code,
                'coupon_code': this.coupon_code,
                'selected_products': this.selectedProducts 
            };

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            console.log(this.selectedProducts);

            if (paymentMethod === 'stripe') {
                var stripe = Stripe(stripePubKey);
                fetch('/api/create_checkout_session/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(data)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok ' + response.statusText);
                    }
                    return response.json();
                })
                .then(session => {
                    return stripe.redirectToCheckout({ sessionId: session.session.id });
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('There was an issue with the checkout process.');
                });
            } /* else if (paymentMethod === 'paymongo') {
                fetch('/api/create_checkout_session_paymongo/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(data)
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(errorData => {
                            throw new Error('Paymongo Error: ' + JSON.stringify(errorData));
                        });
                    }
                    return response.json();
                })
                .then(session => {
                    if (session.session_id) {
                        window.location.href = `https://checkout.paymongo.com/${session.session_id}`;
                    } else {
                        alert('Failed to create session with Paymongo');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('There was an issue with the checkout process: ' + error.message);
                });
            }  
            */                                
        },
        incrementQuantity(product_id, quantity, price) {
            console.log('Product_id:', product_id);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            if (quantity < this.products.find(product => product.id === product_id).number_available) {
                let data = {
                    'product_id': product_id,
                    'update': true,
                    'quantity': quantity + 1  
                };

                fetch('/api/add_to_cart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(data)
                })
                .then((response) => {
                    if (response.ok) {
                        let product = this.products.find(product => product.id === product_id);
                        product.quantity += 1;
                        product.total_price = product.quantity * parseFloat(product.price);
                        
                        store.commit('increment', 1);
                        store.commit('changeTotalCost', parseFloat(price));
                    }
                })
                .catch((error) => {
                    console.log('Error:', error);
                });
            } else {
                alert('No more available in stock');
            }
        },
        
        decrementQuantity(product_id, quantity, price) {
            console.log('Product_id:', product_id);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            if (quantity > 1) {
                let data = {
                    'product_id': product_id,
                    'update': true,
                    'quantity': quantity - 1 
                };

                fetch('/api/add_to_cart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(data)
                })
                .then((response) => {
                    if (response.ok) {
                        let product = this.products.find(product => product.id === product_id);
                        product.quantity -= 1;
                        product.total_price = product.quantity * parseFloat(product.price);
                        
                        store.commit('increment', -1);
                        store.commit('changeTotalCost', -parseFloat(price));
                    }
                })
                .catch((error) => {
                    console.log('Error:', error);
                });
            } else {
                this.removeFromCart(product_id);
            }
        },        
        removeFromCart(product_id) {
            console.log('Remove Product_id:', product_id);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            let data = {
                'product_id': product_id
            };
            
            fetch('/api/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin',
                body: JSON.stringify(data)
            })
            .then((response) => {
                if (response.ok) {
                    let removedProduct = this.products.find(product => product.id === product_id);
                    store.commit('increment', -removedProduct.quantity);
                    store.commit('changeTotalCost', -removedProduct.total_price);
        
                    this.products = this.products.filter(product => product.id !== product_id);
                }
            })
            .catch((error) => {
                console.log('Error:', error);
            });
        }  
    }
});