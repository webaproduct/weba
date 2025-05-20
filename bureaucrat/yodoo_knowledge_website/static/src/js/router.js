/** @odoo-module **/

import { Reader } from "./pages/Reader/Reader";

export function getComponentToRoute(path) {
    let return_data = {
        component: Reader,
        props: {},
    }

    // if (path == '/knowledge') {
    //     return_data.component = Reader
    // }

    return return_data;
}

export function removeLocaleFromPath(pathname) {
    // Проверяем, начинается ли путь с префикса локали (например, /en/ или /uk/)
    const localeRegex = /^\/(en|uk|fr|de|ru)\//; // Перечисли локали, которые у тебя используются
    const match = pathname.match(localeRegex);
    if (match) {
        // Возвращаем путь без префикса локали
        return pathname.replace(localeRegex, '/');
    }
    return pathname; // Если локаль не найдена, возвращаем исходный путь
}