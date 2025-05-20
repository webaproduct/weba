/** @odoo-module **/
import { transliterationMap } from "./consts";


export function makeDashedTransliteratedString(str) {    
    const cirillicRegex = /^[а-яєіїґ]$/;
    const alphaNumericRegex = /^[a-z0-9]$/;
    let outStr = '';

    str = str.toLowerCase();
    for (const char of str) {
        if (cirillicRegex.test(char)) {
            outStr += transliterationMap[char];
            continue;
        }

        if (alphaNumericRegex.test(char)) {
            outStr += char;
            continue;
        }

        outStr += '-';
    }

    return outStr[outStr.length - 1] === '-' ? outStr.slice(0, -1) : outStr;
}

export function changeUrlWithoutRedirect(code, text) {
    const url = new URL(window.location.href);
    
    const dashedTransliteratedString = makeDashedTransliteratedString(text)
    const newUrl = url.origin + `/knowledge/item/${code}/${dashedTransliteratedString}` + url.search + url.hash;
    history.pushState(null, '', newUrl);
}

export function updateMetaTag(property, content) {
    let meta = document.querySelector(`meta[property='${property}']`);
    if (meta) {
        meta.setAttribute("content", content);
    } else {
        meta = document.createElement("meta");
        meta.setAttribute("property", property);
        meta.setAttribute("content", content);
        document.head.appendChild(meta);
    }
}

export function decodeDataBehaviorProps(dataBehaviorPropsAttribute) {
    return JSON.parse(decodeURIComponent(dataBehaviorPropsAttribute));
}

export function highlightSearchDocs(searchDocs, searchString) {
    searchDocs.forEach(doc => {
        const docName = doc.name;
        const docNameToSearch = docName.toLowerCase();

        const index = docNameToSearch.indexOf(searchString.toLowerCase());
        if (index === -1) return;

        const highlightedName = docName.substring(0, index)
            + '<span class="highlighted">'
            + docName.substring(index, index + searchString.length) 
            + '</span>' + docName.substring(index + searchString.length);
        doc.name = markup(highlightedName);
    });

    return searchDocs;
}