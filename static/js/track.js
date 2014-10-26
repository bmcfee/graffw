$(document).ready(function () {
    var myPlayer = videojs('example_video_1');

    var forward = {};

    var timePressedForward = 0;
    var lastDuration = 0;

    $.ajax({
        dataType: "json",
        url: "analysis/1",
        success: onSuccess
    });

    var times = [], durations = [];

    function onSuccess(d) {
        console.log(d);
        forward = d;

        for (var i = 0; i < d.segments.length; i++) {
            var time = d.segments[i].time;
            var duration = d.segments[i].duration;
            times.push(time);
            durations.push(duration);
        }
    }

    $(document).keypress(function (e) {
        if (e.which == 13 && new Date().getTime() - timePressedForward > 1000 * lastDuration) {

            var time = myPlayer.currentTime();

            var nextTime = getNextTime(time, 2).time;
            lastDuration = getNextTime(time, 2).duration;

            myPlayer.currentTime(nextTime);

            timePressedForward = new Date().getTime();
        }
    });

    function getCurrentChunkId(time) {
        for (var i = 0; i < times.length; i++) {
            if (times[i] > time) return i;
        }
    }

    function getNextTime(time, speed) {
        var chunk = getCurrentChunkId(time);
        var nextChunk = forward.forward_map[speed][chunk];
        return {time: times[nextChunk], duration: durations[nextChunk]};
    }

});
