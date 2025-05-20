/** @odoo-module **/
import { Component, useState, onWillStart, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadWysiwygFromTextarea } from "./load";


import { CRNDInputWidget } from "../CRNDInputWidget";
import { startParam } from "../../../features/startParam";


export class CRNDInputTextareaWidget extends CRNDInputWidget {
    static template = 'crnd_vsd.CRNDInputTextareaWidget'

    setup() {
        this.crnd_textarea = useRef('crnd_textarea_wysiwyg')
        this.website_id = startParam.website_id;

        this.loadWysiwygStructure = this.loadWysiwygStructure.bind(this)
        this.updateInputValue = this.updateInputValue.bind(this)

        onMounted(() => {
            var options = {
                value: this.props.default_value,
                autohideToolbar: true,
                toolbarTemplate: 'website_forum.web_editor_toolbar',
                toolbarOptions: {
                    showColors: false,
                    showFontSize: false,
                    showHistory: true,
                    showHeading1: false,
                    showHeading2: false,
                    showHeading3: false,
                    showLink: false,
                    showImageEdit: false,
                },
                recordInfo: {
                    context: {
                        website_id: this.website_id,
                    },
                },
                placeholder: this.props.placeholder,
                resizable: true,
                userGeneratedContent: true,
                height: 350,
            };
            this.loadWysiwygStructure()
            loadWysiwygFromTextarea(this, this.crnd_textarea.el, options).then(wysiwyg => {
                this.wysiwyg = wysiwyg

                this.addObservers()
            });
        })

        this.props._updateInputValue(this.props.name, this.props.default_value || this.props._form_value || '')
    }
    
    addObservers() {
        const observer = new MutationObserver(mutations => {
            this.updateInputValue()
        });
    
        observer.observe(this.wysiwyg.$editable[0], { childList: true, characterData: true, subtree: true });
    }

    updateInputValue() {
        const text = this.wysiwyg.getValue();
        this.props._updateInputValue(this.props.name, text)
    }

    loadWysiwygStructure() {
        var textarea = this.crnd_textarea.el;
        var wrapper = document.createElement('div');
        wrapper.classList.add('position-relative', 'o_wysiwyg_textarea_wrapper');

        var loadingElement = document.createElement('div');
        loadingElement.classList.add('o_wysiwyg_loading');
        var loadingIcon = document.createElement('i');
        loadingIcon.classList.add('text-600', 'text-center',
            'fa', 'fa-circle-o-notch', 'fa-spin', 'fa-2x');
        loadingElement.appendChild(loadingIcon);
        wrapper.appendChild(loadingElement);

        textarea.parentNode.insertBefore(wrapper, textarea);
        wrapper.insertBefore(textarea, loadingElement);
    }

}