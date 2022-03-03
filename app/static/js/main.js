import sparkline from "./modules/sparkline.js"

function drawSparkline(el, data) {
    console.log(`chart requested!`)
    sparkline(el, data)
}

// Format a date for display
function formatDate(target, strDate) {

    let date = new Date(strDate)
    
    const formats = {
        dateOnly: {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric'
        },
    }
    
    return new Intl.DateTimeFormat('en', formats[target]).format(date)
}

function showToast(msg, timeout = 3000, err = false) {
    const toast = document.querySelector(`#toast p`)

    // Handle message objects from hyperscript
    // For non-template returns, the backend will also return JSON with
    // the `message` key with details for the user.
    if(typeof msg === 'object') {
        // HTMX returns strings, so convert it to an object
        let obj = JSON.parse(msg.xhr.responseText)
        msg = obj.message
    }

    toast.innerText = msg;
    if(err) {
        toast.parentNode.classList.add('error')
    }
    toast.parentNode.classList.add('htmx-request');
    setTimeout(() => {
        toast.parentNode.classList.remove('htmx-request')
        toast.innerText = 'Loading...'
        if(err) {
            toast.parentNode.classList.remove('error')
        }
    }, timeout)
}

// Handle errors from the server
document.addEventListener('htmx:responseError', (evt) => {
    showToast(evt.detail.xhr.responseText, true)
})

// document.addEventListener('htmx:beforeSend', (evt) => {
//     showToast('Loading...')
// })

// For debugging requests
// document.addEventListener('htmx:beforeSend', function(evt) {
//     console.info('Dispatched...')
//     console.info(evt.detail)
// })

// Hyperscript can only access global function names. Because this
// is in a module, it has to be assigned explicitely to the 
// Window object.
window.sparkline = drawSparkline;
window.formatDate = formatDate;
window.toast = showToast;