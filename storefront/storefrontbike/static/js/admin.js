document.addEventListener('DOMContentLoaded', function() {
    $('input[type="month"]').datepicker({
        dateFormat: 'yy-mm',
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true,
    });
});

