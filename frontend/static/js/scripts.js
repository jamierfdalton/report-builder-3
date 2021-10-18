$(document).ready(function(){
    // html2pdf
    $("#html2pdfbtn").on('submit', function(e){
      e.preventDefault();
      var element = document.getElementById('presentation');
      var opt = {
        html2canvas:  {width:1485},
        jsPDF:        {orientation: 'landscape'}
      }
      html2pdf(element, opt);
    });

    // File upload via Ajax
    $("#uploadForm").on('submit', function(e){
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/upload',
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            // beforeSend: function(){
            //     $('#uploadStatus').html('<img src="images/uploading.gif"/>');
            // },
            error:function(){
                $('#uploadStatus').html('<span style="color:#EA4335;">Images upload failed, please try again.<span>');
            },
            success: function(data){
                $('#uploadForm').html('');
                // $('#uploadStatus').html('<span style="color:#28A74B;">Images uploaded successfully.<span>');
                $(console.log(data))
                $('#gallery1').html(data);
            }
        });
    });

    $("#uploadForm2").on('submit', function(e){
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/upload',
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            // beforeSend: function(){
            //     $('#uploadStatus').html('<img src="images/uploading.gif"/>');
            // },
            error:function(){
                $('#uploadStatus').html('<span style="color:#EA4335;">Images upload failed, please try again.<span>');
            },
            success: function(data){
                $('#uploadForm2').html('');
                // $('#uploadStatus').html('<span style="color:#28A74B;">Images uploaded successfully.<span>');
                $('#gallery2').html(data);
            }
        });
    });

    // File type validation
    $("#fileInput").change(function(){
        var fileLength = this.files.length;
        var match= ["image/jpeg","image/png","image/jpg","image/gif"];
        var i;
        for(i = 0; i < fileLength; i++){
            var file = this.files[i];
            var imagefile = file.type;
            if(!((imagefile==match[0]) || (imagefile==match[1]) || (imagefile==match[2]) || (imagefile==match[3]))){
                alert('Please select a valid image file (JPEG/JPG/PNG/GIF).');
                $("#fileInput").val('');
                return false;
            }
        }
    });
});
