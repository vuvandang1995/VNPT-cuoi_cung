
$(document).ready(function(){
    var table = $('#list_tk_tu_xu_ly').DataTable({
        "columnDefs": [
            { "width": "2%", "targets": 0 },
            { "width": "12%", "targets": 1 },
            { "width": "10%", "targets": 2 },
            { "width": "10%", "targets": 3 },
            { "width": "10%", "targets": 4 },
            { "width": "5%", "targets": 5 },
            { "width": "5%", "targets": 6 },
            { "width": "3%", "targets": 7 },
            { "width": "9%", "targets": 8 },
            { "width": "9%", "targets": 9 },
            { "width": "7%", "targets": 10 },
            { "width": "5%", "targets": 11 },
            { "width": "13%", "targets": 12 },
        ],
        "ajax": {
            "type": "GET",
            "url": "/user/tu_xu_ly"+"_"+uname,
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
    var table = $('#list_tk_gui_di').DataTable({
        "columnDefs": [
                    { "width": "2%", "targets": 0 },
                    { "width": "12%", "targets": 1 },
                    { "width": "5%", "targets": 2 },
                    { "width": "10%", "targets": 3 },
                    { "width": "10%", "targets": 4 },
                    { "width": "5%", "targets": 5 },
                    { "width": "5%", "targets": 6 },
                    { "width": "3%", "targets": 7 },
                    { "width": "9%", "targets": 8 },
                    { "width": "9%", "targets": 9 },
                    { "width": "7%", "targets": 10 },
                    { "width": "5%", "targets": 11 },
                    { "width": "5%", "targets": 12 },
                    { "width": "13%", "targets": 13 },
                ],

        "ajax": {
            "type": "GET",
            "url": "/user/gui_di"+"_"+uname,
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

    $("#image").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var path = button.data('title');
        var img = '<img src="/media/'+ path +'" style="max-width:80%;max-height:600px;">'
        $("#img").html(img);
    });
    $('body').on('click', '.close_ticket_txl', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var mgs = 'Yêu cầu số ' +id+' được đóng bởi '+userName;
        var message = []
        if(confirm("Bạn có chắc không ?")){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'tkid':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    $("#list_tk_tu_xu_ly").DataTable().ajax.reload();
                    var chatSocket1 = new WebSocket(
                    'ws://' + window.location.host +
                    '/ws/agent/agent+group_agent_Socket/');
                    var message = '';
                    message = 'load';

                    var date = formatAMPM(new Date());
                    chatSocket1.onopen = function (event) {
                        chatSocket1.send(JSON.stringify({
                            'message' : message,
                            'time' : date
                        }));
                    };

                    var chatSocket2 = new WebSocket(
                    'ws://' + window.location.host +
                    '/ws/user/' + uname + '/');

                    var date = formatAMPM(new Date());
                    message = 'Yêu cầu số '+id+' đã đóng bởi '+fullName+'!';
                    chatSocket2.onopen = function (event) {
                        chatSocket1.send(JSON.stringify({
                            'message' : message,
                            'time' : date,
                        }));
                    };
                }
            });
        }
    });

    $('body').on('click', '.send_ticket', function(){
        var id = $(this).attr('id').split('!')[1];
        var topic_name = $(this).attr('id').split('!')[0];
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if(confirm("Bạn có chắc không ?")){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'tkid_send':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    // window.location.reload();
                    var chatSocket1 = new WebSocket(
                    'ws://' + window.location.host +
                    '/ws/agent/agent+group_agent_Socket/');
                    var message = '';
                    message = 'Bạn có một yêu cầu mới!'+topic_name;
                    var date = formatAMPM(new Date());
                    chatSocket1.onopen = function (event) {
                        chatSocket1.send(JSON.stringify({
                            'message' : message,
                            'time' : date
                        }));
                    };

                    var chatSocket2 = new WebSocket(
                    'ws://' + window.location.host +
                    '/ws/user/' + uname + '/');

                    var date = formatAMPM(new Date());
                    message = 'Yêu cầu số '+id+' đã chuyển bởi '+fullName+'!';
                    chatSocket2.onopen = function (event) {
                        chatSocket1.send(JSON.stringify({
                            'message' : message,
                            'time' : date,
                        }));
                    };
                    $(".table").DataTable().ajax.reload();
                }
            });
        }

    });

    $('body').on('click', '.modify_ticket', function(){
        var id = $(this).attr('id');
        $("#usercontent").modal('show');

        $("body input[name=tkid_]").val(id);

        var service = $('#service'+id).text();
        $('#usercontent #service').text(service);

        var loai_su_co = $('#loai'+id).children('p').text();
        $("body input[name=loai_su_co]").val(loai_su_co);

        var content = $('#content'+id).children('p').text();
        $("body textarea[name=content]").val(content);

        var thong_so_kt = $('#thong_so'+id).children('p').text();
        $("body textarea[name=thong_so_kt]").val(thong_so_kt);

        var note = $("#"+id).data('title');
        $("body textarea[name=note]").val(note);

        var client_ = $("#client_"+id).text();
        $("body input[name=client]").val(client_);

        var client = $("#client"+id).text();
        $("body input[name=info_client]").val(client);        
    });

    $("#ticketcontent").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var id = button.text().replace(/\s/g,'');

        var service = $('#service'+id).text();
        $('#ticketcontent #service').text(service);

        var loai_su_co = $('#loai'+id).children('p').text();
        $("body input[name=loai_su_co]").val(loai_su_co);

        var content = $('#content'+id).children('p').text();
        $("body textarea[name=content]").val(content);

        var thong_so_kt = $('#thong_so'+id).children('p').text();
        $("body textarea[name=thong_so_kt]").val(thong_so_kt);

        var note = $("#"+id).data('title');
        $("body textarea[name=note]").val(note);

        var client_ = $("#client_"+id).text();
        $("body input[name=client]").val(client_);

        var client = $("#client"+id).text();
        $("body input[name=info_client]").val(client);
    });

    $('body').on('click', '.save_modify', function(){
        var id = $("input[name=tkid_]").val();
        var token = $("input[name=csrfmiddlewaretoken]").val();
        $("#usercontent").modal('hide');
        var loai_su_co = $("#usercontent input[name=loai_su_co]").val();
        var content = $("#usercontent textarea[name=content]").val();
        var thong_so_kt = $("#usercontent textarea[name=thong_so_kt]").val();
        var note = $("#usercontent textarea[name=note]").val();
        var client = $("#usercontent input[name=client]").val();
        var info_client = $("#usercontent input[name=info_client]").val();
        var message = [];
        var stt = $('#stt'+id).html();
        $.ajax({
            type:'POST',
            url:location.href,
            data: {'tkid_modify':id, 'csrfmiddlewaretoken':token, 'loai_su_co': escapeHtml(loai_su_co),
            'content': escapeHtml(content), 'thong_so_kt': escapeHtml(thong_so_kt), 'note': escapeHtml(note),
             'client': escapeHtml(client), 'info_client': escapeHtml(info_client)},
            success: function(){
                var chatSocket1 = new WebSocket(
                'ws://' + window.location.host +
                '/ws/agent/agent+group_agent_Socket/');
                var array1 = $('#hd'+id).html();
                if (typeof array1 === 'undefined' || array1 == 'Không có ai'){
                    var date = formatAMPM(new Date());
                    chatSocket1.onopen = function (event) {
                        chatSocket1.send(JSON.stringify({
                            'message' : 'load_page_leader_admin',
                            'time' : date
                        }));
                    };
                }else{
                    var array = $('#hd'+id).html().split("<br>");
                    for (i = 0; i < array.length-1; i++) {
                        var agentName = array[i].replace(/\s/g,'');
                        message.push(agentName);
                    }
                    mgs = 'Yêu cầu số ' +id+' được chỉnh sửa bởi '+userName;
                    message.push(mgs);
                    var date = formatAMPM(new Date());
                    chatSocket1.onopen = function (event) {
                        chatSocket1.send(JSON.stringify({
                            'message' : message,
                            'time' : date
                        }));
                    };
                }
                var chatSocket2 = new WebSocket(
                'ws://' + window.location.host +
                '/ws/user/' + uname.replace(/"/g, '') + '/');

                var date = formatAMPM(new Date());
                message = 'Yêu cầu số '+id+' được chỉnh sửa bởi '+userName+'!';
                chatSocket2.onopen = function (event) {
                    chatSocket2.send(JSON.stringify({
                        'message' : message,
                        'time' : date,
                    }));
                };
                $(".table").DataTable().ajax.reload();
            }
        });
    });

    $('body').on('click', '.close_ticket_gui_di', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var mgs = 'Yêu cầu số ' +id+' được đóng bởi '+userName;
        var message = []
        if(confirm("Bạn có chắc không ?")){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'tkid':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    // window.location.reload();
                    $("#list_tk_gui_di").DataTable().ajax.reload();
                    var array = $('#hd'+id).html().split("<br>");
                    for (i = 0; i < array.length-1; i++) {
                        var agentName = array[i].replace(/\s/g,'');
                        message.push(agentName);
                    }

                    message.push(mgs);
                    var date = formatAMPM(new Date());
                    var chatSocket1 = new WebSocket(
                    'ws://' + window.location.host +
                    '/ws/agent/agent+group_agent_Socket/');
                    chatSocket1.onopen = function (event) {
                        chatSocket1.send(JSON.stringify({
                            'message' : message,
                            'time': date
                        }));

                        chatSocket1.send(JSON.stringify({
                            'message' : 'reload_home_agent',
                            'time': date
                        }));
                    };

                    var chatSocket2 = new WebSocket(
                    'ws://' + window.location.host +
                    '/ws/user/' + uname + '/');

                    var date = formatAMPM(new Date());
                    message = 'Yêu cầu số '+id+' đã đóng bởi '+fullName+'!';
                    chatSocket2.onopen = function (event) {
                        chatSocket1.send(JSON.stringify({
                            'message' : message,
                            'time' : date,
                        }));
                    };
                }
            });
        }

    });

    $("body").on('click', '#chat_with_agent', function(){
        var tkid = $(this).children('input').val();
        $('body .chat'+tkid).show();
        $("body .mytext").focus();

        if (typeof(Storage) !== "undefined") {
            var herf = $(this).attr('href');
            var chat = herf.substring(herf.indexOf("(")+1, herf.indexOf(")"));
            // Gán dữ liệu
            sessionStorage.setItem(tkid, chat);

            // Lấy dữ liệu
        } else {
            document.write('Trình duyệt của bạn không hỗ trợ local storage');
        }

        if (dict_ws[tkid] == undefined){
            dict_ws[tkid] = new WebSocket(
            'ws://' + window.location.host +
            '/ws/' + tkid + '/');
        }

        var me = {};
        me.avatar = "https://cdn2.iconfinder.com/data/icons/perfect-flat-icons-2/512/User_man_male_profile_account_person_people.png";

        var you = {};
        you.avatar = "https://cdn2.iconfinder.com/data/icons/rcons-users-color/32/support_man-512.png";


        //-- No use time. It is a javaScript effect.
        function insertChat(who, text, time){
            if (time === undefined){
                time = 0;
            }
            var control = "";
            var date = time;

            if (who == "me"){
                control = '<li style="width:100%">' +
                                '<div class="msj macro">' +
                                '<div class="avatar"><img class="img-circle" style="width:100%;" src="'+ me.avatar +'" /></div>' +
                                    '<div class="text text-l">' +
                                        '<p>'+ text +'</p>' +
                                        '<p><small>'+date+'</small></p>' +
                                    '</div>' +
                                '</div>' +
                            '</li>';
            }else{
                control = '<li style="width:100%;">' +
                                '<div class="msj-rta macro">' +
                                    '<div class="text text-r">' +
                                        '<p>'+text+'</p>' +
                                        '<p><small>'+date+'</small></p>' +
                                    '</div>' +
                                '<div class="avatar" style="padding:0px 0px 0px 10px !important"><img class="img-circle" style="width:100%;" src="'+you.avatar+'" /></div>' +
                        '</li>';
            }
            setTimeout(
                function(){
                    $("body #chat"+tkid+" .frame > ul").append(control).scrollTop($("body #chat"+tkid+" .frame > ul").prop('scrollHeight'));
                }, time);

        }


        dict_ws[tkid].onmessage = function(e) {
            var data = JSON.parse(e.data);
            var message = data['message'];
            var who = data['who'];
            var time = data['time'];
            insertChat(who, message, time);
        };

    });

    $("#note").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        if (title === 'done'){
            var tkid = button.attr('id');
            $("input[name=ticketid]").val(tkid);
            $('#note #title').html("Cập nhật ghi chú cho yêu cầu"+tkid)
            var comment1 = $('#note'+tkid).html();
            $('textarea#comment').val(comment1);
        }
    });

    $("#all_note").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var note = button.data('title');
        $("#note_content").html("<pre>"+note+"</pre>");
    });

    $("body").on('click', '#send_note', function(){
        var id = $("#note input[name=ticketid]").val();
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var comment = $('textarea#comment').val();
        $("#note").modal('hide');
        var message = [];
        $.ajax({
            type:'POST',
            url:location.href,
            data: {'tkid_reprocess':id, 'csrfmiddlewaretoken':token, 'comment': escapeHtml(comment)},
            success: function(){
                var chatSocket1 = new WebSocket(
                    'ws://' + window.location.host +
                    '/ws/agent/agent+group_agent_Socket/');
                mgs = userName + ' đã mở lại yêu cầu số '+id;
                var array = $('#hd'+id).html().split("<br>");
                for (i = 0; i < array.length-1; i++) {
                    var agentName = array[i].replace(/\s/g,'');
                    message.push(agentName);
                }
                message.push(mgs);
                var date = formatAMPM(new Date());
                chatSocket1.onopen = function (event) {
                    chatSocket1.send(JSON.stringify({
                        'message' : message,
                        'time' : date
                    }));
                };


                var chatSocket2 = new WebSocket(
                'ws://' + window.location.host +
                '/ws/user/' + uname.replace(/"/g, '') + '/');

                var date = formatAMPM(new Date());
                message = 'Yêu cầu số '+id+' đã mở lại bởi '+userName+'!';
                chatSocket2.onopen = function (event) {
                    chatSocket2.send(JSON.stringify({
                        'message' : message,
                        'time' : date,
                    }));
                };
                $(".table").DataTable().ajax.reload();
            }
        });
     });
});
