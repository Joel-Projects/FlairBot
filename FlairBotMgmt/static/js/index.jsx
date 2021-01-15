// index.jsx
import { render } from 'react-dom'
import React from "react";
import SnudownField from "./SnudownField";
import Comment from "./Comment";

try {
    render(<Comment {...(commentEntry.dataset)}/>, document.getElementById("commentEntry"))
} catch (e) {
    console.log(e)
}
try {
    render(<SnudownField {...(headerEntry.dataset)}/>, document.getElementById("headerEntry"))
} catch (e) {
    console.log(e)
}
try {
    render(<SnudownField {...(footerEntry.dataset)}/>, document.getElementById("footerEntry"))
} catch (e) {
    console.log(e)
}