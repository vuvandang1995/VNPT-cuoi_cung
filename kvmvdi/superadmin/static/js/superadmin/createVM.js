$(document).ready(function(){
  $("#i_submit").click(function() {
    var token = $("input[name=csrfmiddlewaretoken]").val();
    var svname = $("input[name=svname]").val();
    var description = $("input[name=description]").val();
    var image = document.getElementById("mySelect_image").value;
    var network = document.getElementById("mySelect").value;
    var ram = $("input[name=ram]").val();
    var vcpus = $("input[name=vcpus]").val();
    var disk = $("input[name=disk]").val();
    $.ajax({
        type:'POST',
        url:location.href,
        data: {'svname': svname, 'description': description, 'csrfmiddlewaretoken':token, 'image': image, 'network': network, 'ram': ram, 'vcpus': vcpus,'disk': disk},
        success: function(){
            document.getElementById("close_modal").click();
            setTimeout(function(){
                $('#list_vm').DataTable().ajax.reload(null,false);
            }, 8000);
        }
    });
});

  $("#id02").on('show.bs.modal', function(event){
      $("input[name=svname]").val("");
      $("input[name=description]").val("");
      $("input[name=image]").val("");
      $("input[name=ram]").val("0.5");
      $("input[name=vcpus]").val("1");
      $("input[name=disk]").val("20");
  });
});