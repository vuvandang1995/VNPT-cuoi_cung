$(document).ready(function(){
    $('body .tk_table').each( function(){
        var topicname = $(this).attr('id').split('__')[1];
        $(this).DataTable({
            "columnDefs": [
                { "width": "5%", "targets": 0 },
                { "width": "12%", "targets": 1 },
                { "width": "10%", "targets": 2 },
                { "width": "10%", "targets": 3 },
                { "width": "8%", "targets": 4 },
                { "width": "11%", "targets": 5 },
                { "width": "8%", "targets": 6 },
                { "width": "8%", "targets": 7 },
                { "width": "10%", "targets": 8 },
            ],
            "ajax": {
                "type": "GET",
                "url": location.href +"data/" + topicname,
                "contentType": "application/json; charset=utf-8",
                "data": function(result){
                    return JSON.stringify(result);
                }
            },
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
            "order": [[ 0, "desc" ]],
            "displayLength": 25,
            'dom': 'Rlfrtip',
        });
        
    });
    

    $('body').on('click', '.btn-primary', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var r = confirm('Bạn có chắc ?');
        var array = $('#hd'+id).html().split("<br>");
        var stt = $('#leader'+id).html();
        var date = formatAMPM(new Date());
        var array2 = [];
        for (j = 0; j < array.length-1; j++) {
            array2.push(array[j].replace(/\s/g,''));
        }
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'close':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    $('.tk_table').DataTable().ajax.reload();
                    if (stt != 'Đóng'){
                        array2.push('admin_close_ticket');
                        array2.push(id);
                        var sender = $('#sender'+id).html();
                        group_agent_Socket.send(JSON.stringify({
                            'message' : array2,
                            'time' : date,
                        }));

                        if (stt == 'Chờ'){
                            var topic = $("#tp"+id).html();
                            group_agent_Socket.send(JSON.stringify({
                                'message' : 'tải lại trang đi!'+topic,
                                'time' : date,
                            }));
                        }

                        var Socket1 = new WebSocket(
                        'ws://' + window.location.host +
                        '/ws/user/' + sender + '/');

                        message = 'Yêu cầu số '+id+' đã được đóng bởi Admin!'
                        Socket1.onopen = function (event) {
                            setTimeout(function(){
                                Socket1.send(JSON.stringify({
                                    'message' : message,
                                    'time' : date,
                                }));
                                Socket1.close();
                            }, 1000);
                        };
                    }else{
                        array2.push('admin_open_ticket');
                        array2.push(id);
                        group_agent_Socket.send(JSON.stringify({
                            'message' : array2,
                            'time' : date,
                        }));

                        var topic = $("#tp"+id).html();
                        group_agent_Socket.send(JSON.stringify({
                            'message' : 'tải lại trang đi!'+topic,
                            'time' : date,
                        }));
                        var sender = $('#sender'+id).html();
                        var Socket1 = new WebSocket(
                        'ws://' + window.location.host +
                        '/ws/user/' + sender + '/');

                        message = 'Yêu cầu số '+id+' đang được xử lý bởi Admin!'
                        Socket1.onopen = function (event) {
                            setTimeout(function(){
                                Socket1.send(JSON.stringify({
                                    'message' : message,
                                    'time' : date,
                                }));
                                Socket1.close();
                            }, 1000);
                        };
                    }
                }
            });
        }
    });

    $("body").on('click', '.btn-danger', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var array = $('#hd'+id).html().split("<br>");
        var array2 = [];
        for (j = 0; j < array.length-1; j++) {
            array2.push(array[j].replace(/\s/g,''));
        }
        var date = formatAMPM(new Date());
        var r = confirm('Bạn có chắc ??');
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    // window.location.reload();
                    array2.push('admin_delete_ticket');
                    array2.push(id);
                    group_agent_Socket.send(JSON.stringify({
                        'message' : array2,
                        'time' : date,
                    }));

                    $('.tk_table').DataTable().ajax.reload();
                    var sender = $('#sender'+id).html();
                    var Socket1 = new WebSocket(
                    'ws://' + window.location.host +
                    '/ws/user/' + sender + '/');

                    message = 'Yêu cầu số '+id+' bị xóa bởi Admin!'
                    Socket1.onopen = function (event) {
                        setTimeout(function(){
                            Socket1.send(JSON.stringify({
                                'message' : message,
                                'time' : date,
                            }));
                            Socket1.close();
                        }, 1000);
                    };
                }
            });
        }
    });


    $(".forward_ticket").click(function(){
        $('.loading').show();
        $(this).prop('disabled', true);
        $(".inputText").prop('disabled', true);
        //$(".closefd").prop('disabled', true);
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var id = $("input[name=ticketid]").val();
        var list_agent = [];
        var date = formatAMPM(new Date());
        $('#forward_modal input:checkbox').each(function() {
            if ($(this).is(":checked")){
                list_agent.push(this.name);
            }
        });
        $.ajax({
            type:'POST',
            url:location.href,
            data: {'list_agent[]': JSON.stringify(list_agent),'csrfmiddlewaretoken':token, 'ticketid': id},
            success: function(){
                document.getElementById("forward_ticket_close").click();
                $('.tk_table').DataTable().ajax.reload();
                list_agent.push('leader_forward');
                list_agent.push(id);
                group_agent_Socket.send(JSON.stringify({
                    'message' : list_agent,
                    'time' : date,
                }));
                $(".loading").hide();
                $(".forward_ticket").prop('disabled', false);
                $(".inputText").prop('disabled', false);
                $(".closefd").prop('disabled', false);
                var sender = $('#sender'+id).html();
                var Socket1 = new WebSocket(
                'ws://' + window.location.host +
                '/ws/user/' + sender + '/');

                message = 'Yêu cầu số '+id+' đã được Admin xử lý!'
                Socket1.onopen = function (event) {
                    setTimeout(function(){
                        Socket1.send(JSON.stringify({
                            'message' : message,
                            'time' : date,
                        }));
                        Socket1.close();
                    }, 1000);
                };
            }
        });
    });



    $('#forward_modal').on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var ticketid = button.attr('id');
        var topic = $("#tp"+ticketid).text();
        $('.tpic').each(function() {
            var dm = $(this).children('input').val();
            if (dm == topic){
                $(this).show();
            }else{
                $(this).hide();
            }
        });
        $("input[name=ticketid]").val(ticketid);
        var array = $('#hd'+ticketid).html().split("<br>");
        var list_agent = [];
        $('#forward_modal input:checkbox').each(function() {
            list_agent.push(this.name);
            $(this).prop('checked', false);
        });
        for (i = 0; i < array.length-1; i++) {
            var value = $.inArray(array[i].replace(/\s/g,''), list_agent)
            if (value > -1){
                $('input[name='+array[i].replace(/\s/g,'')+']').prop('checked', true);
            }
        }

    });

    $('#change_modal').on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var ticketid = button.attr('id');
        $("input[name=ticketid]").val(ticketid);
        var topic = $("input[name=topicc"+ticketid+"]").val();
        $("#mySelect").val(topic);
    });

    $(".change_topic").click(function(){
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var id = $("input[name=ticketid]").val();
        var topicid = $("#mySelect").val();
        var topic_old = $("#tp"+id).text();
        var topic_name = $("#mySelect").find('option:selected').attr("name");
        var date = formatAMPM(new Date());
        if (topic_old == topic_name){
            document.getElementById("change_topic_close").click();
        }else{
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'csrfmiddlewaretoken':token, 'ticketid_change': id, 'topicid':topicid},
                success: function(){
                    document.getElementById("change_topic_close").click();
                    $('.tk_table').DataTable().ajax.reload();
                    
                    var message1 = '';
                    var message2 = '';
                    message1 = 'Bạn có một yêu cầu mới!'+topic_name;
                    group_agent_Socket.send(JSON.stringify({
                        'message' : message1,
                        'time' : date
                    }));

                    message2 = 'Yêu cầu số  ' + id + ' đã được chuyển sang chủ đề  '+ topic_name + '!' +topic_old;
                    group_agent_Socket.send(JSON.stringify({
                        'message' : message2,
                        'time' : date
                    }));
                }
            });
        }
    });

    
    setTimeout(function(){
        countdowntime();
    }, 2500);
});