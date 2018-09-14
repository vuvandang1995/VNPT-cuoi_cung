$(document).ready(function(){
    $('body .list_vm').each( function(){
        var ops_ip = $(this).attr('name');
        $(this).DataTable({
            "ajax": {
                "type": "GET",
                "url": "/home_data_"+ops_ip,
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
        var ops = $(this).attr('name');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (confirm('Bạn có chắc ?')){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token, 'ops':ops},
                success: function(){
                    setTimeout(function(){
                        $('.list_vm').DataTable().ajax.reload(null,false);
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