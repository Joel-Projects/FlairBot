import React from "react";
import SnudownField from "./SnudownField";

const Snudown = require("snudown-js");

export default class CommentField extends SnudownField {

    generateHtml() {
        this.headerDivider = '';
        if (this.state.header) {
            this.headerDivider = '\n\n---\n\n'
        } else {
            this.state.header = ''
        }
        this.footerDivider = '';
        if (this.state.footer) {
            this.footerDivider = '\n\n---\n\n'
        } else {
            this.state.footer = ''
        }
        return `${Snudown.markdown(`${this.state.header}${this.headerDivider}${this.textInput.value}${this.footerDivider}${this.state.footer}`.replaceAll('{subreddit}', this.state.subreddit).replaceAll('{author}', 'spez').replaceAll('{kind}', 'submission').replaceAll('{domain}', 'i.imgur.com').replaceAll('{url}', 'https://redd.it/d0ftu6').replaceAll('{title}', 'For some people, this would be a dream come true.'))}`;
    }
}
