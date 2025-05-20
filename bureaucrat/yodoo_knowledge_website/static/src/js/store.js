/** @odoo-module */

import { reactive, useState } from "@odoo/owl";

export function useStoredState(key, initialState = {}) {
    const state = JSON.parse(sessionStorage.getItem(key)) || initialState;
    const store = (obj) => sessionStorage.setItem(key, JSON.stringify(obj));
    const reactiveState = reactive(state, () => store(reactiveState));
    store(reactiveState);
    return useState(state);
}