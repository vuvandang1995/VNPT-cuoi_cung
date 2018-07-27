$(document).ready(function(){
    $('body').on('click', '#new', function(){
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var id = $("body input[name=id]").val();
        var name = $("body input[name=name]").val();
        var day = $("body input[name=day]").val();
        var hour = $("body input[name=hour]").val();
        var minute = $("body input[name=minute]").val();
        var second = $("body input[name=second]").val();
        if(id == ''){
            id = 0
        }
        if(day == ''){
            day = 0
        }
        if(hour == ''){
            hour = 0
        }
        if(minute == ''){
            minute = 0
        }
        if(second == ''){
            second = 0
        }
        $.ajax({
                type:'POST',
                url:location.href,
                data: {'csrfmiddlewaretoken':token,'id':id, 'name':name, 'day':day, 'hour': hour, 'minute':minute, 'second':second},
                success: function(){
                    // window.location.reload();
                    $("body #tb").load(location.href + " #tb");
                    $("#close").click()
                }
           });
    });
    $("#filter ").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        if (title === 'edit'){
            $('#title').html("Chỉnh sửa")
            var id = button.attr('id');
            $("input[name=id]").val(id);
            var name = $("#name"+id).val();
            $("input[name=name]").val(name);
            $("input[name=day]").val("");
            $("input[name=hour]").val("");
            $("input[name=minute]").val("");
            $("input[name=second]").val("");
        }else{
            $('#title').html("Thêm mới")
            $("input[name=id]").val("");
            $("input[name=name]").val("");
            $("input[name=day]").val("");
            $("input[name=hour]").val("");
            $("input[name=minute]").val("");
            $("input[name=second]").val("");
        }
    });

});