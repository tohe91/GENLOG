var table = $('<table>').addClass('foo');

for(i=0; i<3; i++){
    var row = $('<tr>').addClass('bar').text('result ' + i);
    table.append(row);
}

$('#log').append(table);