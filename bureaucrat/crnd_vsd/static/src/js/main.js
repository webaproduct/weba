/** @odoo-module **/

import { App } from "@odoo/owl";
import { makeEnv, startServices } from "@web/env";
import { Component } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
// import { mount } from "@web/../tests/helpers/utils";

import { getComponentToRoute, removeLocaleFromPath } from "./router.js";
import { templates } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";

owl.whenReady(async () => {
  const env = makeEnv();
  await startServices(env);

  const mainContent = document.getElementById("crnd_vsd_anchor_owl")
  const {component, props} = getComponentToRoute(removeLocaleFromPath(document.location.pathname))

  Component.env = env;
  const app = new App(component, {
    templates,
    env: env,
    props:props,
    dev: env.debug,
    translateFn: _t,
  });
  app.mount(mainContent);

});

//   mount(getComponentToRoute(document.location.pathname), mainContent, {
//     env,
//     templates,
//     dev: env.debug,
//   });
// });

/**
 * This code is iterating over the cause property of an error object to console.error a string
 * containing the stack trace of the error and any errors that caused it.
 * @param {Event} ev
 */
function logError(ev) {
  ev.preventDefault();
  let error = ev?.error || ev.reason;

  if (error.seen) {
    // If an error causes the mount to crash, Owl will reject the mount promise and throw the
    // error. Therefore, this if statement prevents the same error from appearing twice.
    return;
  }
  error.seen = true;

  let errorMessage = error.stack;
  while (error.cause) {
    errorMessage += "\nCaused by: ";
    errorMessage += error.cause.stack;
    error = error.cause;
  }
  console.error(errorMessage);
}

browser.addEventListener("error", (ev) => {
  logError(ev);
});
browser.addEventListener("unhandledrejection", (ev) => {
  logError(ev);
});
