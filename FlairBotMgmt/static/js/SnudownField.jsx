import React, {Component} from 'react'

const Snudown = require('snudown-js');

export default class SnudownField extends Component {
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
            subreddit: this.props.subreddit
        };
        this.handleLoad = this.handleLoad.bind(this);
    }

    componentDidMount() {
        window.addEventListener('load', this.handleLoad);
        window.comment_box = this
    }

    handleChange(e) {
        this.updateContents();
        this.textInput.style.minHeight = "auto";
    }

    updateContents() {
        if (this.state.subreddit == null) {
            this.state.subreddit = 'pics'
        }
        this.textOutput.innerHTML = this.generateHtml();
        this.newHeight = this.textInput.scrollHeight + 2;
        this.textInput.setAttribute("style", "height:" + this.newHeight + "px");
    }

    generateHtml() {
        return `${Snudown.markdown(this.textInput.value.replaceAll('{subreddit}', this.state.subreddit).replaceAll('{author}', 'spez').replaceAll('{kind}', 'submission').replaceAll('{domain}', 'i.imgur.com').replaceAll('{url}', 'https://redd.it/d0ftu6').replaceAll('{title}', 'For some people, this would be a dream come true.'))}`;
    }

    handleLoad() {
        this.inputLabel.textContent = this.props.name;
        this.previewLabel.textContent = this.state.previewName;
        this.textInput.name = this.state.formName
        this.updateContents();
        this.textInput.style.minHeight = "54px";
    }

    render() {
        return (
            <div>
                <div className={"form-group"} id={this.state.id}>
                    <label ref={(input) => this.inputLabel = input}/>
                    <textarea id={`${this.state.nameLower}input`} defaultValue={this.state.defaultValue} placeholder={this.state.placeholder} onChange={(e) => {
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
