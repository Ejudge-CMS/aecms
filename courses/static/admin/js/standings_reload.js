(function ($) {
    $(document).ready(function () {
        var contestsField = $('#id_contests');
        var courseField = $('#id_course');
        var typeField = $('#id_type');
        var markField = $('#id_enable_scoring');

        function updateContests() {

            if (!django.jQuery('#id_enable_scoring').is(':checked')) {
                 django.jQuery(".field-contest_mark_js").hide();
                 django.jQuery(".field-total_mark_js").hide();
                 django.jQuery(".field-prob_js").hide();
            } else {
                 django.jQuery(".field-contest_mark_js").show();
                 django.jQuery(".field-total_mark_js").show();
                 django.jQuery(".field-prob_js").show();
            }

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
        markField.change(updateContests);
        updateContests();
    });
})(django.jQuery);
