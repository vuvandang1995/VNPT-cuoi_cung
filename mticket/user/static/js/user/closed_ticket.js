$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
    $('#list_closed_ticket').DataTable({
//        "columnDefs": [
//            { "width": "5%", "targets": 0 },
//            { "width": "20%", "targets": 1 },
//            { "width": "15%", "targets": 2 },
//            { "width": "10%", "targets": 3 },
//            { "width": "12%", "targets": 4 },
//            { "width": "10%", "targets": 5 },
//        ],
        "ajax": {
            "type": "GET",
            "url": location.href +"_data",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": [[ 0, "desc" ]],
    });
});