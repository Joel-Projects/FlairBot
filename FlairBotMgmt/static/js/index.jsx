// index.jsx
import ReactDOM from "react-dom";
import React from "react";
import App from "./App";

ReactDOM.render(<App {...(headerEntry.dataset)}/>, document.getElementById("headerEntry"));
ReactDOM.render(<App {...(footerEntry.dataset)}/>, document.getElementById("footerEntry"));