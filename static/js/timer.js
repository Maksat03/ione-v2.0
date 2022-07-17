const timerBox = document.getElementById("timerBox");

test_is_final_test = true;
let final_test_was_submitted = false;

const activateTimer = (time) => {
    if (time.toString().length < 2) {
        timerBox.innerHTML = `<b>0${time}:00</b>`
    } else {
        timerBox.innerHTML = `<b>${time}:00</b>`
    }

    let minutes = time - 1
    let seconds = 60
    let displaySeconds
    let displayMinutes

    const timer = setInterval(()=>{
        if (final_test_was_submitted) {
            timerBox.innerHTML = "<b>00:00</b>"
            setTimeout(()=>{
                clearInterval(timer)
            }, 500)
        }
        else {
            seconds --
            if (seconds < 0) {
                seconds = 59
                minutes --
            }
            if (minutes.toString().length < 2) {
                displayMinutes = '0'+minutes
            } else {
                displayMinutes = minutes
            }
            if(seconds.toString().length < 2) {
                displaySeconds = '0' + seconds
            } else {
                displaySeconds = seconds
            }
            if (minutes === 0 && seconds === 0) {
                timerBox.innerHTML = "<b>00:00</b>"
                setTimeout(()=>{
                    clearInterval(timer)
                    alert('Time over')
                    sendData()
                }, 500)
            }

            timerBox.innerHTML = `<b>${displayMinutes}:${displaySeconds}</b>`
        }
    }, 1000)
}