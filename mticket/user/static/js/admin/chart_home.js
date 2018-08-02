$(document).ready(function(){
    var month_1 = $('#month_1').val();
    var year_1 = $('#year_1').val();
    $.ajax({
         type: "GET",
         url: '/admin/data_line_month_'+month_1+'_'+year_1+'_all',
         contentType: "application/json; charset=utf-8",
         success: function(response){
            var ctx_1 = $("#bieu_do_1");
            var chart_1 = new Chart(ctx_1, {
                type: 'line',
                data: response,
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Biểu đồ số lượng sự cố',
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true,
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Ngày',
                            }
                        }],
                        yAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Sự cố',
                            }
                        }]
                    }
                }
            });
         }
    });
    $.ajax({
         type: "GET",
         url: '/admin/data_pie_month_'+month_1+'_'+year_1+'_all',
         contentType: "application/json; charset=utf-8",
         success: function(response){
            var ctx_2 = $("#bieu_do_2");
            var chart_2 = new Chart(ctx_2, {
                type: 'pie',
                data: response,
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Biểu đồ phần trăm (%) sự cố'
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                }
            });
         }
    });

    var year_2 = $('#year_2').val();
    $.ajax({
         type: "GET",
         url: '/admin/data_line_year_'+year_2+'_all',
         contentType: "application/json; charset=utf-8",
         success: function(response){
            var ctx_3 = $("#bieu_do_3");
            var chart_3 = new Chart(ctx_3, {
                type: 'line',
                data: response,
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Biểu đồ số lượng sự cố',
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true,
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Tháng',
                            }
                        }],
                        yAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Sự cố',
                            }
                        }]
                    }
                }
            });
         }
    });
    $.ajax({
         type: "GET",
         url: '/admin/data_pie_year_'+year_2+'_all',
         contentType: "application/json; charset=utf-8",
         success: function(response){
            var ctx_4 = $("#bieu_do_4");
            var chart_4 = new Chart(ctx_4, {
                type: 'pie',
                data: response,
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Biểu đồ phần trăm (%) sự cố'
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                }
            });
         }
    });

    $('body').on('click', '#update_month', function(){
        var service_1 = $("#service_1").val();
        var month_1 = $('#month_1').val();
        var year_1 = $('#year_1').val();
        $.ajax({
         type: "GET",
         url: '/admin/data_line_month_'+month_1+'_'+year_1+'_'+service_1,
         contentType: "application/json; charset=utf-8",
         success: function(response){
            $("#bieu_do_1").remove();
            $("#cha_1").append('<canvas id="bieu_do_1"></canvas>');
            var ctx_1 = $("#bieu_do_1");
            var chart_1 = new Chart(ctx_1, {
                type: 'line',
                data: response,
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Biểu đồ số lượng sự cố',
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true,
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Ngày',
                            }
                        }],
                        yAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Sự cố',
                            }
                        }]
                    }
                }
            });
         }
    });
        $.ajax({
         type: "GET",
         url: '/admin/data_pie_month_'+month_1+'_'+year_1+'_'+service_1,
         contentType: "application/json; charset=utf-8",
         success: function(response){
            $("#bieu_do_2").remove();
            $("#cha_2").append('<canvas id="bieu_do_2"></canvas>');
            var ctx_2 = $("#bieu_do_2");
            var chart_2 = new Chart(ctx_2, {
                type: 'pie',
                data: response,
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Biểu đồ phần trăm (%) sự cố'
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                }
            });
         }
    });
        if(service_1==='all'){
            $("#title_month").html("Tổng số sự cố "+month_1+'/'+year_1);
        }
        else{
            $("#title_month").html("Tổng số sự cố "+service_1+" "+month_1+'/'+year_1);
        }
        $("#close_month").click();
    });
    $('body').on('click', '#update_year', function(){
        var service_2 = $("#service_2").val();
        var year_2 = $('#year_2').val();
        $.ajax({
         type: "GET",
         url: '/admin/data_line_year_'+year_2+'_'+service_2,
         contentType: "application/json; charset=utf-8",
         success: function(response){
            $("#bieu_do_3").remove();
            $("#cha_3").append('<canvas id="bieu_do_3"></canvas>');
            var ctx_3 = $("#bieu_do_3");
            var chart_3 = new Chart(ctx_3, {
                type: 'line',
                data: response,
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Biểu đồ số lượng sự cố',
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true,
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Tháng',
                            }
                        }],
                        yAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Sự cố',
                            }
                        }]
                    }
                }
            });
         }
    });
        $.ajax({
         type: "GET",
         url: '/admin/data_pie_year_'+year_2+'_'+service_2,
         contentType: "application/json; charset=utf-8",
         success: function(response){
            $("#bieu_do_4").remove();
            $("#cha_4").append('<canvas id="bieu_do_4"></canvas>');
            var ctx_4 = $("#bieu_do_4");
            var chart_4 = new Chart(ctx_4, {
                type: 'pie',
                data: response,
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Biểu đồ phần trăm (%) sự cố'
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                }
            });
         }
    });
        if(service_2==='all'){
            $("#title_year").html("Tổng số sự cố "+year_2);
        }
        else{
            $("#title_year").html("Tổng số sự cố "+service_2+" "+year_2);
        }
        $("#close_year").click();

    });
});