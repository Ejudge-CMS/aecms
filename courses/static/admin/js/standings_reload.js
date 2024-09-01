(function ($) {
    $(document).ready(function () {
        var contestsField = $('#id_contests');
        var courseField = $('#id_course');
        var typeField = $('#id_type');

        function updateContests() {
            var courseId = courseField.val();
            var type = typeField.val();
            if (!courseId) {
                contestsField.html('');
                return;
            }

            $.ajax({
                url: '/standings_contests/',
                data: {
                    'course_id': courseId,
                    'type': type
                },
                success: function (data) {
                    contestsField.html('');
                    $.each(data.contests, function (index, contest) {
                        var option = $('<option></option>')
                            .attr('value', contest.pk)
                            .text(contest.fields.name);
                        contestsField.append(option);
                    });
                }
            });
        }

        courseField.change(updateContests);
        typeField.change(updateContests);
        updateContests();
    });
})(django.jQuery);
