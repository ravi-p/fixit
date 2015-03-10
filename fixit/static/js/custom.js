$(document).ready(function(){
    var act
    processing=0
    backword=0
    forword=1
    sort_by = document.getElementById("uri").value;

$('a#id-del-task').click(function(e){
    var msg = "Do you want to delete task?"
    var isDelete = window.confirm(msg);
    if ( isDelete != true )
        e.preventDefault();
    $(this).closest('form').trigger('submit');
});
$("th").click(function(){ 
    //alert('clicked');
    $(this).children('a')[0].click() 
});
//$('#divtablecontent').bind('scroll', scrollalert);





$('#load_animation').hide();

});

function scrollalert(){
    if (processing==1){
        return false;
    }

        var scrolltop=$("#divtablecontent").scrollTop();
        var fultbl=$('#full-table').height();//updates
        var divtblhgt=$("#divtablecontent").height();//500px
        console.log(scrolltop,fultbl,divtblhgt);
        var point=fultbl-divtblhgt
        if(scrolltop >= point && forword==1){
            act="forword"
            backword=1
            processing=1
            ajax_load(act,scrolltop,point);
        }
        else if(scrolltop <=0  && backword==1) {
            act='backword'
            processing=1
            var point=0
            ajax_load(act,scrolltop,point);
        }
        else{ }
}
function ajax_load(act,scrolltop,point){
    $('#load_animation').show()
    $.ajax({
        type:'get',
        url:"",
        data:{'direction':act},
        success:function(data){
            if(act=="forword"){
                $('#table-body').append(data); //adds data to the end of the table
                var rowsz=$('#full-table tr').length
                if(rowsz%5 != 0){forword=0}
                console.log("after append sz=",rowsz)
                for(i=20;i<rowsz;i++){ document.getElementById('full-table').deleteRow(0)}
                console.log($('#full-table tr').length)
                $('#load_animation').hide()
                $("#divtablecontent").scrollTop(point-50);
                processing=0
                backword=1

            }
            else{
                $('#table-body').prepend(data);
                var rowsz=$('#full-table tr').length
                if(rowsz%5 != 0){backword=0}
                console.log(rowsz)
                for(i=20;i<rowsz;i++){ $('#full-table tr:last').remove(); }
                console.log($('#full-table tr').length)
                $('#load_animation').hide()
                $("#divtablecontent").scrollTop(40);
                processing=0
                forword=1
            
            
            }
        },
        error:function(e,xhr,foo){
            if(e.responseText=="backword"){backword=0}
            else if(e.responseText=="forword"){forword=0}
            else{
			//alert(e.responseText)
		} 
            $('#load_animation').hide()
            processing=0
        },

    });
}
