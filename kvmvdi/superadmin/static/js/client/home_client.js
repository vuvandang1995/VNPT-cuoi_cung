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
                    swal({
                            type: 'info',
                            title: "Please wait...",
                            showConfirmButton: false
                        });
                $.ajax({
                    type:'POST',
                    url:location.href,
                    data: {'snapshot':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname, 'snapshotname': snapshotname},
                    success: function(){
                        document.getElementById("close_modal_snapshot").click();
                        swal.close();
                    }
                });
            });
        }else if (action == 'backup'){
            $("body").on('click', '#backup_submit', function(){
                var backupname = $("input[name=backupname]").val();
                var backup_type = document.getElementById("mySelect_backup_type").value;
                var rotation = $("input[name=rotation]").val();
                    swal({
                            type: 'info',
                            title: "Please wait...",
                            showConfirmButton: false
                        });
                $.ajax({
                    type:'POST',
                    url:location.href,
                    data: {'backup':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname, 'backupname': backupname, 'backup_type': backup_type, 'rotation': rotation},
                    success: function(){
                        document.getElementById("close_modal_backup").click();
                        swal.close();
                    }
                });
            });
        }else{
            swal({
                title: 'Are you sure?',
                type: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes!'
            }).then(function(result){
                if(result.value){
                    if (action == 'del'){
                        swal({
                            type: 'info',
                            title: "Please wait...",
                            showConfirmButton: false
                        });
                    $.ajax({
                        type:'POST',
                        url:location.href,
                        data: {'delete':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                        success: function(){
                            setTimeout(function(){
                                $('.list_vm_client').DataTable().ajax.reload(null,false);
                                swal.close();
                            }, 4000);
                        }
                    });
                }
                    else if (action == 'start'){
                        swal({
                            type: 'info',
                            title: "Please wait...",
                            showConfirmButton: false
                        });
                    $.ajax({
                        type:'POST',
                        url:location.href,
                        data: {'start':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                        success: function(){
                            setTimeout(function(){
                                $('.list_vm_client').DataTable().ajax.reload(null,false);
                                swal.close();
                            }, 4000);
                        }
                    });
                }
                    else if (action == 'reboot'){
                        swal({
                            type: 'info',
                            title: "Please wait...",
                            showConfirmButton: false
                        });
                    $.ajax({
                        type:'POST',
                        url:location.href,
                        data: {'reboot':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                        success: function(){
                            setTimeout(function(){
                                $('.list_vm_client').DataTable().ajax.reload(null,false);
                                swal.close();
                            }, 4000);
                        }
                    });
                }
                    else if (action == 'stop'){
                        swal({
                            type: 'info',
                            title: "Please wait...",
                            showConfirmButton: false
                        });
                    $.ajax({
                        type:'POST',
                        url:location.href,
                        data: {'stop':id, 'csrfmiddlewaretoken':token, 'ops':ops, 'svname': svname},
                        success: function(){
                            setTimeout(function(){
                                $('.list_vm_client').DataTable().ajax.reload(null,false);
                                swal.close();
                            }, 4000);
                        }
                    });
                }
                }
            })

            
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