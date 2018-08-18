$(document).ready(function(){
    var date = $("input[name=date]").val();
    $('#tb_agent').dataTable( {
        "ajax": {
            "type": "GET",
            "url": "/admin/statistic_data_agent_1_"+date,
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
            "url": "/admin/statistic_data_call_center_1_"+date,
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
            "url": "/admin/statistic_data_service_1_"+date,
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            }
        },
        dom: 'Bfrtip',
        buttons: ['excel', 'pdf', 'print'],
    } );

    $('body').on('click', '#update', function(){
        var date = $("input[name=date]").val();
        agent = $("#tb_agent").DataTable();
        agent.ajax.url('/admin/statistic_data_agent_1_'+date).load();
        agent.ajax.reload();
        call_center =$("#tb_call_center").DataTable();
        call_center.ajax.url('/admin/statistic_data_call_center_1_'+date).load();
        call_center.ajax.reload();
        service = $("#tb_service").DataTable();
        service.ajax.url('/admin/statistic_data_service_1_'+date).load();
        service.ajax.reload();
        var day = new Date(date);
        var dd = day.getDate();
        var mm = day.getMonth()+1; //January is 0!
        var yyyy = day.getFullYear();
        if(dd<10){
            dd='0'+dd;
        }
        if(mm<10){
            mm='0'+mm;
        }
        var day = dd+'/'+mm+'/'+yyyy;
        $("#title").html("Thống kê tuần từ "+day);
        $("#close").click();
    });

});