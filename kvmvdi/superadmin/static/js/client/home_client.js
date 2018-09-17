$(document).ready(function(){
    $('body .list_vm_client').each( function(){
        $(this).DataTable({
            "ajax": {
                "type": "GET",
                "url": "/client/home_data_192.168.40.146",
                "contentType": "application/json; charset=utf-8",
                "data": function(result){
                    return JSON.stringify(result);
                },
            },
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
            "displayLength": 10,
        });
    });


    
    $("body").on('click', '.delete', function(){
        var id = $(this).attr('id').split('_')[1];
        var ops = $(this).attr('name').split('_')[0];
        var svname = $(this).attr('name').split('_')[1];
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (confirm('Bạn có chắc ?')){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                success: function(){
                    setTimeout(function(){
                        $('.list_vm_client').DataTable().ajax.reload(null,false);
                    }, 4000);
                }
           });
        }
    });

    $("body").on('click', '.console', function(){
        var url = $(this).attr('id');
        window.open(url);
    });


});