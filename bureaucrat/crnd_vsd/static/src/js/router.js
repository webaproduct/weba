/** @odoo-module **/

import { RequestsList } from './components/MainContent/RequestsList/RequestsList.js';
import { RequestCreate } from './components/MainContent/RequestCreate/RequestCreate.js';
import { RequestsView } from './components/MainContent/RequestsView/RequestsView.js';

export function getComponentToRoute(path) {
  let return_data = {
    component: null,
    props: {},
  }

  if (path == '/requests') {
    return_data.component = RequestsList
  } else if (path == '/requests/create') {
    return_data.component = RequestCreate
  } else if (path.includes('/requests/')) {
    let req_id = path.split('/requests/').at(-1)
    req_id = +req_id
    return_data.component = RequestsView
    return_data.props = {"request_id": req_id}
  }

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