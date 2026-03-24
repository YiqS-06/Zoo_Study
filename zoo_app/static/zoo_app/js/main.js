// ZooStudy Main JavaScript
// CSRF token and AJAX URLs are injected by base.html via window.ZOO_CONFIG

$(document).ready(function () {
    initShop();
    initTimer();
    initTaskToggle();
    initNotes();
    initFormWidgets();
});

// --- Shop: AJAX animal purchase ---
function initShop() {
    if (!$('.buy-btn').length) return;

    // Handle buy button click — POST to AJAX endpoint and update UI on success
    $('.buy-btn').on('click', function () {
        const btn = $(this);
        const animalId = btn.data('animal-id');

        btn.prop('disabled', true).text('Buying...');

        $.ajax({
            url: ZOO_CONFIG.urls.buyAnimal,
            method: 'POST',
            data: { animal_id: animalId, csrfmiddlewaretoken: ZOO_CONFIG.csrfToken },
            success: function (data) {
                if (data.success) {
                    showBuyMessage(data.message, 'success');
                    btn.removeClass('buy-btn').addClass('btn-owned').text('✓ Owned');
                    // Refresh coin display and disable buttons the user can no longer afford
                    $('.coin-display').text('🪙 ' + data.currency + ' coins');
                    updateAffordability(data.currency);
                } else {
                    showBuyMessage(data.message, 'error');
                    btn.prop('disabled', false).text('Buy (🪙 ' + btn.data('cost') + ')');
                }
            },
            error: function () {
                showBuyMessage('Something went wrong. Please try again.', 'error');
                btn.prop('disabled', false).text('Buy (🪙 ' + btn.data('cost') + ')');
            }
        });
    });

    // Disable/enable buy buttons based on the user's current coin balance
    function updateAffordability(currency) {
        $('.buy-btn').each(function () {
            const cost = parseInt($(this).data('cost'));
            if (currency < cost) {
                $(this).prop('disabled', true).attr('title', 'Not enough coins');
            } else {
                $(this).prop('disabled', false).removeAttr('title');
            }
        });
    }

    // Show a temporary toast notification in the bottom-right corner
    function showBuyMessage(msg, type) {
        const el = $('#buy-message');
        el.removeClass('success error').addClass(type).text(msg).fadeIn();
        setTimeout(function () { el.fadeOut(); }, 3000);
    }
}

// --- Study Hub: countdown timer with coin tracking ---
function initTimer() {
    if (!$('#timer-display').length) return;

    let timerInterval = null;
    let totalSeconds = 0;
    let running = false;

    // Format seconds as HH:MM:SS
    function formatTime(s) {
        const h = Math.floor(s / 3600);
        const m = Math.floor((s % 3600) / 60);
        const sec = s % 60;
        return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(sec).padStart(2, '0');
    }

    // Update the coins-earned label based on elapsed minutes (10 coins/min)
    function updateCoinsDisplay() {
        const mins = Math.floor(totalSeconds / 60);
        $('#timer-coins').text('🪙 ' + (mins * 10) + ' coins earned');
    }

    $('#btn-start').on('click', function () {
        running = true;
        timerInterval = setInterval(function () {
            totalSeconds++;
            $('#timer-display').text(formatTime(totalSeconds));
            updateCoinsDisplay();
        }, 1000);
        $('#btn-start').hide();
        $('#btn-pause').show();
        $('#btn-stop').show();
    });

    // Toggle between pause and resume
    $('#btn-pause').on('click', function () {
        if (running) {
            clearInterval(timerInterval);
            running = false;
            $('#btn-pause').text('▶ Resume');
        } else {
            timerInterval = setInterval(function () {
                totalSeconds++;
                $('#timer-display').text(formatTime(totalSeconds));
                updateCoinsDisplay();
            }, 1000);
            running = true;
            $('#btn-pause').text('⏸ Pause');
        }
    });

    // Stop timer and POST session duration to server; reload page on success
    $('#btn-stop').on('click', function () {
        clearInterval(timerInterval);
        running = false;
        const minutes = Math.floor(totalSeconds / 60);

        if (minutes < 1) {
            showSessionToast('⚠️ Session too short (minimum 1 minute).');
            resetTimer();
            return;
        }

        $.ajax({
            url: ZOO_CONFIG.urls.logSession,
            method: 'POST',
            data: { duration_minutes: minutes, csrfmiddlewaretoken: ZOO_CONFIG.csrfToken },
            success: function (data) {
                if (data.success) {
                    showSessionToast('🎉 Session saved! +' + data.coins_earned + ' coins | Streak: ' + data.streak + ' days');
                    setTimeout(function () { location.reload(); }, 2500);
                } else {
                    showSessionToast('❌ ' + data.message);
                }
            }
        });

        resetTimer();
    });

    // Reset timer display and button visibility to initial state
    function resetTimer() {
        totalSeconds = 0;
        $('#timer-display').text('00:00:00');
        updateCoinsDisplay();
        $('#btn-start').show();
        $('#btn-pause').hide().text('⏸ Pause');
        $('#btn-stop').hide();
    }

    function showSessionToast(msg) {
        $('#session-toast').text(msg).fadeIn();
        setTimeout(function () { $('#session-toast').fadeOut(); }, 3000);
    }
}

// --- Study Hub: AJAX task completion toggle ---
function initTaskToggle() {
    if (!$('.toggle-btn').length) return;

    // Use event delegation so dynamically-added task buttons also work
    $(document).on('click', '.toggle-btn', function () {
        const btn = $(this);
        const taskId = btn.data('task-id');
        const taskEl = $('#task-' + taskId);

        $.ajax({
            url: ZOO_CONFIG.urls.toggleTask,
            method: 'POST',
            data: { task_id: taskId, csrfmiddlewaretoken: ZOO_CONFIG.csrfToken },
            success: function (data) {
                if (data.success) {
                    if (data.completed) {
                        // Mark task as done without a page reload
                        taskEl.addClass('completed').removeClass('overdue');
                        btn.text('Undo').data('completed', 'true');
                        taskEl.find('.badge-due, .badge-overdue').replaceWith('<span class="badge-done">✓ Done</span>');
                    } else {
                        // Reload to recalculate deadlines when undoing
                        taskEl.removeClass('completed');
                        btn.text('Done').data('completed', 'false');
                        location.reload();
                    }
                }
            }
        });
    });
}

// --- Notes: toggle add-note form visibility per task ---
function initNotes() {
    if (!$('.toggle-form-btn').length) return;

    $('.toggle-form-btn').on('click', function () {
        const targetId = $(this).data('target');
        $('#' + targetId).slideToggle(200);
    });
}

// --- Apply Bootstrap form-control class to Django-rendered form widgets ---
function initFormWidgets() {
    $('input[name="title"]').addClass('form-control');
    $('input[name="deadline"]').addClass('form-control');
}
