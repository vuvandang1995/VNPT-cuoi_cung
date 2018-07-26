$(document).ready(function(){
    $('#list_ticket_leader').DataTable({
        "columnDefs": [
            { "width": "5%", "targets": 0 },
            { "width": "15%", "targets": 1 },
            { "width": "15%", "targets": 2 },
            { "width": "15%", "targets": 3 },
            { "width": "12%", "targets": 4 },
            { "width": "10%", "targets": 5 },
            { "width": "13%", "targets": 6 },
            { "width": "13%", "targets": 7 },
        ],
        "ajax": {
            "type": "GET",
            "url": location.href +"data",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": [[ 0, "desc" ]],
        "displayLength": 25,
    });

    setTimeout(function(){
        countdowntime();
    }, 2500);

    
});