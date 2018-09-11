$(document).ready(function(){
    var table_teacher = $('#list_vm').DataTable({
        "ajax": {
            "type": "GET",
            "url": "/home_data",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            },
        },
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "displayLength": 10,
    });


    
    $("#list_vm").on('click', '.btn-danger', function(){
        var id = $(this).attr('id').split('_')[1];
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (confirm('Bạn có chắc ?')){
        //     $.ajax({
        //         type:'POST',
        //         url:location.href,
        //         data: {'delete':id, 'csrfmiddlewaretoken':token},
        //         success: function(){
        //             $('#list_teacher').DataTable().ajax.reload(null,false);
        //         }
        //    });
        }
    });


});