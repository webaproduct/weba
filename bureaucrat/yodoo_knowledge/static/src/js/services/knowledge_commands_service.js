/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * This service store data from non-knowledge form view records that can be used
 * by a Knowledge form view.
 *
 * A typical usage could be the following:
 * - A form view is loaded and one field of the current record is a match for
 *   Knowledge @see FormControllerPatch
 *   - Information about this record and how to access its form view is stored
 *     in this @see yodooKnowledgeCommandsService .
 * - A knowledge Item is opened and it contains a @see TemplateBehavior .
 *   - When the behavior is injected (@see HtmlFieldPatch ) in the view, it
 *     asks this @see yodooKnowledgeCommandsService if the record can be interacted
 *     with.
 *   - if there is one such record, the related buttons are displayed in the
 *     toolbar of the behavior.
 * - When one such button is used, the form view of the record is reloaded
 *   and the button action is executed through a @see Macro .
 *   - an example of macro action would be copying the template contents as the
 *     value of a field_html of the record, such as "description"
 *
 * Scope of the service:
 *
 * Knowledge macros:
 *
 * 1) @see FormControllerPatch :
 *        It will only be called if the viewed record can be used within the
 *        Knowledge module. Such a record should at least have one html field
 *        that is visible and editable by the current user.
 * 2) @see ChatterPatch :
 *        It will be called if the currently viewed record (in a Form view) has
 *        a chatter which the user can use to attach files or send messages.
 * 3) @see TemplateBehavior or @see FileBehavior :
 *        It will be called by a behavior to check whether it has a record that
 *        can be interacted with in the context of the toolbar, detected through
 *        case 1) and/or 2): canPostMessages, canAttachFiles, withHtmlField.
 *
 * Knowledge external embedded views insertion:
 *
 * 1) @see EmbeddedViewRendererPatch :
 *        Store information related to an Odoo view in the service, in order
 *        to insert it in a Knowledge knowledgeItem body.
 * 2) @see HtmlFieldPatch :
 *        Recover the previously stored information to perform the insertion.
 */
export const yodooKnowledgeCommandsService = {
    start(env) {
        //----------------------------------------------------------------------
        // Knowledge macros features
        //----------------------------------------------------------------------

        // Potential candidate for Knowledge macros.
        let commandsRecordInfo = null;

        /**
         * Register data related to a potential record candidate for Knowledge
         * macros.
         *
         * @param {Object|null} recordInfo if null is given, the
         *        commandsRecordInfo values are reset.
         * @param {number} [recordInfo.resId] id of the target record
         * @param {string} [recordInfo.resModel] model name of the target record
         * @param {Array} [recordInfo.breadcrumbs] array of breadcrumbs objects
         *                {jsId, name} leading to the target record
         * @param {boolean} [recordInfo.canPostMessages] target record
         *                  has a chatter and user can post messages
         * @param {boolean} [recordInfo.canAttachFiles] target record
         *                  has a chatter and user can attach files
         * @param {boolean} [recordInfo.withHtmlField] target record has a
         *                  targeted html field @see FormControllerPatch
         * @param {Object} [recordInfo.fieldInfo] info object for the html field
         *                 {string, name, pageName}
         * @param {XMLDocument} [recordInfo.xmlDoc] xml document (arch of the
         *                      form view of the target record)
         */
        function setCommandsRecordInfo(recordInfo) {
            commandsRecordInfo = recordInfo;
        }

        /**
         * Get the current record candidate that would be used in Knowledge.
         */
        function getCommandsRecordInfo() {
            return commandsRecordInfo;
        }

        /**
         * Copy some actionService breadcrumbs properties used as an identifier
         * for a recordInfo object.
         *
         * @param {Breadcrumbs} breadcrumbs from the @see actionService
         * @returns {Array[Object]} breadcrumbs identifier containing the jsId
         *                          and name.
         */
        function getBreadcrumbsIdentifier(breadcrumbs) {
            return breadcrumbs.map(breadcrumb => {
                return {
                    jsId: breadcrumb.jsId,
                    name: breadcrumb.name,
                };
            });
        }

        /**
         * Evaluate if a record candidate is usable for at least one macro in
         * Knowledge.
         *
         * @param {Object} recordInfo refer to @see setCommandsRecordInfo
         */
        function isRecordCompatibleWithMacro(recordInfo) {
            return recordInfo.canAttachFiles ||
                recordInfo.canPostMessages ||
                recordInfo.withHtmlField;
        }

        /**
         * Compare the provided breadcrumbs identifier with a previously
         * registered recordInfo's and unregister the recordInfo if the
         * registered breadcrumbs are not included at the start of the provided
         * breadcrumbs.
         *
         * @param {Breadcrumbs} breadcrumbs from the @see actionService
         */
        function unregisterCommandsRecordInfo(breadcrumbs) {
            const commandsRecordInfo = getCommandsRecordInfo();
            if (!commandsRecordInfo) {
                return;
            }
            // Extract identifier props from the breadcrumbs.
            breadcrumbs = getBreadcrumbsIdentifier(breadcrumbs);
            if (
                breadcrumbs.length <= commandsRecordInfo.breadcrumbs.length ||
                breadcrumbs[commandsRecordInfo.breadcrumbs.length - 1].jsId !== commandsRecordInfo.breadcrumbs.at(-1).jsId
            ) {
                // Unregister the recordInfo if the target controller does not
                // match what was recorded.
                setCommandsRecordInfo(null);
            }
        }

        //----------------------------------------------------------------------
        // External embedded views features
        //----------------------------------------------------------------------

        let pendingBehaviorBlueprints = {};

        /**
         * @param {Object}
         * @param {HTMLElement} behaviorBlueprint element to be inserted in a
         *                      html field
         * @param {string} model model name of the target record
         * @param {string} field field name of the target record
         * @param {integer} resId id of the target record
         */
        function setPendingBehaviorBlueprint({behaviorBlueprint, model, field, resId}) {
            if (!(model in pendingBehaviorBlueprints)) {
                pendingBehaviorBlueprints[model] = {};
            }
            if (!(field in pendingBehaviorBlueprints[model])) {
                pendingBehaviorBlueprints[model][field] = {};
            }
            pendingBehaviorBlueprints[model][field][resId] = behaviorBlueprint;
        }

        function popPendingBehaviorBlueprint({model, field, resId}) {
            if (model in pendingBehaviorBlueprints && field in pendingBehaviorBlueprints[model]) {
                const pendingBehaviorBlueprint = pendingBehaviorBlueprints[model][field][resId];
                delete pendingBehaviorBlueprints[model][field][resId];
                return pendingBehaviorBlueprint;
            }
        }

        const yodooKnowledgeCommandsService = {
            setCommandsRecordInfo,
            getCommandsRecordInfo,
            getBreadcrumbsIdentifier,
            isRecordCompatibleWithMacro,
            unregisterCommandsRecordInfo,
            setPendingBehaviorBlueprint,
            popPendingBehaviorBlueprint,
        };
        return yodooKnowledgeCommandsService;
    }
};

registry.category("services").add("yodooKnowledgeCommandsService", yodooKnowledgeCommandsService);
