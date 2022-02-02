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

// Handle errors from the server
document.addEventListener('htmx:responseError', (evt) => {
    let toast = document.querySelector(`#toast`)
    toast.innerHTML = evt.detail.xhr.responseText;
    toast.classList.add('htmx-request', 'error');
    setTimeout(() => {
        toast.classList.remove('htmx-request', 'error')
        toast.innerHTML = "";
    }, 7000
})

document.addEventListener('error', (evt) => { console.log(evt)})

// For debugging requests
// document.addEventListener('htmx:beforeSend', function(evt) {
//     console.log(evt.detail)
// })

// Hyperscript can only access global function names. Because this
// is in a module, it has to be assigned explicitely to the 
// Window object.
window.sparkline = drawSparkline;
window.formatDate = formatDate;