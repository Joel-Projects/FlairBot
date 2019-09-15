// index.jsx
import ReactDOM from "react-dom";
import React from "react";
import App from "./App";
import Comment from "./Comment";

ReactDOM.render(<Comment {...(commentEntry.dataset)}/>, document.getElementById("commentEntry"));
ReactDOM.render(<App {...(headerEntry.dataset)}/>, document.getElementById("headerEntry"));
ReactDOM.render(<App {...(footerEntry.dataset)}/>, document.getElementById("footerEntry"));