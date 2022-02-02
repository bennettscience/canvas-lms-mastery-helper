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

// Listen for new elements in lists and inititalize HTMX on them
htmx.onLoad((detail) => console.log(detail))

// Hyperscript can only access global function names. Because this
// is in a module, it has to be assigned explicitely to the 
// Window object.
window.sparkline = drawSparkline;
window.formatDate = formatDate;