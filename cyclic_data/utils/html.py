

def table(head, body, foot, body_formats=None):
    tab_str = get_pre_table()
    tab_str += '{:4s}<thead>\n'.format('')
    tab_str += table_row(head, encap='th')
    tab_str += '{:4s}</thead>\n'.format('')
    tab_str += '{:4s}<tbody>\n'.format('')
    for b in body:
        tab_str += table_row(b, encap='td', formats=body_formats)
    tab_str += '{:4s}</tbody>\n'.format('')
    tab_str += '{:4s}<tfoot>\n'.format('')
    tab_str += table_row(foot, encap='th')
    tab_str += '{:4s}</tfoot>\n'.format('')
    tab_str += get_post_table()
    return tab_str
    
    
def table_row(contents, encap='td', formats=None):
    row_str = '{:8s}<tr>\n'.format('')
    if formats is None:        
        for content in contents:
            row_str += '{0:12s}<{1:s}>{2:s}</{1:s}>\n'.format('',encap,
                                                              str(content))
    else:
        for content, fmt in zip(contents, formats):
            row_template = '{0:12s}<{1:s}>{2:' + fmt + '}</{1:s}>\n'
            row_str += row_template.format('', encap, content)
    row_str += '{:8s}</tr>\n'.format('')
    return row_str


def get_pre_table():
    return (''
            + '<!DOCTYPE html>\n'
            + '<!Based on https://datatables.net/examples/api/multi_filter.html>\n'
            + '<html>\n'
            + '<head>\n'
            + '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + '\n'
            + '<script src="https://code.jquery.com/jquery-3.5.1.js"></script>\n'
            + '<script src="https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js"></script>\n'
            + '<script src="table.js"></script>\n'
            + '<link rel="stylesheet" href="https://cdn.datatables.net/1.10.23/css/jquery.dataTables.min.css">\n'
            + '<link rel="stylesheet" href="style.css">\n'
            + '\n'
            + '<table id="test_data" class="display" style="width:100%">\n')


def get_post_table():
    return (''
            + '</table>\n'
            + '\n'
            + '</body>\n'
            + '</html>\n')


def get_table_style():
    return (''
            + '/* From https://datatables.net/examples/api/multi_filter.html */\n'
            + 'tfoot input {\n'
            + '        width: 100%;\n'
            + '        padding: 3px;\n'
            + '        box-sizing: border-box;\n'
            + '    }\n'
            + 'td {\n'
            + '  display: table-cell;\n'
            + '  vertical-align: inherit;\n'
            + '  text-align: right;\n'
            + '}\n')


def get_table_script():
    return (''
            + '// From https://datatables.net/examples/api/multi_filter.html\n'
            + '$(document).ready(function() {\n'
            + '    // Setup - add a text input to each footer cell\n'
            + '    $(\'#test_data tfoot th\').each( function () {\n'
            + '        var title = $(this).text();\n'
            + '        $(this).html( \'<input type="text" placeholder="Search \'+title+\'" />\' );\n'
            + '    } );\n'
            + '\n'
            + '    // DataTable\n'
            + '    var table = $(\'#test_data\').DataTable({\n'
            + '        initComplete: function () {\n'
            + '            // Apply the search\n'
            + '            this.api().columns().every( function () {\n'
            + '                var that = this;\n'
            + '\n'
            + '                $( \'input\', this.footer() ).on( \'keyup change clear\', function () {\n'
            + '                    if ( that.search() !== this.value ) {\n'
            + '                        that\n'
            + '                            .search( this.value )\n'
            + '                            .draw();\n'
            + '                    }\n'
            + '                } );\n'
            + '            } );\n'
            + '        }\n'
            + '    });\n'
            + '\n'
            + '} );\n')
