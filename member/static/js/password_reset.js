var delayTimerEmail;
$('document').ready(function(){


    $('input.reset_password').after(function(){
        return `<p id='error_id_email' class='invalid-feedback' style='font-weight:bold'></p>`
    })
    $('input.reset_password').keyup(function(){
    clearTimeout(delayTimerEmail);
        delayTimerEmail = setTimeout(function(){
            var text = $('input.reset_password').val();
            console.log(text)
            $.ajax({
                url:'/email/',
                data:{
                    'search_email':text,
                    },
                dataType: 'json',
                success:function(data){
                console.log(data.data)
                var result = data.data
                $('#error_id_email').text('Email: '+result).css({'display':'block','color':'black'})
                $('button').prop('disabled',false)
                var str = $('#error_id_email').text().split(':')[1]
                if (str.length >= 11){
                        $('#error_id_email').css({'color':'red','font-weight':'bold'})
                        $('button').prop('disabled',true)
                    }
                }
            }),1000});
    });
});