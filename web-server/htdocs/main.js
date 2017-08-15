function updateOne(name, value)
{
    if (value.toFixed) {
        var str = value.toFixed(2);
        $(name).text(str);
    } else {
        for (var subsensor in value) {
            updateOne(name + "-" + subsensor, value[subsensor]);
        }
    }
}

function gotUpdate(data, textStatus, jqXHR)
{
    console.log(data);
    updateOne("#sensor", data);
    var date = new Date(data['time'] * 1000);
    $("#time-formatted").text(
        date.toLocaleString([], {timeZone: "America/Los_Angeles"}));
}

function update()
{
    $.ajax({url: "/pi-stream/sensors", dataType: "json", success: gotUpdate});
}

$(function() { window.setInterval(update, 1000); });
