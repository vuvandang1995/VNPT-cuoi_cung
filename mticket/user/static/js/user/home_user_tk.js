$(document).ready(function(){
    var table = $('#list_tk_tu_xu_ly').DataTable({
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
            "url": location.href +"tu_xu_ly",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        'dom': 'Rlfrtip',
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": [[ 0, "desc" ]],
        "displayLength": 25,
    });
    var table = $('#list_tk_gui_di').DataTable({
        "columnDefs": [
//                    { "width": "2%", "targets": 0 },
//                    { "width": "11%", "targets": 1 },
//                    { "width": "10%", "targets": 2 },
//                    { "width": "10%", "targets": 3 },
//                    { "width": "11%", "targets": 4 },
//                    { "width": "6%", "targets": 5 },
//                    { "width": "7%", "targets": 6 },
//                    { "width": "7%", "targets": 7 },
//                    { "width": "7%", "targets": 8 },
//                    { "width": "6%", "targets": 9 },
//                    { "width": "11%", "targets": 10 },
//                    { "width": "11%", "targets": 11 },
                    { "width": "12%", "targets": 12 },
                ],
        "ajax": {
            "type": "GET",
            "url": location.href +"gui_di",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        'dom': 'Rlfrtip',
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": [[ 0, "desc" ]],
        "displayLength": 25,
    });
    $('#invalid-msg').html("");
    function validateSize(){
        if(($("#attach"))[0].files[0].size > 10485760){
            $('#invalid-msg').html("maximum size is 10MB");
            return false;
        }
        return true;
    }
    $("#id02").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        $("input[name=kind]").val(title);
    });
    $("#id02").submit(function() {
        var chatSocket1 = new WebSocket(
        'ws://' + window.location.host +
        '/ws/agent/agent+group_agent_Socket/');
        var message = '';
        var topic = document.getElementById("mySelect").value;
        var topic_name = $("#mySelect option[value='"+topic+"']").attr("name");
        message = 'Bạn có một yêu cầu mới!'+topic_name;

        var date = formatAMPM(new Date());
        chatSocket1.onopen = function (event) {
            chatSocket1.send(JSON.stringify({
                'message' : message,
                'time' : date
            }));
        };
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
//                    countdowntime();
//                    var array = $('#hd'+id).html().split("<br>");
//                    for (i = 0; i < array.length-1; i++) {
//                        var agentName = array[i].replace(/\s/g,'');
//                        message.push(agentName);
//                    }
//
//                    message.push(mgs);
//                    var date = formatAMPM(new Date());
//                    var chatSocket1 = new WebSocket(
//                    'ws://' + window.location.host +
//                    '/ws/agent/agent+group_agent_Socket/');
//                    chatSocket1.onopen = function (event) {
//                        chatSocket1.send(JSON.stringify({
//                            'message' : message,
//                            'time': date
//                        }));
//
//                        chatSocket1.send(JSON.stringify({
//                            'message' : 'reload_home_agent',
//                            'time': date
//                        }));
//                    };
                }
            });
        }
    });

    $('body').on('click', '.send_ticket', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
//        var mgs = 'Yêu cầu số ' +id+' được đóng bởi '+userName;
//        var message = []
        if(confirm("Bạn có chắc không ?")){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'tkid_send':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    // window.location.reload();
                    $(".table").DataTable().ajax.reload();
//                    countdowntime();
//                    var array = $('#hd'+id).html().split("<br>");
//                    for (i = 0; i < array.length-1; i++) {
//                        var agentName = array[i].replace(/\s/g,'');
//                        message.push(agentName);
//                    }
//
//                    message.push(mgs);
//                    var date = formatAMPM(new Date());
//                    var chatSocket1 = new WebSocket(
//                    'ws://' + window.location.host +
//                    '/ws/agent/agent+group_agent_Socket/');
//                    chatSocket1.onopen = function (event) {
//                        chatSocket1.send(JSON.stringify({
//                            'message' : message,
//                            'time': date
//                        }));
//
//                        chatSocket1.send(JSON.stringify({
//                            'message' : 'reload_home_agent',
//                            'time': date
//                        }));
//                    };
                }
            });
        }

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
                    countdowntime();
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

});
