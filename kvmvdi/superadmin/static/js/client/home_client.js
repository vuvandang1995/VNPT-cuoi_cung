$(document).ready(function(){
    $('body .list_vm_client').each( function(){
        $(this).DataTable({
            "ajax": {
                "type": "GET",
                "url": "/client/home_data_192.168.40.146",
                "contentType": "application/json; charset=utf-8",
                "data": function(result){
                    return JSON.stringify(result);
                },
            },
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
            "displayLength": 10,
        });
    });


    $("body").on('click', '.console', function(){
        var url = $(this).attr('id');
        window.open(url);
    });

    $("#snapshot").on('show.bs.modal', function(event){
        $("input[name=snapshotname]").val('');
    });

    $("#backup").on('show.bs.modal', function(event){
        $("input[name=backupname]").val('');
    });

    $("body").on('click', '.control', function(){
        var id = $(this).attr('id').split('_')[1];
        var action = $(this).attr('id').split('_')[0];
        var ops = $(this).attr('name').split('_')[0];
        var svname = $(this).attr('name').split('_')[1];
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (action == 'snapshot'){
            $("body").on('click', '#snapshot_submit', function(){
                var snapshotname = $("input[name=snapshotname]").val();
                $("#processing").modal({backdrop: false, keyboard: false});
                $.ajax({
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(event){
                            var percent = Math.round((event.loaded / event.total) * 100) + '%';
                            $("#progressBar").attr("style","width:"+percent);
                            $("#progressBar").text(percent);
                        }, false);
                        return xhr;
                      },
                    type:'POST',
                    url:location.href,
                    data: {'snapshot':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname, 'snapshotname': snapshotname},
                    success: function(){
                        document.getElementById("close_modal_snapshot").click();
                        $("#processing").modal('hide');
                    }
                });
            });
        }else if (action == 'backup'){
            $("body").on('click', '#backup_submit', function(){
                var backupname = $("input[name=backupname]").val();
                var backup_type = document.getElementById("mySelect_backup_type").value;
                var rotation = $("input[name=rotation]").val();
                $("#processing").modal({backdrop: false, keyboard: false});
                $.ajax({
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(event){
                            var percent = Math.round((event.loaded / event.total) * 100) + '%';
                            $("#progressBar").attr("style","width:"+percent);
                            $("#progressBar").text(percent);
                        }, false);
                        return xhr;
                      },
                    type:'POST',
                    url:location.href,
                    data: {'backup':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname, 'backupname': backupname, 'backup_type': backup_type, 'rotation': rotation},
                    success: function(){
                        document.getElementById("close_modal_backup").click();
                        $("#processing").modal('hide');
                    }
                });
            });
        }else if (confirm('Bạn có chắc ?')){
            if (action == 'del'){
                $("#processing").modal({backdrop: false, keyboard: false});
                $.ajax({
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(event){
                            var percent = Math.round((event.loaded / event.total) * 100) + '%';
                            $("#progressBar").attr("style","width:"+percent);
                            $("#progressBar").text(percent);
                        }, false);
                        return xhr;
                      },
                    type:'POST',
                    url:location.href,
                    data: {'delete':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                    success: function(){
                        setTimeout(function(){
                            $('.list_vm_client').DataTable().ajax.reload(null,false);
                            $("#processing").modal('hide');
                        }, 4000);
                    }
                });
            }else if (action == 'start'){
                $("#processing").modal({backdrop: false, keyboard: false});
                $.ajax({
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(event){
                            var percent = Math.round((event.loaded / event.total) * 100) + '%';
                            $("#progressBar").attr("style","width:"+percent);
                            $("#progressBar").text(percent);
                        }, false);
                        return xhr;
                      },
                    type:'POST',
                    url:location.href,
                    data: {'start':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                    success: function(){
                        setTimeout(function(){
                            $('.list_vm_client').DataTable().ajax.reload(null,false);
                            $("#processing").modal('hide');
                        }, 4000);
                    }
                });
            }else if (action == 'reboot'){
                $("#processing").modal({backdrop: false, keyboard: false});
                $.ajax({
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(event){
                            var percent = Math.round((event.loaded / event.total) * 100) + '%';
                            $("#progressBar").attr("style","width:"+percent);
                            $("#progressBar").text(percent);
                        }, false);
                        return xhr;
                      },
                    type:'POST',
                    url:location.href,
                    data: {'reboot':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                    success: function(){
                        setTimeout(function(){
                            $('.list_vm_client').DataTable().ajax.reload(null,false);
                            $("#processing").modal('hide');
                        }, 4000);
                    }
                });
            }else if (action == 'stop'){
                $("#processing").modal({backdrop: false, keyboard: false});
                $.ajax({
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function(event){
                            var percent = Math.round((event.loaded / event.total) * 100) + '%';
                            $("#progressBar").attr("style","width:"+percent);
                            $("#progressBar").text(percent);
                        }, false);
                        return xhr;
                      },
                    type:'POST',
                    url:location.href,
                    data: {'stop':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                    success: function(){
                        setTimeout(function(){
                            $('.list_vm_client').DataTable().ajax.reload(null,false);
                            $("#processing").modal('hide');
                        }, 4000);
                    }
                });
            }
            
        }
    });

    $("#mySelect_image").select2({
        templateResult: formatState
    });

    $("#mySelect").select2({
        templateResult: formatState
    });
    
    function formatState (state) {
        if (!state.id) { return state.text; }
        var $state = $(
        '<span>' + state.text + '</span>'
        );
        return $state;
    }

});