/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";
import { useEffect } from "@odoo/owl";

import { YodooAbstractBehavior } from "@yodoo_knowledge/js/components/behaviors/abstract_behavior";
import { encodeDataBehaviorProps } from "@yodoo_knowledge/js/utils/knowledge_utils";



export class KnowledgeItemBehavior extends YodooAbstractBehavior {
    static defaultProps = {
        isBack: true,
    };
    static props = {
        ...YodooAbstractBehavior.props,
        knowledgeItem_id: { type: Number, optional: false },
        display_name: { type: String, optional: false },
        isBack: { type: Boolean, optional: true },
    };
    static template = "yodoo_knowledge.KnowledgeItemBehavior";

    setup () {
        if (this.props.isBack) {
            super.setup();
            this.actionService = useService('action');
            this.dialogService = useService('dialog');
        }
        useEffect(() => {
            /**
             * @param {Event} event
             */
            const onLinkClick = async event => {
                if (!event.currentTarget.closest('.o_yodoo_knowledge_editor')) {
                    // Use the link normally if not already in Knowledge
                    return;
                }
                event.preventDefault();
                event.stopPropagation();
                // TODO: remove when the model correctly asks the htmlField if
                // it is dirty. This isDirty is necessary because the
                // /knowledgeItem Behavior can be used outside of Knowledge.
                await this.props.record.isDirty();
                this.openKnowledgeItem();
            };
            this.props.anchor.addEventListener('click', onLinkClick);
            return () => {
                this.props.anchor.removeEventListener('click', onLinkClick);
            };
        });
    }

    //--------------------------------------------------------------------------
    // TECHNICAL
    //--------------------------------------------------------------------------

    /**
     * Some `/knowledgeItem` blocks had their behavior-props encoded with
     * `JSON.stringify` instead of `encodeDataBehaviorProps`. This override is
     * there to ensure that props are encoded with the correct format.
     * TODO ABD: this logic should be ultimately part of a knowledge upgrade.
     * @see YodooAbstractBehavior
     * @override
     */
    setupAnchor() {
        super.setupAnchor();
        this.props.anchor.setAttribute('target', '_blank');
        if (!this.props.readonly) {
            try {
                // JSON.parse will crash if the props are already encoded,
                // in that case there is no need to update them.
                this.props.anchor.dataset.behaviorProps = encodeDataBehaviorProps(
                    JSON.parse(this.props.anchor.dataset.behaviorProps)
                );
            } catch {}
        }
    }

    //--------------------------------------------------------------------------
    // HANDLERS
    //--------------------------------------------------------------------------

    async openKnowledgeItem () {
        if (this.props.isBack) {
            try {
                await this.actionService.doAction('yodoo_knowledge.ir_actions_server_yodoo_knowledge_home_page', {
                    additionalContext: {
                        res_id: parseInt(this.props.knowledgeItem_id)
                    }
                });
            } catch {
                this.dialogService.add(AlertDialog, {
                    title: _t('Error'),
                    body: _t("This Knowledge Item was deleted or you don't have the rights to access it."),
                    confirmLabel: _t('Ok'),
                });
            }
        } else {
            window.location.href = `/knowledge/item/${this.props.knowledgeItem_id}`
        }
    }
}
