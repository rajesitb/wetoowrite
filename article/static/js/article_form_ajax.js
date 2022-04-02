$(document).ready(function(){
   $("#comment_data").on('submit',function(e){
       e.preventDefault();
        var name = $("#id_name").val();
        var body = $("textarea#id_body").val();
        console.log(body);

        $.ajax({
            url: '/article_comments/',
            type:'POST',
            data:{
                'name':$("#id_name").val(),
                'email':$("#id_email").val(),
                'body':$("#id_body").val(),
                'pk':$("#pk").val(),
            },

            success: function(data){
                var count =$('#number').text();
                console.log(data)
                var next_count = parseInt(count)+1
                $('#number').text('');
                $('#number').text(next_count);
                $('#ajax_comment').append("<p>Comment "+next_count+" By "+data['name']+ "</p>");
                $('#comment_body').append(data['reply']);
                $('button#comment').text('Uploaded');


            }
        });
    });

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



        });



$(document).ready(function(){
    var comment_id = $("#id_com_id").val();

    $(".btn1").click(function(e){

    var btn_id = $(this).attr('id');

    var div = $("#"+btn_id).siblings('div').attr('id');
    console.log(div)
    var form_id = $("#"+div).children('form').attr('id');
    console.log(form_id)
    var h4_id = $("#"+btn_id).siblings('h4').attr('id');
    var span_id = $("#"+btn_id).siblings('span').attr('id');
    var img_id = $("#"+btn_id).siblings('img').attr('id');

    var options = { percent: 50 };
    $('#'+div).css({'display': 'block'})

   $("form#"+form_id).on('submit',function(e){
        e.preventDefault();
        console.log($("#comment_reply_form").serialize())
        var formd=$("form#"+form_id).serialize();
        $.ajax({
            url:"/article_comment_reply/",
            data:formd,
            type:"POST",
            dataType:'json',
            success:function(data){
                $("#"+h4_id).text(data['name'])
                $("#"+span_id).text(data['reply'])

                $("#"+img_id+".posted_img1").css({
                    "display":'block'})
                $("form#"+form_id).css({'display':'none'});
                $('a#'+btn_id).css({'display':'none'});
            }
        })
    });
 });
});

$(document).ready(function(){
    $('form#comment_data').find('label').css({'display':'inline'});
    $('form#comment_data').find('input[name="images"]').prop({"multiple":'true'})
    $('button.reply_edit').click(function(){
    var btn_id = $(this).attr('id')
    var form_id = 'form_'+btn_id;
    var submit_id = 'btn_'+btn_id;
    var content = 'h6.'+btn_id
    var name = 'h6.name_'+btn_id;
    var email = 'h6.email_'+btn_id;
    var text = $(content).text();
    var name_text = $(name).text();
    var email_text = $(email).text();
    console.log(name_text, email_text,text)
        $('textarea#id_body').text(text)

    $('#commentForm_'+btn_id).on('show.bs.modal',function(e){
        $('#'+form_id+' textarea[name="body"]').val(text);
        $('#'+form_id+' input[name="name"]').val(name_text). prop("disabled", true).css({'cursor': 'not-allowed'});

        $('#'+form_id+' input[name="email"]').val(email_text). prop("disabled", true).css({'cursor': 'not-allowed'});
        $('[data-toggle="tooltip"]').tooltip();

        });
            $('#commentForm_'+btn_id).on('submit', function(e){
                $('#'+form_id+' input[name="name"]').val(name_text). prop("disabled", false);
                $('#'+form_id+' input[name="email"]').val(email_text). prop("disabled", false)
            });
        });
    });

$(document).ready(function(){
    $('a.like').click(function(e){
        e.preventDefault();
        $.post('/article-like/',
            {
                id:$(this).data('id'),
                action:$(this).data('action')
            },
        function(data){
            if (data['status'] == 'ok'){
            var like = {src:'/media/outline.png'};
            var unlike = {src:'/media/filled.png'};
            var previous_action=$('a.like').data('action');
            //toggle data-action
                $('a.like').data('action', previous_action == 'like'?
                'unlike':'like');
                //toggle emoji
                previous_action == 'like'? $('a.like img').attr(unlike):$('a.like img').attr(like);
                //update total likes
                var previous_likes=parseInt($('span.count .total').text());
                $('span.count .total strong').text(previous_action == 'like'?
                    previous_likes+1:previous_likes-1);//text
            }//ok status
        }//success function
        );//ajax
    });//click function
});

$(function(){
    $('a.follow').click(function(e){
         e.preventDefault();
        $.post('/article-follow/',
            {
                id:$(this).data('id'),
                action:$(this).data('action')
            },
            function(data){
            console.log(data)
                if (data['status'] == 'ok'){
                    var previous_action = $('a.follow').data('action')
                    var follow = {src:'/media/add.png'};
                    var remove = {src:'/media/remove.png'};
                    console.log(previous_action)
                    //change data-action value
                    $('a.follow').data('action', previous_action == 'follow'? 'unfollow':'follow')
                    console.log($(this).text())
                    //toggle follow text
                    previous_action == 'follow'?  $('a.follow img').attr(remove):$('a.follow img').attr(follow);
                    //follower count
                    var followers = parseInt($('.follow-count .total-follow').text())
                    console.log(followers)
                    $('.follow-count .total-follow strong').text(previous_action == 'follow'? followers+1:followers-1)

                }
            }//function-ajax-success

        )//ajax
    });//click
});//function