$(function () {
	$(document).on("click", ".add_friendbutton button", function () {
	particularuser=$(this).closest('.particularuser')
	console.log(particularuser)
	console.log($(this))
	csrf=$(particularuser).attr('csrf')
	console.log(csrf)
	user=$(particularuser).attr('user')
	performaction=$(this).attr('performaction')
	actiontype=$(this).attr('actiontype')
	prev=this
	console.log(performaction)
	$.ajax({
        url: '/ajax/AddFriend/',
        data:{
		  'fuser':user,
		  'type':performaction,
			'csrfmiddlewaretoken':csrf,
        },
				type:'POST',
        success: function (data) {
					if(data==0){
						alert("something fishy")
						return;
					}
					if (performaction=='Send')
						{$(prev).html("Cancel Request")
						 $(prev).attr("performaction","Cancel");}
					else if(performaction=='Cancel')
						{
							console.log('1')
							$(prev).html("Send Request")
						$(prev).attr("performaction","Send");
					}
					else if(performaction=='Confirm')
						{$(prev).html("Unfriend")
						$(prev).attr("performaction","Unfriend")

						$('.type2').remove()
						if($(prev).hasClass('type1')){
							$(prev).removeClass('type1')
							$(prev).addClass('type2')
							$(prev).attr("actiontype","type2")
						}
					}
					else if( performaction=='Delete')
						{
							button=$('.type1')
							console.log('2')
							$(button).html("Send Request")
							$(button).attr("performaction","Send")
							$(prev).remove()
						}
					else if(performaction=='Unfriend'){
						console.log('3')
						$(prev).html("Send Request")
						$(prev).attr("performaction","Send")
					}
					else if(performaction=='Block')
					{
						console.log('4')
						console.log('blocking sucess')
						$(prev).html("UnBlock");
						$(prev).attr("performaction","UnBlock")
					}
					else if (performaction=='UnBlock') {
						console.log('5')
						$(prev).html("Block");
						$(prev).attr("performaction","Block")
					}
        }
      });

	});
});
