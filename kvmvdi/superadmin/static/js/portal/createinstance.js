$(document).ready(function() {
    $('.js-example-basic-single').select2();
});	
function updateDCIDSelected()
{
	if ($('input[name=DCID]:checked').hasClass('deploylocationsoldout'))
	{
		var diskTypeNode = $('input[name=disk_type]:checked');
		var is_valid = diskTypeNode.length > 0 && (diskTypeNode.val() == 'SSD' || diskTypeNode.val() == 'SATA' || diskTypeNode.val() == 'DEDICATED' || diskTypeNode.val() == 'BAREMETAL');

		if (is_valid)
		{
			$('input[name=DCID]:checked')
				.attr('dropdown-info', '')
				.attr('dropdown-disclaimer', $('input[name=DCID]:checked').attr('data-city') + ' is currently sold out. We anticipate additional capacity within the next one to two weeks. Would you like to be notified when we have additional capacity?')
				.attr('dropdown-action', 'dcid-notify')
				.attr('aria-label', 'Should we notify you')
				.attr('dropdown-function', "accountLocationNotifyDCID("+$('input[name=DCID]:checked').val()+",'"+diskTypeNode.val()+"'); return false;")
				.addClass('has-dropdown')
			;

			$('.deploylocationsoldout').next('label').addClass('has-dropdown').find('*').addClass('has-dropdown').children();

			if ($('input[name=DCID]:checked').val() == DCID_TOR)
			{
				$('input[name=DCID]:checked')
					.attr('dropdown-disclaimer', 'Our Toronto, Canada location is coming soon! Would you like to be notified when it is available?')
				;
			}

			$('#accountLocationNotifyDCID input[name=backorder_DCID]').val($('input[name=DCID]:checked').val());
			$('#accountLocationNotifyDCID input[name=backorder_disk_type]').val($('input[name=disk_type]:checked').val());
			$('.warning_message').hide();
			$('.dropdown-actions').show();
			$('#question-mark').show();

			showConfirmationDropdown($('input[name=DCID]:checked'));
		}
	}

	var selected_DCID = $('input[name=DCID]:checked').val();
	$('label[data-DCID]').each(function (index, cur) {
		if ($(cur).data('dcid') != selected_DCID)
		{
			$(cur).hide();
		}
		else
		{
			$(cur).show();
		}
	});
}

$("body").on('click', '.image_', function(){
	if ($(this).css("border-color") == "rgb(230, 233, 235)"){
		$(this).css("border-color", 'red');
		$(this).prev().val($(':nth-child(3)', this).text());
	}else{
		$(this).css("border-color", 'rgb(230, 233, 235)');
		$(this).prev().val("");
	}
});