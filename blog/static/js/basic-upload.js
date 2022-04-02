$(function () {

  $(".js-upload-photos").click(function () {
    $("#fileupload").click();
  });

  $("#fileupload").fileupload({
    dataType: 'json',
    done: function (e, data) {
      if (data.result.is_valid) {
        $("#box").prepend(

        '<a href='+ data['url'] + ' ><img class=" img-fluid img-thumbnail" src=' +  data['url']+" ></a>"

        )}
    }
  });

});
