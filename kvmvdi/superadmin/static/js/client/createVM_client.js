$(document).ready(function(){
    $("#i_submit").click(function() {
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var svname = $("input[name=svname]").val();
        var description = $("input[name=description]").val();
        var image = document.getElementById("mySelect_image").value;
        var ops = $("input[name=svip]").val();
        var project = $("input[name=project]").val();
        var flavor = document.getElementById("mySelect").value;
        var ram = $("input[name=ram]").val();
        var vcpus = $("input[name=vcpus]").val();
        var disk = $("input[name=disk]").val();
        var count = $("input[name=count]").val();
        var price = $("input[name=price]").val();
        swal({
            type: 'info',
            title: "Please wait...",
            showConfirmButton: false
        });
        $.ajax({
            type:'POST',
            url:location.href,
            data: {'svname': svname, 'price': price,'ops': ops, 'description': description, 'csrfmiddlewaretoken':token, 'image': image, 'flavor': flavor, 'ram': ram, 'vcpus': vcpus,'disk': disk, 'count': count, 'project': project},
            success: function(msg){
                if (msg == "Vui long nap them tien vao tai khoan!"){
                    swal({
                        type: 'warning',
                        title: msg,
                    });
                }else{
                    document.getElementById("close_modal").click();
                    setTimeout(function(){
                        $('.list_vm_client').DataTable().ajax.reload(null,false);
                        swal.close();
                    }, 10000);
                }
             },
        });

    });



    $("#id02").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var ip = button.data('title');
        var project = button.data('project');
        $("input[name=svip]").val(ip);
        $("input[name=project]").val(project);
        $("input[name=svname]").val("");
        $("input[name=description]").val("");
        $("input[name=ram]").val("0.5");
        $("input[name=vcpus]").val("1");
        $("input[name=disk]").val("20");
        $("input[name=count]").val("1");
        opsSocket.send(JSON.stringify({
            'message' : ip,
        }));
    });


    $('body .price').change(function(){
        var flavor = document.getElementById("mySelect").value;
        var ram = flavor.split(',')[0];
        var vcpus = flavor.split(',')[1];
        var disk = flavor.split(',')[2];
        var count = $("body input[name=count]").val();
        var price_new = ((parseInt(ram)/1024) * 3 + parseInt(vcpus) * 2 + parseInt(disk) * 1) * parseInt(count);
        $("body input[name=price]").val(price_new);
    });
});