


def table(head, body, foot, body_formats=None):
    tab_str = '{:4s}<thead>\n'.format('')
    tab_str += table_row(head, encap='th')
    tab_str += '{:4s}</thead>\n'.format('')
    tab_str += '{:4s}<tbody>\n'.format('')
    for b in body:
        tab_str += table_row(b, encap='td', formats=body_formats)
    tab_str += '{:4s}</tbody>\n'.format('')
    tab_str += '{:4s}<tfoot>\n'.format('')
    tab_str += table_row(foot, encap='th')
    tab_str += '{:4s}</tfoot>\n'.format('')
    
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