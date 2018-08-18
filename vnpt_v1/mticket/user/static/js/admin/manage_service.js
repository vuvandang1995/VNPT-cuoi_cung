$(document).ready(function(){
    $("#list_topic").on('click', '.close_', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var leader = $("#leader_topic"+id).children('input').val();
        var r = confirm('Are you sure?');
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'close':id, 'csrfmiddlewaretoken':token, 'leader': leader},
                success: function(){
                    // window.location.reload();
                    $("#list_topic").load(location.href + " #list_topic");
                }
           });
        }
    });

    $("#list_topic").on('click', '.btn-danger', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var leader = $("#leader_topic"+id).children('input').val();
        var r = confirm('Are you sure?');
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token, 'leader': leader},
                success: function(){
                    // window.location.reload();
                    $("#list_topic").load(location.href + " #list_topic");
                }
           });
        }
    });

    $("#addTopic").click(function() {
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var svname = $("input[name=svname]").val();
        var description = $("input[name=description]").val();
        var svid = $("input[name=svid]").val();
        var leader = $("input[name=username_leader]").val();
        var gpsv = document.getElementById("mySelect").value;
        var ngay = $("input[name=ngay]").val();
        var gio = $("input[name=gio]").val();
        var phut = $("input[name=phut]").val();
        if (ngay == ''){
            ngay = '0';
        }
        if (gio == ''){
            gio = '0';
        }
        if (phut == ''){
            phut = '0';
        }
        var downtime = parseInt(phut) + parseInt(gio) * 60 + parseInt(ngay) * 24 * 60;

        var list_agent = [];
        var date = formatAMPM(new Date());
        $('#topicModal input:checkbox').each(function() {
            if ($(this).is(":checked")){
                list_agent.push(this.name);
            }
        });
        $("#nameerr").html("");
        $("#deserr").html("");
        $("#leadererr").html("");
        $("#gpsverr").html("");
        $("#agenterr").html("");
        $("#downtimeerr").html("");
        ag_leader = [];
        if (svname==''){
            $("#nameerr").html("Vui lòng không để trống");
        }else if(description==''){
            $("#deserr").html("Vui lòng không để trống");
        }else if (leader==''){
            $("#leadererr").html("Vui lòng chọn");
        }else if (downtime == 0){
            $("#downtimeerr").html("Vui lòng chọn");
        }else{
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'list_agent[]': JSON.stringify(list_agent), 'add_service': svname, 'description': description, 'csrfmiddlewaretoken':token, 'svid': svid, 'leader': leader, 'gpsv': gpsv, 'downtime': downtime},
                success: function(){
                    // window.location.reload();
                    $("#list_topic").load(location.href + " #list_topic");
                    document.getElementById("add_topic_close").click();
                    var date = formatAMPM(new Date());
                    ag_leader.unshift('admin_add_topic');
                    ag_leader.unshift(list_agent);
                    ag_leader.unshift(svname);
                    group_agent_Socket.send(JSON.stringify({
                        'message' : ag_leader,
                        'time' : date
                    }));

                    
                    
                }
            });
        }
    });



    $("#topicModal").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        if (title === 'edit'){
            $('#title').html("Chỉnh sửa dịch vụ")
            var svname = button.data('name');
            var svid = button.attr('id');
            $("input[name=svname]").val(svname);

            var description = $("#description_topic"+svid).html();
            $("input[name=description]").val(description);

            var leader = $("#leader_topic"+svid).children('p').text();
            $("input[name=search]").val(leader);

            var leader_username = $("#leader_topic"+svid).children('input').val();
            $("input[name=username_leader]").val(leader_username);

            var gpsv = $("input[name=gpsv"+svid+"]").val();
            $("#mySelect").val(gpsv);

            var downtime = $('body #downtime'+svid).html();
            var ngay = parseInt(downtime/1440);
            var gio = parseInt((downtime - ngay*1440)/60);
            var phut = parseInt(downtime - ngay*1440 - gio*60);
            $("input[name=ngay]").val(ngay);
            $("input[name=gio]").val(gio);
            $("input[name=phut]").val(phut);

            $('body #list_agent').empty();
            $('body .listagent'+svid).each(function(){
                var username = $(this).children('input').val();
                var fullname = $(this).text();
                var element = '<li><input style="transform: scale(1.3)" type="checkbox" class="check_agent" name="'+username+'" value="'+username+'" checked >'+fullname+'</li>';
                $('#list_agent').append(element);
            });

            $("#search_agent").val("");
            $("input[name=svid]").val(svid);
            $("#nameerr").html("");
            $("#deserr").html("");
            $("#leadererr").html("");
            $("#gpsverr").html("");
            $("#downtimeerr").html("");
            
        }else{
            $('#title').html("Thông tin dịch vụ mới")
            $("input[name=svid]").val(0);
            $("input[name=svname]").val("");
            $("input[name=description]").val("");
            $("input[name=search]").val("");
            $("input[name=search_agent]").val("");
            $("input[name=username_leader]").val("");
            $('body #list_agent').empty();
            $("input[name=ngay]").val("");
            $("input[name=gio]").val("");
            $("input[name=phut]").val("");
            $("#nameerr").html("");
            $("#deserr").html("");
            $("#leadererr").html("");
            $("#gpsverr").html("");
            $("#downtimeerr").html("");
        }
    });

    $('body #list_agent').on('change', '.check_agent', function() {
        $(this).parent().remove();
    });
});