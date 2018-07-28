$(document).ready(function(){
    $("#list_gs").on('click', '.btn-danger', function(){
        var id = $(this).attr('id');
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var r = confirm('Are you sure?');
        if (r == true){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    $("#list_gs").load(location.href + " #list_gs");
                }
           });
        }
    });

    $("#addDepartment").click(function() {
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var addname = $("input[name=name]").val();
        var gsid = $("input[name=gsid]").val();
        $("#add_name_error").html("");
        if (addname==''){
            $("#add_name_error").html("not null");
        }else{
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'addname': addname, 'csrfmiddlewaretoken':token , 'gsid':gsid},
                success: function(){
                    // window.location.reload();
                    document.getElementById("add_department_close").click();
                    $("#list_gs").load(location.href + " #list_gs");
                }
            });
        }
    });

    $("#departmentModal").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        if (title === 'edit'){
            $('#title').html("Chỉnh sửa nhóm dịch vụ")
            var gsid = button.attr('id');
            $("input[name=gsid]").val(gsid);
            var name = $("#name"+gsid).html();
            $("input[name=name]").val(name);
            
        }
        else{
            $("input[name=gsid]").val("");
            $("input[name=name]").val("");
        }
    });
});