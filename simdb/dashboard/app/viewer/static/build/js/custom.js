
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


    $.ajax({
        url: "build_filter",                 // call the search page
        data: {
            // search_query: search_query,
            selected_groups: selected_groups.join(","),
            selected_keywords: selected_keywords.join(",")
        },     // get results from search page by sending value
        dataType: "json",
        success: function(data){

            // fill groups
            var out = "";
            if(data.groups.length == 0) {

                out += "<p class='scrollable-group-placeholder'>No Groups found</p>";
            } else {
                for(i in data.groups) {

                    var for_display = data.groups[i] + " (" + data.group_counts[i] + ")";

                    if(  selected_groups.includes(data.groups[i]) ){
                        out += "<label class='btn btn-default active'>";
                        out += "<input type='checkbox' name='options' value='" + data.groups[i] + "' checked>" + for_display;
                        out += "</label>";
                    } else {
                        out += "<label class='btn btn-default'>";
                        out += "<input type='checkbox' name='options' value='" + data.groups[i] + "'>" + for_display;
                        out += "</label>";
                    }
                }
            }

            $( "#select_group" ).html(out); // push options to html

            // keywords
            var out = "";
            if(data.keywords.length == 0) {

                out += "<p class='scrollable-group-placeholder'>No Keywords found</p>";
            } else {

                for(i in data.keywords) {

                    var for_display = data.keywords[i] + " (" + data.keyword_counts[i] + ")";

                    if(  selected_keywords.includes(data.keywords[i]) ){
                        out += "<label class='btn btn-default active'>";
                        out += "<input type='checkbox' name='options' value='" + data.keywords[i] + "' checked>" + for_display;
                        out += "</label>";
                    } else {
                        out += "<label class='btn btn-default'>";
                        out += "<input type='checkbox' name='options' value='" + data.keywords[i] + "'>" + for_display;
                        out += "</label>";
                    }
                }
            }

            $( "#select_keyword" ).html(out); // push options to html

            // keyword values
            var out = "";
            if(data.values.length == 0) {

                out += "<p class='scrollable-group-placeholder'>No Values found</p>";
            } else {

                for(i in data.values) {

                    var for_display = data.values[i]  + " (" + data.value_counts[i] + ")";

                    if(  selected_keyword_values.includes(data.values[i]) ){
                        out += "<label class='btn btn-default active'>";
                        out += "<input type='checkbox' name='options' value='" + data.values[i] + "' checked>" + for_display;
                        out += "</label>";
                    } else {
                        out += "<label class='btn btn-default'>";
                        out += "<input type='checkbox' name='options' value='" + data.values[i] + "'>" + for_display;
                        out += "</label>";
                    }
                }
            }

            $("#select_keyword_value").html(out); // push options to html

        }

    });
}


function filterTable(){
    // collect selected options
    // call filter view
    // get table as HTML code back

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

    $.ajax({
        url: "filter",                 // call the search page
        data: {                        // get results from search page by sending value
            selected_groups: selected_groups.join(","),
            selected_keywords: selected_keywords.join(","),
            selected_keyword_values: selected_keyword_values.join(",")
        },
        dataType: "html",
        success: function(data){
            $('#database_entries .x_content').html(data);  // push resulting table to something with id=results

            $('#database_entries table').dataTable( {

                // bootstrap 4 style
                dom: "<'row'<'col-sm-12 col-md-6'f><'col-sm-12 col-md-6'B>>" +
                     "<'row'<'col-sm-12 col-md-12'pl>>" +
                     "<'row'<'col-sm-12'tr>>" +
                     "<'row'<'col-sm-12 col-md-5'i>>",

                // disable visibility of dates by default
                'columnDefs': [
                   { targets: [2, 3, 4], visible: false }
                ],

                "language": {
                    "search": "<i class='fas fa-search'></i>"
                },

                buttons: [
                    {
                        extend: 'csv',
                        text: "<i class='fas fa-file-csv' aria-hidden='true'></i>",
                        titleAttr: 'Export CSV'
                    },
                    {
                        extend: 'print',
                        text: "<i class='fa fa-print' aria-hidden='true'></i>",
                        titleAttr: 'Print'
                    },
                    {
                        extend: 'colvis',
                        columns: ':gt(0)',
                        text: "<i class='fa fa-bars fa-rotate-90' aria-hidden='true'></i>",
                        titleAttr: 'Show Columns'
                    }
                ]

            });

        }

    });
}

// run on start up
$(document).ready(function() {
   buildFilter();
   filterTable();
});

// filter Table after group was selected
$('#select_group').change(function() {
    buildFilter();
    filterTable();
});

// filter Table after keyword was selected
$('#select_keyword').change(function() {
    buildFilter();
    filterTable();
});

// filter table after selection of column has changed
$('#select_keyword_value').change(function () {
    filterTable();
});

// buttons for selection
// $( "#select_keyword" ).find( "input:checkbox" ).each(function(){
//     // set checkboxes to active which were selected
//     if( selected_keywords.includes($(this).val()) ){
//         $(this).prop("checked", true);
//         $(this).parent().addClass("active");
//     }
// });

// $( "#select_group" ).find( "input:checkbox" ).each(function(){
//     // set checkboxes to active which were selected
//     if(  selected_groups.includes($(this).val()) ){
//         $(this).prop("checked", true);
//         $(this).parent().addClass("active");
//     }
// });



$(document).on('click','#select_group label',function(event) {
    if( ! event.ctrlKey ) {
        $( "#select_group label" ).not($(this)).children().prop("checked", false);
        $( "#select_group label" ).not($(this)).removeClass("active");
    }
});

$(document).on('click','#select_keyword label',function(event) {
    if( ! event.ctrlKey ) {
        $("#select_keyword label").not($(this)).children().prop("checked", false);
        $( "#select_keyword label" ).not($(this)).removeClass("active");

        $("#select_keyword_value label").children().prop("checked", false);
        $( "#select_keyword_value label" ).removeClass("active");
    }
});

$(document).on('click','#select_keyword_value label',function(event) {
    if( ! event.ctrlKey ) {
        $("#select_keyword_value label").not($(this)).children().prop("checked", false);
        $( "#select_keyword_value label" ).not($(this)).removeClass("active");
    }
});