var store = new Vuex.Store({
    state: {
        numItems: numItemsBase,
        totalCost: totalCostBase
    },
    mutations: {
        increment(state, quantity) {
            state.numItems += quantity;
        },
        changeTotalCost(state, newCost) {
            state.totalCost += parseFloat(newCost);
        },
        setCart(state, payload) {
            state.numItems = payload.numItems;
            state.totalCost = parseFloat(payload.totalCost);
        }
    }
});

var navbarapp = new Vue({
    el: '#navbarapp',
    delimiters: ['[[', ']]'],
    store: store,
    data () {
        return {
            menuClass: false,
            isDropdownActive: {}  
        };
    },
    computed: {
        numItems: function() {
            return store.state.numItems;
        }
    },
    methods: {
        toggleMenu() {
            this.menuClass = !this.menuClass;
        },
    }
});


