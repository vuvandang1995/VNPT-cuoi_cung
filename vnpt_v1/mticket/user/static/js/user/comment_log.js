$(document).ready(function(){
    var table_comment = $('#list_comment').DataTable({
        "columnDefs": [
                    { "width": "15%", "targets": 0 },
                    { "width": "10%", "targets": 1 },
                    { "width": "20%", "targets": 2 },
                    { "width": "55%", "targets": 3 },
                ],
        "ajax": {
            "type": "GET",
            "url": "/user/comment_data_all",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            },
        },
        'dom': 'Rlfrtip',
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": [[ 0, "desc" ]],
        "displayLength": 25,
    });
});
