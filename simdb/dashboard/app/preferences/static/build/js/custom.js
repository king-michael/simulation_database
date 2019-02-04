/**
 * Functions which should be added to custom.js
 *
 */

// Table Box to show Databases
 $(document).on('click','.delete-link',function() {

     if ( $(this).hasClass('disabled') ) {
         return;
     }

     var $TABLE_ROW = $(this).closest('.entry');

     var id = $TABLE_ROW.find('.db_table_id').text();

     $TABLE_ROW.remove();

     $.get("/preferences/delete_db_from_table", {id: id});
 });

 $(document).on('click','.confirm-link',function() {

     if ( $(this).hasClass('disabled') ) {
         return;
     }

    var $TABLE_ROW = $(this).closest('.entry');

    // get rows
    var $ID = $TABLE_ROW.find('.db_table_id');
    var $NAME = $TABLE_ROW.find('.db_table_name');
    var $PATH = $TABLE_ROW.find('.db_table_path');
    var $COMMENT = $TABLE_ROW.find('.db_table_comment');

    var id = $ID.text();
    var name = $NAME.find('.form-control').val();
    var path = $PATH.find('.form-control').val();
    var comment = $COMMENT.find('.form-control').val();

    $.ajax({
        url: "/preferences/edit_db_table",
        data: {
            id: id,
            name: name,
            path: path,
            comment: comment
        },
        dataType: "text",
        success: function(data){
            $ID.html(data);
        }

    });

    $NAME.html(name);
    $PATH.html(path);
    $COMMENT.html(comment);

    $TABLE_ROW.find('.fa-check').addClass('fa-edit').removeClass('fa-check');
    $TABLE_ROW.find('.confirm-link').addClass('edit-link').removeClass('confirm-link');

    $TABLE_ROW.find('.select-link').removeClass('disabled');

 });

 $(document).on('click','.edit-link',function() {

     if ( $(this).hasClass('disabled') ) {
         return;
     }

    var $TABLE_ROW = $(this).closest('.entry');

    var name = $TABLE_ROW.find('.db_table_name').text();
    var path = $TABLE_ROW.find('.db_table_path').text();
    var comment = $TABLE_ROW.find('.db_table_comment').text();

    $TABLE_ROW.find('.db_table_name').html("<input type='text' required='required' class='form-control db_name_field'>");
    $TABLE_ROW.find('.db_table_name').find('input').val(name);

    $TABLE_ROW.find('.db_table_path').html("<input type='text' required='required' class='form-control db_path_field'>");
    $TABLE_ROW.find('.db_table_path').find('input').val(path);

    $TABLE_ROW.find('.db_table_comment').html("<input type='text' class='form-control db_comment_field'>");
    $TABLE_ROW.find('.db_table_comment').find('input').val(comment);

    $TABLE_ROW.find('.fa-edit').addClass('fa-check').removeClass('fa-edit');
    $TABLE_ROW.find('.edit-link').addClass('confirm-link').removeClass('edit-link');

    $TABLE_ROW.find('.select-link').addClass('disabled');
 });

 $(document).on('click','.select-link',function() {

     if ( $(this).hasClass('disabled') ) {
         return;
     }

     var $TABLE_ROW = $(this).closest('.entry');

    var $ID = $TABLE_ROW.find('.db_table_id');
    var $NAME = $TABLE_ROW.find('.db_table_name');
    var $PATH = $TABLE_ROW.find('.db_table_path');

    var id = $ID.text();
    var name = $NAME.text();
    var path = $PATH.text();

     $.ajax({
        url: "/preferences/select_db",
        data: {id: id},
        dataType: "text",
        success: function(data){
            $('.selected-db').not($TABLE_ROW).removeClass('selected-db');
            $TABLE_ROW.toggleClass('selected-db');
            if ( data === "selected") {
                $('.footer_status .fa-unlink').addClass('fa-link').removeClass('fa-unlink');
                $('.footer_status .db_name').html(name);
                $('.footer_status .db_path').html( "( " + path + " )");
            } else {
                $('.footer_status .fa-link').addClass('fa-unlink').removeClass('fa-link');
                $('.footer_status .db_name').html("No database selected");
                $('.footer_status .db_path').html("");
            }
        }

     });

     $('#database_table .edit-link').not($TABLE_ROW.find('.edit-link')).removeClass('disabled')
     $('#database_table .delete-link').not($TABLE_ROW.find('.delete-link')).removeClass('disabled')
     $TABLE_ROW.find('.edit-link').toggleClass('disabled');
     $TABLE_ROW.find('.delete-link').toggleClass('disabled');

 });

$(document).ready(function() {
    // top panel
    // add DB path button

    $('.add-link').click(function () {

        var $BOX_PANEL = $(this).closest('.x_panel');
        var $BOX_TABLE = $BOX_PANEL.find('#database_table tbody')

        var out = "<tr class='entry'>";
            out += "<td class='db_table_id hidden'></td>";
            out += "<td class='db_table_name'><input type='text' required='required' class='form-control db_name_field'></td>";
            out += "<td class='db_table_path'><input type='text' required='required' class='form-control db_path_field'></td>";
            out += "<td class='db_table_comment'><input type='text'                  class='form-control db_comment_field'></td>";
            out += "<td class='db_table_toolbox'>";
            out += "<ul class='nav navbar-right panel_toolbox'>";
            out += "<li><a class='select-link disabled'><i class='fa fa-circle'></i></a></li>";
            out += "<li><a class='confirm-link'><i class='fa fa-check'></i></a></li>";
            out += "<li><a class='delete-link'><i class='fa fa-times'></i></a></li>";
            out += "</ul></td>";
            out += "</tr>";

        $BOX_TABLE.append(out);

    });
});
// Table Box to show Databases
