$(document).ready(function(){
    $("#list_topic").on('click', '.btn-danger', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var leader = $("#tendangnhap"+id.split('_')[2]).html();
        var r = confirm('Are you sure?');
        var svname = $(this).children('p').text();
        ag_leader = [];
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    $("body #list_agent_leader_"+svname).load(location.href + " #list_agent_leader_"+svname);
                    var date = formatAMPM(new Date());
                    ag_leader.unshift('admin_delete_topic');
                    ag_leader.unshift(leader);
                    ag_leader.unshift(svname);
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
        var serviceid = $("#mySelect").val();
        var svname = $("#mySelect").find('option:selected').attr("name");
        ag_leader = [];
        var list_agent = [];
        $('#topicModal input:checkbox').each(function() {
            if ($(this).is(":checked")){
                list_agent.push(this.name);
            }
        });
        
        $.ajax({
            type:'POST',
            url:location.href,
            data: {'csrfmiddlewaretoken':token, 'serviceid': serviceid, 'list_agent[]': JSON.stringify(list_agent)},
            success: function(){
                // window.location.reload();
                $("body #list_agent_leader_"+svname).load(location.href + " #list_agent_leader_"+svname);
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
    });

    $("#topicModal").on('show.bs.modal', function(event){
        $("input[name=serviceid]").val(0);
        $("input[name=search]").val("");
        $("input[name=username_leader]").val("");
        $("input[name=search]").val("");
        $('body #list_agent').empty();
        $("#leadererr").html("");
    });

    $('body #list_agent').on('change', '.check_agent', function() {
        $(this).parent().remove();
    });

    $('body #list_topic').on('change', '.switch', function() {
        var agid = parseInt($(this).attr('id').split('-')[0]);
        var svname = $(this).attr('id').split('-')[1];
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var agent = $("#tendangnhap"+agid).html();
        var check = $(this).children('p').text();
        ag_leader = [];
        if(confirm("Are you sure ?")){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'csrfmiddlewaretoken':token, 'agid':agid, 'svname': svname},
                success: function(){
                    $("body #list_agent_leader_"+svname).load(location.href + " #list_agent_leader_"+svname);
                    if (check == 'ok'){
                        var date = formatAMPM(new Date());
                        ag_leader.unshift('admin_bo_uy_quyen');
                        ag_leader.unshift(agent);
                        ag_leader.unshift(svname);
                        group_agent_Socket.send(JSON.stringify({
                            'message' : ag_leader,
                            'time' : date
                        }));
                    }else{
                        var date = formatAMPM(new Date());
                        ag_leader.unshift('admin_uy_quyen');
                        ag_leader.unshift(agent);
                        ag_leader.unshift(svname);
                        group_agent_Socket.send(JSON.stringify({
                            'message' : ag_leader,
                            'time' : date
                        }));
                    }
                }
            });
        }else{
            $("body #list_agent_leader_"+svname).load(location.href + " #list_agent_leader_"+svname);
        }
    });

});