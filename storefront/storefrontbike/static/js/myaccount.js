new Vue({
    el: '#account-info',
    data: {
        isEditing: false,
        user: userDetails,
        showSuccess: false,
        showErrorPassword: false,
    }, 
    methods: {
        editInfo() {
            this.isEditing = true;
        },
        cancelEdit() {
            this.isEditing = false;
        },
        async updateInfo() {
            var data = {
                'first_name': this.user.first_name,
                'last_name': this.user.last_name,
                'email': this.user.email,
                'username': this.user.username,
                'contact_number': this.user.userprofile.contact_number,
                'address': this.user.userprofile.address,
                'zip_code': this.user.userprofile.zip_code,    
                'password1': this.user.password1,
                'password2': this.user.password2
            };

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            console.log('User details updating...');
            if (data.password1 !== data.password2) {
                this.showErrorPassword = true;
            } else {
                const response = await fetch(fetch_updated_data, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(data)
                });
                if (response.ok) {
                    this.isEditing = false;
                    this.showSuccess = true;

                    setTimeout(() => {
                        this.showSuccess = false;
                        window.location.reload();
                    }, 2000);
                } else {
                    console.error("Failed to update user info");
                }
            }
        },
        /*
        loadMapScript() {
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key={{ google_api_key }}&callback=initMap`;
            script.async = true;
            script.defer = true;
            document.body.appendChild(script);
        },

        initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                center: { lat: 37.7749, lng: -122.4194 },
                zoom: 8,
            });

            this.setInitialLocation(map);

            map.addListener("click", async (mapsMouseEvent) => {
                const latLng = mapsMouseEvent.latLng.toJSON();
                const address = await this.getAddressFromCoordinates(latLng.lat, latLng.lng);
                if (address) {
                    this.user.userprofile.address = address;  
                }
            });
        },
        async getAddressFromCoordinates(lat, lng) {
            const geocoder = new google.maps.Geocoder();
            const latLng = { lat: parseFloat(lat), lng: parseFloat(lng) };

            return new Promise((resolve, reject) => {
                geocoder.geocode({ location: latLng }, (results, status) => {
                    if (status === 'OK' && results[0]) {
                        resolve(results[0].formatted_address);
                    } else {
                        reject('Failed to fetch address');
                    }
                });
            });
        },
        setInitialLocation(map) {
            if (this.user.userprofile.address) {
                const geocoder = new google.maps.Geocoder();
                geocoder.geocode({ address: this.user.userprofile.address }, (results, status) => {
                    if (status === 'OK' && results[0]) {
                        map.setCenter(results[0].geometry.location);
                        new google.maps.Marker({
                            map,
                            position: results[0].geometry.location,
                        });
                    } else {
                        console.error('Geocode failed: ' + status);
                    }
                });
            }
        }
    }, 
    mounted() {
        this.loadMapScript();
    }
        */
}
});

