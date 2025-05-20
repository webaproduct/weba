/** @odoo-module **/

import { Component } from '@odoo/owl';
import { Wysiwyg } from '@web_editor/js/wysiwyg/wysiwyg';
import {
    isSelectionInSelectors,
    preserveCursor,
    setCursorEnd,
} from "@web_editor/js/editor/odoo-editor/src/utils/utils";
import { renderToElement } from "@web/core/utils/render";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

import { KnowledgeItemSelectionBehaviorDialog } from '@yodoo_knowledge/js/components/behaviors/knowledge_item_behavior_dialog/knowledge_item_behavior_dialog';
import {
    encodeDataBehaviorProps,
} from "@yodoo_knowledge/js/utils/knowledge_utils";

patch(Wysiwyg.prototype, {
    /**
     * @override
     */
    async resetEditor() {
        await super.resetEditor(...arguments);
        this.$editable[0].dispatchEvent(new Event('mount_knowledge_behaviors'));
    },
    /**
     * @override
     */
    _getEditorOptions() {
        const finalOptions = super._getEditorOptions(...arguments);
        const onHistoryResetFromSteps = finalOptions.onHistoryResetFromSteps;
        finalOptions.onHistoryResetFromSteps = () => {
            onHistoryResetFromSteps();
            if (this._onHistoryResetFromSteps) {
                this._onHistoryResetFromSteps();
            }
        };
        return {
            allowCommandFile: true,
            ...finalOptions,
        };
    },
    /**
     * @override
     * @returns {Array[Object]}
     */
    _getPowerboxOptions() {
        const options = super._getPowerboxOptions();
        const {commands, categories} = options;
        categories.push({ name: _t('Media'), priority: 50 });
        commands.push({
            category: _t('Media'),
            name: _t('Knowledge Item'),
            priority: 10,
            description: _t('Link a Knowledge Item'),
            fontawesome: 'fa-file',
            isDisabled: () => this.options.isWebsite || this.options.inIframe,
            callback: () => {
                this._insertKnowledgeItemLink();
            },
        });

        return {...options, commands, categories};
    },
    /**
     * mail is a dependency of Knowledge and @see MailIceServer are a model from
     * mail. When Knowledge is installed, this is always true, meaning that
     * portal users have access to the collaborative mode.
     * @override
     */
    _hasICEServers() {
        return true;
    },
    /**
     * Notify @see FieldHtmlInjector that behaviors need to be injected
     * @see KnowledgeBehavior
     *
     * @param {Element} anchor blueprint for the behavior to be inserted
     * @param {Function} restoreSelection Instructions on where to insert it
     * @param {Function} insert Instructions on how to insert it if it needs
     *                   custom handling
     */
    _notifyNewBehavior(anchor, restoreSelection, insert = null) {
        const type = Array.from(anchor.classList).find(className => className.startsWith('o_yodoo_knowledge_behavior_type_'));
        this.$editable[0].dispatchEvent(new CustomEvent('mount_knowledge_behaviors', { detail: { behaviorData: {
            anchor,
            behaviorType: type,
            shouldSetCursor: true,
            restoreSelection,
            behaviorStatus: 'new',
            insert,
        }}}));
    },
    /**
     * Insert a /knowledgeItem block (through a dialog)
     */
    _insertKnowledgeItemLink: function () {
        const restoreSelection = preserveCursor(this.odooEditor.document);
        Component.env.services.dialog.add(KnowledgeItemSelectionBehaviorDialog, {
            title: _t('Link an Knowledge Item'),
            confirmLabel: _t('Insert Link'),
            knowledgeItemSelected: knowledgeItem => {
                const knowledgeItemLinkBlock = renderToElement('yodoo_knowledge.KnowledgeItemBehaviorBlueprint', {
                    href: `/web#id=${knowledgeItem.knowledgeItemId}&model=yodoo.knowledge.item`,
                    data: encodeDataBehaviorProps({
                        knowledgeItem_id: knowledgeItem.knowledgeItemId,
                        knowledgeItem_code: knowledgeItem.knowledgeItemCode,
                        display_name: knowledgeItem.displayName,
                    }),
                });
                const nameNode = document.createTextNode(knowledgeItem.displayName);
                knowledgeItemLinkBlock.appendChild(nameNode);
                this._notifyNewBehavior(knowledgeItemLinkBlock, restoreSelection);
            },
            parentKnowledgeItemId: this.options.recordInfo.res_model === 'knowledge.knowledgeItem' ? this.options.recordInfo.res_id : undefined
        }, {
            onClose: () => {
                restoreSelection();
            }
        });
    },
    /**
     * Insert a behaviorBlueprint programatically. If the wysiwyg is a part of a
     * collaborative peer to peer connection, ensure that the behaviorBlueprint
     * is properly appended even when the content is reset by the collaboration.
     *
     * @param {HTMLElement} behaviorBlueprint element to append to the editable
     */
    appendBehaviorBlueprint(behaviorBlueprint) {
        const restoreSelection = () => {
            // Set the cursor to the end of the knowledgeItem by not normalizing the position.
            // By not normalizing we ensure that we will use the knowledgeItemś body as the container
            // and not an invisible character.
            return setCursorEnd(this.odooEditor.editable, false);
        }
        const insert = (anchor) => {
            const fragment = this.odooEditor.document.createDocumentFragment();
            // Add a P after the Behavior to be able to continue typing
            // after it
            const p = this.odooEditor.document.createElement('p');
            p.append(this.odooEditor.document.createElement('br'));
            fragment.append(anchor, p);
            const insertedNodes = this.odooEditor.execCommand('insert', fragment);
            if (insertedNodes) {
                insertedNodes[0].scrollIntoView();
                return insertedNodes;
            }
        };
        // Clone behaviorBlueprint to be sure that the nodes are not modified
        // during the first insertion attempt and that the correct nodes
        // are inserted the second time.
        this._notifyNewBehavior(behaviorBlueprint.cloneNode(true), restoreSelection, (anchor) => {
            const insertedNodes = insert(anchor);
            this._onHistoryResetFromSteps = () => {
                this._notifyNewBehavior(behaviorBlueprint.cloneNode(true), restoreSelection, insert);
                this._onHistoryResetFromSteps = undefined;
            };
            return insertedNodes;
        });
        if (behaviorBlueprint.classList.contains('o_knowledge_behavior_type_embedded_view')) {
            this.env.model.root.update({'full_width': true});
        }
    },
});
