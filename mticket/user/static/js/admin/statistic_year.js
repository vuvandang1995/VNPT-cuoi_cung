$(document).ready(function(){
    var year = $("input[name=year]").val();
    $('#tb_agent').dataTable( {
        "ajax": {
            "type": "GET",
            "url": "/admin/statistic_data_agent_3_"+year,
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        dom: 'Bfrtip',
        buttons: ['excel', 'pdf', 'print'],
    } );

    $('#tb_call_center').dataTable( {
        "ajax": {
            "type": "GET",
            "url": "/admin/statistic_data_call_center_3_"+year,
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        dom: 'Bfrtip',
        buttons: ['excel', 'pdf', 'print'],
    } );

    $('#tb_service').dataTable( {
        "ajax": {
            "type": "GET",
            "url": "/admin/statistic_data_service_3_"+year,
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        dom: 'Bfrtip',
        buttons: ['excel', 'pdf', 'print'],
    } );

    $('body').on('click', '#update', function(){
        var year = $("input[name=year]").val();
        agent = $("#tb_agent").DataTable();
        agent.ajax.url('/admin/statistic_data_agent_3_'+year).load();
        agent.ajax.reload();
        call_center =$("#tb_call_center").DataTable();
        call_center.ajax.url('/admin/statistic_data_call_center_3_'+year).load();
        call_center.ajax.reload();
        service = $("#tb_service").DataTable();
        service.ajax.url('/admin/statistic_data_service_3_'+year).load();
        service.ajax.reload();
        $("#title").html("Thống kê "+year);
        $("#close").click();
    });

});