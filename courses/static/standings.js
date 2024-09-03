let _dom_loaded = false;
let _data = null;

document.addEventListener('DOMContentLoaded', function () {
    _dom_loaded = true;
    buildStandings();
});

(function() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/standings_data/' + standings_label, true);
    xhr.responseType = 'json';
    xhr.onload = function () {
        let status = xhr.status;
        if (status === 200) {
            _data = xhr.response;
            buildStandings();
        } else {
            loadFailed();
        }
    };
    xhr.send();
})();

var addCell = function(row, text, klass, rowSpan, colSpan) {
    let cell = row.insertCell();
    cell.innerHTML = text;
    cell.className = klass || '';
    cell.rowSpan = rowSpan || 1;
    cell.colSpan = colSpan || 1;
    return cell;
};

var loadFailed = function() {
    alert('Не удалось получить таблицу результатов!');
};

var compareUsers = function(a, b) {
    if (a['score'] !== b['score']) {
        return b['score'] - a['score'];
    }
    if (a['penalty'] !== b['penalty']) {
        return a['penalty'] - b['penalty'];
    }
    return a['name'].localeCompare(b['name']);
};

var calculateInformation = function(users, contests) {
    users.forEach(function(user) {
        let id = user['id'];
        user['score'] = 0.0;
        user['penalty'] = 0;
        user['scores'] = [];
        contests.forEach(function(contest, idc) {
            let sc = 0;
            contest['users'][id].forEach(function(result) {
                sc += result['score'];
                if (result['score'] !== 0) {
                    user['penalty'] += result['penalty'];
                }
            });
            user['score'] += sc;
            user['scores'].push(sc);
        });
    });
};

var getScoreColor = function(score) {
    score = Math.min(score, 100);
    let red = parseInt(240 + (144 - 240) * Math.sqrt(score / 100));
    let green = parseInt(128 + (238 - 128) * Math.sqrt(score / 100));
    let blue = parseInt(128 + (144 - 128) * Math.sqrt(score / 100));
    return 'rgb(' + red + ',' + green + ',' + blue + ')';
};

var addProblemCell = function(row, problem) {
    let score = problem['score'];
    let penalty = problem['penalty'];
    if (is_olymp) {
        let text;
        if (score === 0 && penalty === 0) {
            text = '';
        } else {
            text = score;
        }
        let cell = addCell(row, text, 'gray');
        if (text !== '') {
            cell.style.backgroundColor = getScoreColor(score);
        }
    } else {
        const add_inf = function (text) {
            return '<p class="small">' + text + '&infin;</p>';
        };
        if (problem['verdict'] === 'OK') {
            let text = '+';
            if (penalty > 0) {
                if (penalty <= 9) {
                    text += penalty;
                } else {
                    text = add_inf(text);
                }
            }
            let cell = addCell(row, text, 'ok');
            if (penalty > 9) {
                cell.title = '+' + penalty;
            }
        } else if (problem['verdict'] === 'SM') {
            let cell = addCell(row, '<div></div>', 'gray defense');
            cell.title = 'Вызвано на защиту';
        } else if (problem['verdict'] === 'SV') {
            let cell = addCell(row, '<div></div>', 'gray ban');
            cell.title = 'Нарушение правил оформления программ';
        } else if (problem['verdict'] === 'PD') {
            let cell = addCell(row, '?', 'gray');
            cell.title = 'Ожидает проверки';
            cell.style.backgroundColor = '#ffdc33';
        } else if (problem['verdict'] === 'DQ') {
            let cell = addCell(row, 'ᕁ_ᕁ', 'gray');
            cell.title = 'Дисквалифицированно';
            cell.style.backgroundColor = "#808080";
        } else {
            if (penalty === 0) {
                addCell(row, '', 'gray');
            } else {
                let text = '-';
                if (penalty <= 9) {
                    text += penalty;
                } else {
                    text = add_inf(text);
                }
                let cell = addCell(row, text, 'bad');
                if (penalty > 0) {
                    cell.title = '-' + penalty;
                }
            }
        }
    }
};

var addHeader = function(holder, contests) {
    let header_row1 = holder.insertRow();
    let header_row2 = holder.insertRow();
    addCell(header_row1, 'Место', '', 2, 1);
    addCell(header_row1, 'Фамилия и имя', '', 2, 1);
    addCell(header_row1, (is_olymp ? 'Балл' : 'Решено'), '', 2, 1);
    if (!is_olymp) {
        addCell(header_row1, 'Штраф', '', 2, 1);
    }

    if (contests.length === 0) {
        addCell(header_row1, '', 'invisible contest_title');
        addCell(header_row2, '', 'invisible');
    }

    contests.forEach(function(contest, idx) {
        let problems = contest['problems'];
        let title_text = contest['title'];
        let title;
        if (contest_id === -1) {
            title = '<a href="./' + (contests.length - 1 - idx) + '/">' + title_text + '</a>';
        } else {
            title = title_text;
        }
        addCell(header_row1, title, 'gray contest_title', 1, problems.length + 1);
        problems.forEach(function(problem) {
            let cell = addCell(header_row2, problem['short'], 'problem_letter gray');
            cell.title = problem['long'];
        });
        addCell(header_row2, 'Σ', 'problem_letter gray');
    });
};

var fixColumnWidths = function (objs) {
    let results_pos = objs[0].childNodes[0].childNodes.length;
    objs[0].childNodes[0].childNodes.forEach(function (column, idx) {
        if (column.classList.contains('gray')) {
            results_pos = Math.min(results_pos, idx);
        }
    });
    let max_width = {};
    objs.forEach(function (obj) {
        obj.childNodes.forEach(function (row, row_idx) {
            let add = 0;
            if (row_idx === 1) {
               add = results_pos
            }
            let first = row_idx === 0;
            row.childNodes.forEach(function (column, idx) {
                if (first && idx >= results_pos) {
                    return;
                }
                let width = column.clientWidth;
                if ((idx + add) in max_width) {
                    max_width[idx + add] = Math.max(max_width[idx + add], width);
                } else {
                    max_width[idx + add] = width;
                }
            });
        })
    });
    objs.forEach(function(obj) {
        obj.childNodes.forEach(function(row, row_idx) {
            let add = 0;
            if (row_idx === 1) {
               add = results_pos
            }
            let first = row_idx === 0;
            row.childNodes.forEach(function (column, idx) {
                if (first && idx >= results_pos) {
                    return;
                }
                if (!column.classList.contains("invisible")) {
                    column.style.minWidth = max_width[idx + add] + 'px';
                }
            });
        });
    });
};

var addBody = function(body, users, contests) {
    for (let i = 0; i < users.length; i++) {
        let user = users[i];
        let id = user['id'];
        let row = body.insertRow();
        addCell(row, i + 1);
        addCell(row, user['name'], 'name');
        addCell(row, user['score']);
        if (!is_olymp) {
            addCell(row, user['penalty']);
        }
        contests.forEach(function (contest, idx) {
            let problems = contest['users'][id];
            problems.forEach(function (problem) {
                addProblemCell(row, problem);
            });
            let text = user['scores'][idx];
            if (user['scores'][idx] === 0) {
                text = ""
            }
            let cell = addCell(row, text, 'gray');
        });
    }
};

var buildStandings = function() {
    if (!_dom_loaded) {
        return;
    }
    if (!_data) {
        return;
    }
    let data = _data;
    let contests = data['contests'];
    if (contest_id !== -1) {
        if (contest_id < 0 || contest_id >= contests.length) {
            alert('Wrong contest id!');
        }
        contests = [contests[contests.length - 1 - contest_id]];
        data['contests'] = contests;
    }

    let users = data['users'];
    calculateInformation(users, contests);
    users.sort(compareUsers);

    let table = document.getElementById('standings');
    let header = document.createElement('thead');
    let body = document.createElement('tbody');
    table.appendChild(header);
    table.appendChild(body);
    let table_fixed = document.getElementById('standings_fixed');
    let body_fixed = document.createElement('tbody');
    table_fixed.appendChild(body_fixed);
    addHeader(header, contests);
    addHeader(body, contests);
    addBody(body, users, contests);
    addHeader(body_fixed, []);
    addBody(body_fixed, users, []);
    fixColumnWidths([header, body_fixed, body], contests);

    document.getElementsByClassName('wrapper')[0].addEventListener('scroll', function(e) {
        header.style.marginLeft = -e.target.scrollLeft + 'px';
    });

    let rotating_elements = document.getElementsByClassName("rotating");
    for (let i = 0; i < rotating_elements.length; i++) {
        let el = rotating_elements[i];
        let ang = 0;
        setInterval(function() {
            ang += 1;
            ang %= 360;
            el.style.transform = "rotate(-" + ang + "deg)";
        }, 10);
    }
};
