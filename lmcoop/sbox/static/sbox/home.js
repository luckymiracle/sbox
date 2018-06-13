function vent_control()
{
    value = document.getElementById("vent").value
    $.get('vent/', value);
}

function rotate()
{
    $.get('rotate/');
}

function light()
{
    $.get('light/');
}

function timer()
{
    $.get('timer/', function(data, status){
        var parsed = data.split("~~")
        if (parsed[0].length > 0){
            var parsed_data = parsed[0].split(';')
            for (i=0; i<parsed_data.length; i++) {
                var datasplit = parsed_data[i].split(',')
                if (datasplit.length > 2){
                    if (datasplit[0].length > 9){
                        var x = new Date(datasplit[0]);
                    }
                    else{
                        var x = new Date()
                    }   
                    var y = Number(datasplit[1]);
                    var z = Number(datasplit[2]);
                    //console.log(x)
                    //console.log(datasplit[0].length)
                    //console.log(y)
                    //console.log(z)
                    window.data.push([x, y, z]);
                }
            }
            window.g.updateOptions( { 'file': window.data } );
            document.getElementById("dht_data").innerHTML = "Temperature: " + y + " F<br> Humidity: " + z + "%" + "<br>" + x
        }
        if (parsed[1].length > 2){
            document.getElementById("rot").innerHTML = parsed[1]
        }
        if (parsed[4].length > 2){
            document.getElementById("delta").innerHTML = parsed[4]
        }

        window.setTimeout(timer, 2000)
    })
}

function click_image()
{
    $.get('image/', function(data, status){
        var parsed = data.split("~~")
        document.getElementById("capture").innerHTML = parsed[3]
    })
}

function get_dht(){
    $.get('timer/', function(data, status){
        var parsed = data.split("~~")
        if (parsed[0].length > 0){
            var parsed_data = parsed[0].split(';')
            for (i=0; i<parsed_data.length; i++) {
                var datasplit = parsed_data[i].split(',')
                if (datasplit.length > 2){
                    if (datasplit[0].length > 6){
                        var x = new Date(datasplit[0]);
                    }
                    else{
                        var x = new Date()
                    }   
                    var y = Number(datasplit[1]);
                    var z = Number(datasplit[2]);
                }
            }
            document.getElementById("dht_data").innerHTML = "Temperature: " + y + " F<br> Humidity: " + z + "%" + "<br>" + x
        }
        window.setTimeout(get_dht, 2000)
    })
}
