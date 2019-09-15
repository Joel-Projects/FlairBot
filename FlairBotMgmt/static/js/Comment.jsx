import React from "react";

const Snudown = require('snudown-js');

export default class App extends React.Component {
    namelower;
    previewname;
    formname;
    constructor(props) {
        super(props);
        this.state = {
            defaultValue: this.props.text,
            placeHolder: this.props.placeholder,
            name: this.props.id,
            nameLower: this.props.namelower,
            previewName: this.props.previewname,
            formName: this.props.formname,
            header: this.props.header,
            footer: this.props.footer,
            subreddit: this.props.subreddit
        };
        this.handleLoad = this.handleLoad.bind(this);
    }

    componentDidMount() {
        window.addEventListener('load', this.handleLoad);
    }

    handleChange(e) {
        this.textOutput.innerHTML = this.generateHtml();
        this.newHeight = this.textInput.scrollHeight + 2;
        this.textInput.style.minHeight = "auto";
        this.textInput.setAttribute("style", `height:${this.newHeight}px`);
        console.log(this.textInput.style.minHeight)
    }

    handleLoad() {
        this.inputLabel.textContent = this.props.name;
        this.previewLabel.textContent = this.state.previewName;
        this.textInput.name = this.state.formName;
        this.textOutput.innerHTML = this.generateHtml();

        this.textInput.style.minHeight = "54px";

        console.log(this.textInput.style.minHeight)
    }

    generateHtml() {
        this.headerDivider = '';
        if (this.state.header) {
            this.headerDivider = '\n\n---\n\n'
        }
        this.footerDivider = '';
        if (this.state.footer) {
            this.footerDivider = '\n\n---\n\n'
        }
        return `${Snudown.markdown(`${this.state.header}${this.headerDivider}${this.textInput.value}${this.footerDivider}${this.state.footer}`.replace('{subreddit}', this.state.subreddit).replace('{author}', 'spez').replace('{kind}', 'submission').replace('{domain}', 'i.imgur.com').replace('{url}', 'https://redd.it/d0ftu6').replace('{title}', 'For some people, this would be a dream come true.'))}`;
    }

    render() {
        return (
            <div>
                <div className={"form-group"} id={this.state.id}>
                    <label ref={(input) => this.inputLabel = input}/>
                    <textarea id={`${this.state.nameLower}input`} defaultValue={this.state.defaultValue} placeholder={this.props.placeholder} onChange={(e) => {
                        this.handleChange(e)
                    }} ref={(input) => this.textInput = input} className={"form-control"}/>
                </div>
                <div className={"form-group"} id={`${this.state.nameLower}Preview`}>
                    <label ref={(input) => this.previewLabel = input}/>
                    <div ref={(input) => this.textOutput = input} id={`${this.state.nameLower}output`} style={{color: "#495057", backgroundColor: "#fff", backgroundClip: "paddingBox", border: "1px solid #ced4da", borderRadius: ".25rem", paddingTop: "6px", paddingLeft: "12px", paddingBottom: "6px", paddingRight: "12px", minHeight: "54px"}}/>
                </div>
            </div>
        )
    }
}
