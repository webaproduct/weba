/** @odoo-module **/

export function redirectToReqView(req_id) {
    window.location.href = `/requests/${req_id}`
}
