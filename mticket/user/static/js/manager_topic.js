$(document).ready(function(){
    $("#list_topic").on('click', '.close_', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var r = confirm('Are you sure?');
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'close':id, 'csrfmiddlewaretoken':token},
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
        var r = confirm('Are you sure?');
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    // window.location.reload();
                    $("#list_topic").load(location.href + " #list_topic");
                }
           });
        }
    });

    $("#addTopic").click(function() {
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var topicname = $("input[name=topicname]").val();
        var description = $("input[name=description]").val();
        var topicid = $("input[name=topicid]").val();
        var leader = $("input[name=username_leader]").val();
        $("#nameerr").html("");
        $("#deserr").html("");
        $("#leadererr").html("");
        ag_leader = [];
        if (topicname==''){
            $("#nameerr").html("Vui lòng không để trống");
        }
        else if(description==''){
            $("#deserr").html("Vui lòng không để trống");
        }else if (leader==''){
            $("#leadererr").html("Vui lòng chọn");
        }else{
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'add_topic': topicname, 'description': description, 'csrfmiddlewaretoken':token, 'topicid': topicid, 'leader': leader},
                success: function(){
                    // window.location.reload();
                    $("#list_topic").load(location.href + " #list_topic");
                    document.getElementById("add_topic_close").click();
                    /*var date = formatAMPM(new Date());
                    ag_leader.unshift('admin_add_leader');
                    ag_leader.unshift(leader);
                    group_agent_Socket.send(JSON.stringify({
                        'message' : ag_leader,
                        'time' : date
                    }));*/
                }
            });
        }
    });



    $("#topicModal").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        if (title === 'edit'){
            $('#title').html("Edit Topic")
            var topicname = button.data('name');
            var topicid = button.attr('id');
            $("input[name=topicname]").val(topicname);

            var description = $("#description_topic"+topicid).html();
            $("input[name=description]").val(description);

            var leader = $("#leader_topic"+topicid).html();
            $("input[name=search]").val(leader);

            $("input[name=topicid]").val(topicid);
        }else{
            $('#title').html("Add New Topic")
            $("input[name=topicid]").val(0);
            $("input[name=topicname]").val("");
            $("input[name=description]").val("");
            $("input[name=search]").val("");
            $("input[name=username_leader]").val("");
        }
    });
    
});