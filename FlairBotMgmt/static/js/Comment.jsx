import React from "react";

export default class Comment extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            defaultValue: this.props.text,
            placeHolder: this.props.placeholder,
            name: this.props.id,
            nameLower: this.props.namelower,
            previewName: this.props.previewname,
            formName: this.props.formname
        };
        this.handleLoad = this.handleLoad.bind(this);
    }

    componentDidMount() {
        window.addEventListener('load', this.handleLoad);
    }

    handleChange(e) {
        this.textOutput.innerHTML = `${Snudown.markdown(this.textInput.value)}`;
        this.newHeight = this.textInput.scrollHeight + 2;
        this.textInput.style.minHeight = "auto";
        this.textInput.setAttribute("style", "height:" + this.newHeight + "px");
    }

    handleLoad() {
        this.inputLabel.textContent = this.props.name
        this.previewLabel.textContent = this.state.previewName
        // this.textInput.setAttribute("class", "form-control");
        this.textOutput.innerHTML = `${Snudown.markdown(this.textInput.value)}`;
        this.newHeight = this.textInput.scrollHeight + 2;
        this.textInput.style.minHeight = "54px";
        this.textInput.setAttribute("style", "height:" + this.newHeight + "px");
        this.textInput.name = this.state.formName
        console.log(this.textInput.name = this.state.formName)
    }

    render() {
        return (
            <div>
                <div className={"form-group"} id={this.state.id}>
                    <label ref={(input) => this.inputLabel = input}/>
                    <textarea id={this.state.nameLower + 'input'} defaultValue={this.state.defaultValue} placeholder={this.props.placeholder} onChange={(e) => {
                        this.handleChange(e)
                    }} ref={(input) => this.textInput = input} className={"form-control"}/>
                </div>
                <div className={"form-group"} id={this.state.nameLower + "Preview"}>
                    <label ref={(input) => this.previewLabel = input}/>
                    <div ref={(input) => this.textOutput = input} id={this.state.nameLower + 'output'} style={{color: "#495057", backgroundColor: "#fff", backgroundClip: "paddingBox", border: "1px solid #ced4da", borderRadius: ".25rem", paddingBottom: "6px", paddingLeft: "12px", paddingRight: "12px", paddingTop: "6px", minHeight: "54px"}}/>
                </div>
            </div>
        )
    }
}