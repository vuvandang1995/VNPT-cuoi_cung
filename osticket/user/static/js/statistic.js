$(document).ready(function(){
    $('#tb').dataTable( {
        dom: 'Bfrtip',
        buttons: ['excel', 'pdf', 'print'],
    } );

    $('body').on('click', '#update', function(){
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var month = $("body input[name=month]").val();
        var year = $("body input[name=year]").val();
        var all;
        if ($('body input:checkbox').is(":checked")){
                all = 1;
            }else {
                all = 0;
            }
        location.href="/agent/admin/statistic_"+all+"_"+month+"_"+year;
    });

});