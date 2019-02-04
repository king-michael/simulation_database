
function buildFilter(){
    // collect selected options
    // call build_filter
    // get available options as json back
    // update filter

    // get selected groups
    var selected_groups = [];
    $( "#select_group" ).find("input:checkbox:checked").each(function() {
        selected_groups.push($(this).val());
    });

    // get selected keywords
    var selected_keywords = [];
    $( "#select_keyword" ).find("input:checkbox:checked").each(function() {
        selected_keywords.push($(this).val());
    });

    // get selected keyword values
    var selected_keyword_values = [];
    $( "#select_keyword_value" ).find("input:checkbox:checked").each(function() {
        selected_keyword_values.push($(this).val());
    });

    // get search query
    var search_query = $( "#search_field" ).val();

    $.ajax({
        url: "build_filter",                 // call the search page
        data: {
            search_query: search_query,
            selected_group: selected_groups.join(","),
            selected_keyword: selected_keywords.join(","),
            selected_keyword_value: selected_keyword_values.join(",")
        },     // get results from search page by sending value
        dataType: "json",
        success: function(data){

            // fill groups
            var out = "";
            if(data.groups.length == 0) {

                out += "<p class='scrollable-group-placeholder'>No Groups found</p>";
            } else {
                for(i in data.groups) {

                    var for_display = data.groups[i] + " (" + data.groupscount[i] + ")";

                    out += "<label class='btn btn-default'>";
                    out += "<input type='checkbox' name='options' value='" + data.groups[i] + "'>" + for_display;
                    out += "</label>";
                }
            }

            $( "#select_group" ).html(out); // push options to html

            $( "#select_group" ).find( "input:checkbox" ).each(function(){
                // set checkboxes to active which were selected
                if(  selected_groups.includes($(this).val()) ){
                    $(this).prop("checked", true);
                    $(this).parent().addClass("active");
                }
            });

            // add click function:
            // detect if ctr key was pressed
            $("#select_group label").click(function(event) {
                if( ! event.ctrlKey ) {
                    $("#select_group label").not(this).children().prop("checked", false);
                    $( "#select_keyword_value label" ).not($(this)).removeClass("active");
                }
            });


            // keywords
            var out = "";
            if(data.keywords.length == 0) {

                out += "<p class='scrollable-group-placeholder'>No Keywords found</p>";
            } else {

                for(i in data.keywords) {

                    var for_display = data.keywords[i] + " (" + data.keywordscount[i] + ")";

                    out += "<label class='btn btn-default'>";
                    out += "<input type='checkbox' name='options' value='" + data.keywords[i] + "'>" + for_display;
                    out += "</label>";
                }
            }

            $( "#select_keyword" ).html(out); // push options to html

            $( "#select_keyword" ).find( "input:checkbox" ).each(function(){
                // set checkboxes to active which were selected
                if( selected_keywords.includes($(this).val()) ){
                    $(this).prop("checked", true);
                    $(this).parent().addClass("active");
                }
            });

            // add click function:
            // detect if ctr key was pressed
            $("#select_keyword label").click(function(event) {
                if( ! event.ctrlKey ) {
                    $("#select_keyword label").not(this).children().prop("checked", false);
                    $( "#select_keyword_value label" ).not($(this)).removeClass("active");
                }
            });


            // keyword values
            var out = "";
            if(data.values.length == 0) {

                out += "<p class='scrollable-group-placeholder'>No Values found</p>";
            } else {

                for(i in data.values) {

                    var for_display = data.values[i] // + " (" + data.keywordscount[i] + ")";

                    out += "<label class='btn btn-default'>";
                    out += "<input type='checkbox' name='options' value='" + data.values[i] + "'>" + for_display;
                    out += "</label>";
                }
            }

            $("#select_keyword_value").html(out); // push options to html

            // add click function:
            // detect if ctr key was pressed
            $("#select_keyword_value label").click(function(event) {
                if( ! event.ctrlKey ) {
                    $("#select_keyword_value label").not(this).children().prop("checked", false);
                    $( "#select_keyword_value label" ).not($(this)).removeClass("active");
                }
            });

        }

    });
}


function filterTable(){
    // collect selected options
    // call filter view
    // get table as HTML code back

    // get selected table
    var db_path = $('#select_database input:radio:checked').val();

    // get selected group
    var selected_group = $('#select_group input:checkbox:checked').val();
    if(selected_group == undefined) {
        selected_group = "";
    }

    // get selected keyword
    var selected_keyword = $('#select_keyword input:checkbox:checked').val();
    if(selected_keyword == undefined) {
        selected_keyword = "";
    }

    // get selected keyword value
    var selected_keyword_value = $( "#select_keyword_value" ).val();

    // get search query
    var search_query = $( "#search_field" ).val();


    // get selected columns with bootstrap select
    var selected_columns = "";
    $( "#select_columns" ).find("option:selected").each(function() {
        selected_columns = selected_columns + " " + $(this).val();
    });

    // get sort by key
    var sort_ascending = $( ".sort_ascending" ).attr("id");
    var sort_descending = $( ".sort_descending" ).attr("id");
    if(sort_ascending == undefined){
        sort_ascending = "";
    }
    if(sort_descending == undefined){
        sort_descending = "";
    }

    //value = value.trim(); // remove any spaces around the text
        $.ajax({
            url: "filter",                 // call the search page
            data: {                        // get results from search page by sending value
                db_path: db_path,
                search_query: search_query,
                selected_group: selected_group,
                selected_keyword: selected_keyword,
                selected_keyword_value: selected_keyword_value,
                sort_ascending: sort_ascending,
                sort_descending: sort_descending,
                selected_columns: selected_columns
            },
            dataType: "html",
            success: function(data){
                $('#database_entries .x_content').html(data);  // push resulting table to something with id=results
                $('#database_entries table').dataTable( {
                    dom: 'fBrtip',
                    "paging": false,
                    buttons: [
                        {
                            extend: 'csv',
                            text: "<i class='fas fa-file-csv' aria-hidden='true'></i>"
                        },
                        {
                            extend: 'print',
                            text: "<i class='fa fa-print' aria-hidden='true'></i>"
                        },
                        {
                            extend: 'colvis',
                            columns: ':gt(0)',
                            text: "<i class='fa fa-bars fa-rotate-90' aria-hidden='true'></i>"
                        }
                    ]
                } );
            }

        });
}


$(document).ready(function() {
   buildFilter();
   filterTable();
});