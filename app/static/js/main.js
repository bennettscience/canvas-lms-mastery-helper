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

function showToast(msg, err = false) {
    const toast = document.querySelector(`#toast`)

    // Handle message objects from hyperscript
    // For non-template returns, the backend will also return JSON with
    // the `message` key with details for the user.
    if(typeof msg === 'object') {
        
        // Convert the message to a JSON object
        let obj = JSON.parse(msg.xhr.responseText)
        msg = obj.message
    }
    toast.innerHTML = msg;
    if(err) {
        toast.classList.add('error')
    }
    toast.classList.add('htmx-request');
    setTimeout(() => {
        toast.classList.remove('htmx-request')
        if(err) {
            toast.classList.remove('error')
        }
        toast.innerHTML = "Loading"
    }, 7000)
}

// Handle errors from the server
document.addEventListener('htmx:responseError', (evt) => {
    showToast(evt.detail.xhr.responseText, true)
})

// For debugging requests
document.addEventListener('htmx:beforeSend', function(evt) {
    console.info('Dispatched...')
    console.info(evt.detail)
})

document.addEventListener('htmx:afterRequest', (evt) => {
    console.info('Received...')
    console.info(evt.detail)
})

// Hyperscript can only access global function names. Because this
// is in a module, it has to be assigned explicitely to the 
// Window object.
window.sparkline = drawSparkline;
window.formatDate = formatDate;
window.toast = showToast;