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
                url: '/admin/get-standings-contests/',  // You'll need to create this view
                data: {
                    'course_id': courseId,
                    'type': type
                },
                success: function (data) {
                    contestsField.html('');
                    $.each(data.contests, function (index, contest) {
                        var option = $('<option></option>')
                            .attr('value', contest.id)
                            .text(contest.name);
                        contestsField.append(option);
                    });
                }
            });
        }

        contestsField.change(updateContests);
        updateTags();
    });
})(django.jQuery);
