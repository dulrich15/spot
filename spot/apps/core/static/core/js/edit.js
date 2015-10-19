$('textarea').live('keydown', function(e){
    var keycode = e.which || e.keyCode;
    var key = String.fromCharCode(keycode).toLowerCase()

    if ( keycode == 9 ) // tab
    {
        e.preventDefault();
        var beg = $(this).get(0).selectionStart;
        var end = $(this).get(0).selectionEnd;

        var text = $(this).val()
        if ( beg == end ) {
            beg_text = text.slice(0, beg);
            end_text = text.slice(end);

            if (e.shiftKey) {
                delta = 0;
                if ( beg_text.slice(-1) == ' ' ) { beg_text = beg_text.slice(0,-1); delta += 1; }
                if ( beg_text.slice(-1) == ' ' ) { beg_text = beg_text.slice(0,-1); delta += 1; }
                if ( beg_text.slice(-1) == ' ' ) { beg_text = beg_text.slice(0,-1); delta += 1; }
                if ( beg_text.slice(-1) == ' ' ) { beg_text = beg_text.slice(0,-1); delta += 1; }

                $(this).val(beg_text + end_text);
                $(this).get(0).selectionStart =
                $(this).get(0).selectionEnd = end - delta;
            } else {
                $(this).val(beg_text + '    ' + end_text);
                $(this).get(0).selectionStart =
                $(this).get(0).selectionEnd = end + 4;
            }
        } else {
            var lines = text.split(/\r\n|\r|\n/g);

            var pos = 0;
            var beg_index = -1;
            var end_index = -1;
            for ( var i in lines ) {
                lines[i] += '\r\n';
                pos += lines[i].length - 1;
                if ( pos > beg && beg_index == -1 ) beg_index = i;
                if ( pos > end && end_index == -1 ) end_index = i;
            }
            if ( text.charCodeAt(end - 1) == 10 ) end_index = end_index - 1;

            for ( var i = beg_index; i <= end_index; i++ ) {
                if (e.shiftKey) {
                    var line = lines[i];
                    if ( line.slice(0, 1) == ' ' ) line = line.slice(1);
                    if ( line.slice(0, 1) == ' ' ) line = line.slice(1);
                    if ( line.slice(0, 1) == ' ' ) line = line.slice(1);
                    if ( line.slice(0, 1) == ' ' ) line = line.slice(1);
                    lines[i] = line;
                } else {
                    lines[i] = '    ' + lines[i];
                }
            }

            text = '';
            var beg_pos = 0;
            var end_pos = 0;
            for ( var i in lines ) {
                if ( i == beg_index ) beg_pos = text.length - beg_index;
                text += lines[i];
                if ( i == end_index ) end_pos = text.length - end_index - 2;
            }
            end_pos = end_pos + 1;

            text = text.slice(0,-2);

            $(this).val(text);
            $(this).get(0).selectionStart = beg_pos;
            $(this).get(0).selectionEnd = end_pos;
        }
    }
    if ( e.ctrlKey && ( key == '8' || keycode == 192 ) )
    {
        e.preventDefault();
        if ( key == '8' ) var mark = '*';
        if ( keycode == 192 ) var mark = '`';
        
        var beg = $(this).get(0).selectionStart;
        var end = $(this).get(0).selectionEnd;
        var text = $(this).val()
        
        beg_text = text.slice(0, beg);
        mid_text = text.slice(beg, end);
        end_text = text.slice(end);

        while ( mid_text[0] == ' ' )
        {
            beg = beg + 1
            beg_text = text.slice(0, beg);
            mid_text = text.slice(beg, end);
        }
        
        while ( mid_text[mid_text.length - 1] == ' ' )
        {
            end = end - 1
            mid_text = text.slice(beg, end);
            end_text = text.slice(end);
        }        

        $(this).val(beg_text + mark + mid_text + mark + end_text);
            
        $(this).get(0).selectionStart = beg;
        $(this).get(0).selectionEnd = end + 2 * mark.length;
    }
});
