$(document).ready(function(){
    var table = $('#list_ticket_home').DataTable({
        "columnDefs": [
//                    { "width": "2%", "targets": 0 },
//                    { "width": "12%", "targets": 1 },
//                    { "width": "12%", "targets": 2 },
//                    { "width": "12%", "targets": 3 },
//                    { "width": "14%", "targets": 4 },
//                    { "width": "6%", "targets": 5 },
//                    { "width": "8%", "targets": 6 },
//                    { "width": "8%", "targets": 7 },
//                    { "width": "8%", "targets": 8 },
//                    { "width": "6%", "targets": 9 },
//                    { "width": "12%", "targets": 10 },
                    { "width": "12%", "targets": 11 },
                ],
        "ajax": {
            "type": "GET",
            "url": location.href +"data",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            },
            "complete": function(){
                setTimeout(function(){
                    countdowntime();
                }, 1000);
            }
        },
        'dom': 'Rlfrtip',
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": [[ 0, "desc" ]],
        "displayLength": 25,
    });
    $('[data-toggle="tooltip"]').tooltip();
    $("body").on('click', '.assign_ticket', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if(confirm("Are you sure ?")){
            var userName = $('#user_name'+id).val();
            var chatSocket1 = new WebSocket(
                'ws://' + window.location.host +
                '/ws/user/' + userName + '/');

            var date = formatAMPM(new Date());
            message = 'Yêu cầu số '+id+' đang được xử lý!';
            chatSocket1.onopen = function (event) {
                chatSocket1.send(JSON.stringify({
                    'message' : message,
                    'time' : date,
                }));
            };

            group_agent_Socket.send(JSON.stringify({
                'message' : 'ticket da duoc xu ly',
                'time' : date,
            }));

            $.ajax({
                type:'POST',
                url:location.href,
                data: {'tkid':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    $("#list_ticket_home").DataTable().ajax.reload();
//                    chatSocket1.close();
                }
            });
        }
    });
});