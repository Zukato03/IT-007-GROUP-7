new Vue ({
    el: '#search',
    data : {
        isAdvancedSearch: false
    },
    methods: {
        advancedSearch() {
            this.isAdvancedSearch = true;
        },
        cancelAdvancedSearch() {
            this.isAdvancedSearch = false;
        }
    }
})