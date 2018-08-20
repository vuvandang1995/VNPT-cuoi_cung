$(document).ready(function(){
    $('#list_user').DataTable({
        "columnDefs": [
            { "width": "5%", "targets": 0 },
            { "width": "20%", "targets": 1 },
            { "width": "18%", "targets": 2 },
            { "width": "10%", "targets": 3 },
            { "width": "12%", "targets": 4 },
            { "width": "20%", "targets": 5 },
            { "width": "15%", "targets": 6 },
        ],
        "ajax": {
            "type": "GET",
            "url": location.href +"/data",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": [[ 0, "desc" ]],
        "displayLength": 25,
    });
    $("#info_user").on('click', '.unblock', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if(confirm("Are you sure ?")){
             $.ajax({
                 type:'POST',
                 url:location.href,
                 data: {'agid':id, 'csrfmiddlewaretoken':token, 'stt': 1},
                 success: function(){
                    $('#list_user').DataTable().ajax.reload()
                 }
             });
        }
    });
    $("#info_user").on('click', '.block', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if(confirm("Are you sure ?")){
             $.ajax({
                 type:'POST',
                 url:location.href,
                 data: {'agid':id, 'csrfmiddlewaretoken':token, 'stt': 0},
                 success: function(){
                    $('#list_user').DataTable().ajax.reload(null,false);
                 }
             });
        }
    });

    $('body #info_user').on('change', '.position', function() {
        var position = parseInt($(this).val());
        var id = $(this).attr('name');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if(confirm("Are you sure ?")){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'csrfmiddlewaretoken':token, 'position': position, 'agid':id},
                success: function(){
                    $('#list_user').DataTable().ajax.reload()
                }
            });
        }else{
            $('#list_user').DataTable().ajax.reload()
        }
    });
});