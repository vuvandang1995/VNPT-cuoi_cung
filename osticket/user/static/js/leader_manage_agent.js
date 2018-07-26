$(document).ready(function(){
    $("#list_topic").on('click', '.btn-danger', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var leader = $("#tendangnhap"+id).html();
        var r = confirm('Are you sure?');
        ag_leader = [];
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    $("#list_topic").load(location.href + " #list_topic");
                    var date = formatAMPM(new Date());
                    ag_leader.unshift('admin_delete_topic');
                    ag_leader.unshift(leader);
                    group_agent_Socket.send(JSON.stringify({
                        'message' : ag_leader,
                        'time' : date
                    }));
                }
           });
        }
    });

    $("#addTopic").click(function() {
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var topicid = $("#mySelect").val();
        var leader = $("input[name=username_leader]").val();
        $("#leadererr").html("");
        ag_leader = [];
        if (leader==''){
            $("#leadererr").html("Vui lòng chọn");
        }else{
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'csrfmiddlewaretoken':token, 'topicid': topicid, 'leader': leader,},
                success: function(){
                    // window.location.reload();
                    $("#list_topic").load(location.href + " #list_topic");
                    document.getElementById("add_topic_close").click();
                    var date = formatAMPM(new Date());
                    ag_leader.unshift('admin_add_topic');
                    ag_leader.unshift(leader);
                    group_agent_Socket.send(JSON.stringify({
                        'message' : ag_leader,
                        'time' : date
                    }));
                }
            });
        }
    });

    $("#topicModal").on('show.bs.modal', function(event){
        $("input[name=topicid]").val(0);
        $("input[name=search]").val("");
        $("input[name=username_leader]").val("");
    });

});