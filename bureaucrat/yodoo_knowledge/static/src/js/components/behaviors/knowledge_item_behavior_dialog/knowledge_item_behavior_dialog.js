/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from '@web/core/utils/hooks';
import { Dialog } from '@web/core/dialog/dialog';
import { SelectMenu } from '@web/core/select_menu/select_menu';
import { DropdownItem } from '@web/core/dropdown/dropdown_item';
import { Component, useEffect, onWillStart, useRef, useState } from '@odoo/owl';

export class KnowledgeItemSelectionBehaviorDialog extends Component {

    static template = 'yodoo_knowledge.KnowledgeItemSelectionBehaviorDialog';
    static components = { Dialog, DropdownItem, SelectMenu };
    static props = {
        knowledgeItemSelected: Function,
        close: Function,
        confirmLabel: String,
        title: String,
        parentKnowledgeItemId: { type: Number, optional: true },
    };


    /**
     * @override
     */
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.userService = useService('user');
        this.placeholderLabel = _t('Choose a Knowledge Item...');
        this.toggler = useRef('togglerRef');
        this.state = useState({
            selectedKnowledgeItemName: false,
            knowledgeKnowledgeItems: [],
            createLabel: ''
        });

        //autofocus
        useEffect((toggler) => {
            toggler.click();
        }, () => [this.toggler.el]);

        onWillStart(async () => {
            await this.fetchKnowledgeItems();
            this.state.isInternalUser = await this.userService.hasGroup('base.group_user');
        });
    }

    async createKnowledgeItem(label) {
        const knowledgeItemId = await this.orm.call(
            'yodoo.knowledge.item',
            'create',
            [{name: label}],
        );
        const knowledgeItem = await this.orm.searchRead(
            'yodoo.knowledge.item',
            [["id", "=", knowledgeItemId]],
            ['id', 'display_name', "code"], {
                limit: 20
            });
        this.props.knowledgeItemSelected({
            knowledgeItemId: knowledgeItem.id, 
            knowledgeItemCode: knowledgeItem.code,
            displayName: `📄 ${label}`,
        });
        this.props.close();
    }

    async fetchKnowledgeItems(searchValue) {
        this.state.createLabel = _t('Create "%s"', searchValue);
        const domain = [
            // ['is_template', '=', false]
        ];
        if (searchValue) {
            domain.push(
                '|',
                ['name', '=ilike', `%${searchValue}%`], 
                ['code', '=ilike', `%${searchValue}%`],
            );
        }
        const knowledgeKnowledgeItems = await this.orm.searchRead(
            'yodoo.knowledge.item',
            domain,
            ['id', 'display_name', 'code'], {
                limit: 20
            });
        this.state.knowledgeKnowledgeItems = knowledgeKnowledgeItems.map(({ id, display_name, code }) => {
            return {
                value: {
                    knowledgeItemId: id,
                    knowledgeItemCode: code,
                },
                label: `📄 ${this.truncateString(display_name, 70)}`,
            };
        });
    }
    truncateString(str, maxLength) {
        return str.length > maxLength ? str.slice(0, maxLength-3) + '...' : str;
    }

    async selectKnowledgeItem(value) {
        this.selectedKnowledgeItem = this.state.knowledgeKnowledgeItems.find(knowledgeKnowledgeItem => knowledgeKnowledgeItem.value.knowledgeItemId === value.knowledgeItemId);
        this.state.selectedKnowledgeItemName = this.selectedKnowledgeItem.label;
    }

    confirmKnowledgeItemSelection() {
        this.props.knowledgeItemSelected({
            knowledgeItemId: this.selectedKnowledgeItem.value.knowledgeItemId, 
            knowledgeItemCode: this.selectedKnowledgeItem.value.knowledgeItemCode,
            displayName: this.selectedKnowledgeItem.label,
        });
        this.props.close();
    }

}
