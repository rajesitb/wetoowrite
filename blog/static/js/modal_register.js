var delayTimer;
$('document').ready(function(){
    $('input[name="r_username"],input[name="r_email"]').css( {'margin-bottom':0})

    $('.username').after(function(){
        return `<p id='error_id_username' class='invalid-feedback' style='font-weight:bold'></p>`
    })
    $('.username').keyup(function(){
    clearTimeout(delayTimer);
        delayTimer = setTimeout(function(){
            var text = $('.username').val();
            $.ajax({
                url:'/name/',
                data:{
                    'search_term':text,
                    },
                dataType: 'json',
                success:function(data){
                console.log(data.data)
                var result = data.data
                $('#error_id_username').text('UserName: '+result).css({'display':'block','color':'black'})
                var str = $('#error_id_username').text().split(':')[1]
                if (str.length <= 6){
                        $('#error_id_username').css({'color':'red','font-weight':'bold'})
                    }
                }
            }),1000});
    });
});

var delayTimer;
var error_message = `<p id='error_id_email' class='invalid-feedback'><strong>Please enter a valid email</strong></p>`
$(function(){
    $('.email').prop({'autocomplete':'off'})
    $('input.email').after(function(){
        return `<p id='error_id_email' class='invalid-feedback' onfocusout="clearMessage()">
        <strong>Please enter a valid email</strong></p>`
    })//after
    $('input.email').keyup(function(){
    clearTimeout(delayTimer);
        delayTimer = setTimeout(function(){
            var regex_email = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
            var email = $('input.email').val()
            console.log(email)
            if (email.match(regex_email)){
                console.log('true')
                $('#error_id_email').text('');
                $.ajax({
                    url:'/name/',
                    data:{
                        'search_email':email,
                        },
                    dataType: 'json',
                    success:function(data){
                        var e_result = data.email_data
                        $('#error_id_email').text('Email: '+e_result).css({'display':'inline','font-weight':'bold'})
                        var str = $('#error_id_email').text().split(':')[1]
                        if (str.length <= 6){
                            $('#error_id_email').css({'color':'red','font-weight':'bold'})
                        }
                        else{
                        console.log('false')
                            $('#error_id_email').css({'color':'black','font-weight':'bold'})
                            }//else
                        }//success
                });//ajax
            }//if
            else{
                $('#error_id_email').text('Please enter a valid email')
                .css({'display':'inline','font-weight':'bold'});
            }//else

        1000});//setTimeout
    });

});