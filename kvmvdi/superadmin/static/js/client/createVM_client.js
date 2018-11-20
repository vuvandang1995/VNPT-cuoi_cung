$(document).ready(function(){
    $("#i_submit").click(function() {
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var svname = $("input[name=svname]").val();
        var description = $("input[name=description]").val();
        var rootpass = $("input[name=rootpass]").val();
        // var image = document.getElementById("mySelect_image").value;
        var type_disk = document.getElementById("type_disk").value;
        var image;
        var flavor;
        var sshkey;
        $('.image_select').find('label').children().each(function() {
            if ($(this).is(':checked')){
                image = $(this).val();
            }
        });
        
        var ops = $("input[name=svip]").val();
        var project = $("input[name=project]").val();
        // var flavor = document.getElementById("mySelect").value;
        $('.flavor_select').find('label').children().each(function() {
            if ($(this).is(':checked')){
                flavor = $(this).val();
            }
        });

        $('.sshkey_select').find('label').children().each(function() {
            if ($(this).is(':checked')){
                sshkey = $(this).val();
            }
        });


        // var ram = $("input[name=ram]").val();
        // var vcpus = $("input[name=vcpus]").val();
        // var disk = $("input[name=disk]").val();
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
            data: {'svname': svname, 'type_disk': type_disk, 'rootpass': rootpass, 'sshkey': sshkey, 'price': price,'ops': ops, 'description': description, 'csrfmiddlewaretoken':token, 'image': image, 'flavor': flavor, 'count': count, 'project': project},
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
                    }, 0);
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
            'message' : ip+'abcxyz'+userName,
        }));
    });


    $('body .price').change(function(){
        var flavor
        $('.flavor_select').find('label').children().each(function() {
            if ($(this).is(':checked')){
                flavor = $(this).val();
            }
        });
        var ram = flavor.split(',')[0];
        var vcpus = flavor.split(',')[1];
        var disk = flavor.split(',')[2];
        var count = $("body input[name=count]").val();
        var price_new = ((parseInt(ram)/1024) * 3 + parseInt(vcpus) * 2 + parseInt(disk) * 1) * parseInt(count);
        $("body input[name=price]").val(price_new);
    });

});