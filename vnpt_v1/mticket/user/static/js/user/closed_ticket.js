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

    var table_comment = $('#list_comment').DataTable({
        "columnDefs": [
                    { "width": "15%", "targets": 0 },
                    { "width": "20%", "targets": 1 },
                    { "width": "65%", "targets": 2 },
                ],
        "ajax": {
            "type": "GET",
            "url": "/user/comment_data_0",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            },
        },
        'dom': 'Rlfrtip',
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": [[ 0, "asc" ]],
        "displayLength": 25,
    });

    $("#all_note").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var id = button.attr('id');
        var type = button.data('title');
        $("#all_note input[name=type]").val(type);
        $("#title_comment").text("Ghi chú yêu cầu số "+id);
        $("#comment_ticketid").val(id);
        $('#list_comment').DataTable().ajax.url("/user/comment_data_"+id).load();
        $('#list_comment').DataTable().ajax.reload(null,false);
        $("#new_text").hide();

    });
});