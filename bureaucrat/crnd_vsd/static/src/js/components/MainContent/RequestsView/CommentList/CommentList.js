/** @odoo-module **/
import { Component, useState, onWillStart, markup } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { FileLoader } from "../../../common/FileLoader/FileLoader";

import { CRNDInputTextareaWidget } from "../../../common/CRNDInputTextareaWidget/CRNDInputTextareaWidget";
import { CRNDInputSelectWidget } from "../../../common/CRNDInputSelectWidget/CRNDInputSelectWidget";


export class CommentList extends Component {
  static template = "crnd_vsd.CommentList";
  static components = {
    CRNDInputTextareaWidget,
    CRNDInputSelectWidget,
    FileLoader,
  }

  setup() {
    this.rpc = useService("rpc");

    this.state = useState({
      commentFormData: {
        messageText: null,
      },
      files: [],
      openForm: false,
      isFollowersOpenForm: false,
      followerForAdd: 0,
      availableFollowers: [],
    })

    this._updateNewCommentValue = this._updateNewCommentValue.bind(this)
    this.updateFilesList = this.updateFilesList.bind(this)
    this.removeFile = this.removeFile.bind(this)

    onWillStart(async () => {
        await this.getListOfAvailableFollowers();
    })
  }

  onOpenForm() {
    this.state.isFollowersOpenForm = false
    this.state.openForm = true
  }
  onCloseForm() {
    this.state.openForm = false
    this.state.commentFormData.messageText = null
    this.state.files = []
  }
  toggleOpenFollowersForm() {
      this.state.openForm = false
      this.state.isFollowersOpenForm = !this.state.isFollowersOpenForm
  }

  _updateNewCommentValue(name, value) {
    this.state.commentFormData.messageText = value
  }
  getHtmlText(html_text) {
    return markup(html_text)
  }

  updateFilesList(files) {
    this.state.files = files
    console.log(this.state.files)
  }
  removeFile(file) {
    this.state.files = this.state.files.filter(x => x.name != file.name && x.size != file.size)
  }

  isEnabledSave() {
    return !!(this.state.files.length || this.state.commentFormData.messageText) 
  }

  async addComment() {
    if (this.state.commentFormData.messageText || this.state.files.length) {
      const status = await this.props.addComment(this.state.commentFormData.messageText, this.state.files)
      console.log(status)
      this.onCloseForm()
    }
  }

  async addFollower(follower) {
    if (follower) {
        await this.props.addFollower(follower)
        this.state.followerForAdd = 0
        this.state.followerForAdd = null
        await this.getListOfAvailableFollowers()
    }
  }

  async getListOfAvailableFollowers() {
    const responseFollowersList = await this.rpc('/api/get_available_followers', {
        website_id: this.website_id,
        request_id: this.props.requestId,
    })
    if (responseFollowersList.length) {
        this.state.availableFollowers = responseFollowersList.map(item => ({
            value: item.id,
            name: item.display_name,
        }))
    }
  }
}