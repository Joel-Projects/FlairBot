// index.jsx
import ReactDOM from "react-dom";
import React from "react";
import App from "./App";
import Comment from "./Comment";

try {
    ReactDOM.render(<Comment {...(commentEntry.dataset)}/>, document.getElementById("commentEntry"))
} catch (e) {
    console.log(e)
}
try {
    ReactDOM.render(<App {...(headerEntry.dataset)}/>, document.getElementById("headerEntry"))
} catch (e) {
    console.log(e)
}
try {
    ReactDOM.render(<App {...(footerEntry.dataset)}/>, document.getElementById("footerEntry"))
} catch (e) {
    console.log(e)
}