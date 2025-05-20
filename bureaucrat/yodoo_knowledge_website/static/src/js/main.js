/** @odoo-module **/

import { mount } from '@odoo/owl';
import {templates} from '@web/core/assets';
import { getComponentToRoute, removeLocaleFromPath } from "./router.js";

async function getEnv() {
    let env = null;
    while (!env) {
        env = await new Promise((resolve) => {
            setTimeout(() => {
                resolve(owl.Component.env);
            }, 200);
        });
    }
    return env;
}

const elem = document.getElementById('yodoo_knowledge_website_anchor_owl');
if (!elem) return;

elem.innerHTML = "";

const loader = document.getElementById('loader');
if (loader) loader.style.display = 'none';

owl.whenReady(async () => {
    const env = await getEnv();
    const { component, props } = getComponentToRoute(removeLocaleFromPath(document.location.pathname))

    mount(component, elem, {
        env,
        templates,
        props,
    });
})













// import { App } from "@odoo/owl";
// import { makeEnv, startServices } from "@web/env";
// import { browser } from "@web/core/browser/browser";
// // import { mount } from "@web/../tests/helpers/utils";

// import { templates } from "@web/core/assets";
// import { _t } from "@web/core/l10n/translation";

// owl.whenReady(async () => {
//     const env = makeEnv();
//     await startServices(env);

//     const mainContent = document.getElementById("yodoo_knowledge_website_anchor_owl")
//     const { component, props } = getComponentToRoute(removeLocaleFromPath(document.location.pathname))

//     const app = new App(component, {
//         templates,
//         env: env,
//         props: props,
//         dev: env.debug,
//         translateFn: _t,
//     });
//     app.mount(mainContent);

// });

// /**
//  * This code is iterating over the cause property of an error object to console.error a string
//  * containing the stack trace of the error and any errors that caused it.
//  * @param {Event} ev
//  */
// function logError(ev) {
//     ev.preventDefault();
//     let error = ev?.error || ev.reason;

//     if (error.seen) {
//         // If an error causes the mount to crash, Owl will reject the mount promise and throw the
//         // error. Therefore, this if statement prevents the same error from appearing twice.
//         return;
//     }
//     error.seen = true;

//     let errorMessage = error.stack;
//     while (error.cause) {
//         errorMessage += "\nCaused by: ";
//         errorMessage += error.cause.stack;
//         error = error.cause;
//     }
//     console.error(errorMessage);
// }

// browser.addEventListener("error", (ev) => {
//     logError(ev);
// });
// browser.addEventListener("unhandledrejection", (ev) => {
//     logError(ev);
// });
