/** @odoo-module **/
import { Component, useState, onWillStart, markup, useRef, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { post } from "@web/core/network/http_service";

import { MainComponentsContainer } from "@web/core/main_components_container";

import { startParam } from "../../../features/startParam";
import { redirectToReqView } from "../../../features/utils";

import { CommentList } from "./CommentList/CommentList";
import { CRNDInputTextareaWidget } from "../../common/CRNDInputTextareaWidget/CRNDInputTextareaWidget";
import { CRNDInputTextWidget } from "../../common/CRNDInputTextWidget/CRNDInputTextWidget";



export class RequestsView extends Component {
  static template = "crnd_vsd.RequestsView";
  static components = {
    MainComponentsContainer,
    CommentList,
    CRNDInputTextareaWidget,
    CRNDInputTextWidget,
  }

  CSRFTokenRef = useRef("CSRFTokenRef");

  setup() {
    this.rpc = useService("rpc");
    this.website_id = startParam.website_id;
    this.use_service = startParam.use_service;

    this.state = useState({
        isReqLoaded: false,
      requestId: this.props.request_id,
      requestData: {},
      allowedColumns: [],
      isReqEdit: false,
      editRequestData: {
        title: null,
        text: null,
      },
    })

    this.isAllowed = this.isAllowed.bind(this)
    this.addComment = this.addComment.bind(this)
    this.addFollower = this.addFollower.bind(this)
    this.removeFollower = this.removeFollower.bind(this)
    this.changeReqId = this.changeReqId.bind(this)
    this._updateInputValue = this._updateInputValue.bind(this)


    useExternalListener(window, 'touchstart', this.handleTouchStart.bind(this));
    useExternalListener(window, 'touchmove', this.handleTouchMove.bind(this));
    this.xDown = null;                                                        
    this.yDown = null;


    
    onWillStart(async () => {
      await this.loadRequest();
      await this.getAllowedColumns();
    })
  }

  onClickHome() {
    window.location.href = "/requests"
  }

  clickOnReqName(req_id) {
    redirectToReqView(req_id)
  }

  async changeReqId(req_id) {
    if (!req_id) return
    this.state.requestId = req_id
    await this.loadRequest();

    const url = new URL(window.location.href);
    const newUrl = url.origin + `/requests/${this.state.requestId}` + url.search + url.hash;
    history.pushState(null, '', newUrl);

  }

  toogleReqEdit(value) {
    this.state.isReqEdit = value
    this.state.editRequestData.title = this.state.requestData.title
    this.state.editRequestData.text = this.state.requestData.request_text
  }

  async changeStage(stageId) {
    await this.rpc(`/api/update_request/${this.state.requestId}`, {
      website_id: this.website_id,
      stage_id: stageId
    })
    await this.loadRequest();
  }

  _updateInputValue(name, value) {
    this.state.editRequestData[name] = value
  }

  async saveRequest() {
    await this.rpc(`/api/update_request/${this.state.requestId}`, {
      website_id: this.website_id,
      title: this.state.editRequestData.title,
      request_text: this.state.editRequestData.text,
    })
    await this.loadRequest();
    this.toogleReqEdit(false)
  }


  async sendFiles(files) {
    const attachment_ids = [];
    
    if(!files.length){
      return attachment_ids
    }


    // pack data
    for(let i=0; i<files.length; i++) {
      const file = files[i]
      const data = {
        'name': file.name,
        'file': file,
        'res_id': this.state.requestId,
        'res_model': 'request.request',
        'access_token': false,
        'csrf_token': startParam.csrf_token,
      }
      
      const resp = await post('/portal/attachment/add', data)
      attachment_ids.push(resp.id)
      // await this.rpc('/portal/attachment/add', data)
    }
    
    return attachment_ids
  }

  async addComment(messageText, files) {
    const attachment_ids = await this.sendFiles(files)
    const response = await this.rpc('/api/add_comment_to_request', {
      website_id: this.website_id,
      request_id: this.state.requestId,
      message_text: messageText,
      attachment_ids: attachment_ids,
    })
    if (response.status == 200) {
      await this.loadRequest()
      return true
    }
    return false
  }
  async addFollower(followerId) {
    const response = await this.rpc('/api/add_follower_to_request', {
        website_id: this.website_id,
        request_id: this.state.requestId,
        follower_id: followerId,
      })
      await this.loadRequest()

  }
  async removeFollower(followerId) {
    const response = await this.rpc('/api/remove_follower_for_request', {
      website_id: this.website_id,
      request_id: this.state.requestId,
      follower_id: followerId,
    })
    await this.loadRequest()

  }

  getHtmlText(html_text) {
    return markup(html_text)
  }

  getPriorityStatus(priority_index) {
    return priority_index <= +this.state.requestData.priority
  }

  async getAllowedColumns() {
    const response = await this.rpc('/api/get_allowed_read_blocks', {
        request_id: this.state.requestData?.id
    })
    this.state.allowedColumns = response
  }

  isAllowed(name) {
    return this.state.allowedColumns.includes(name)
  }

  getNavUrl(req_id) {
    if (!req_id) {
      return
    } else {
      return `/requests/${req_id}`
    }
  }

  async loadRequest() {
    this.state.isReqLoaded = false
    const response = await this.rpc(`/api/get_requests/${this.state.requestId}`, {
        website_id: this.website_id,
    })
    this.state.requestData = response.data
    this.state.isReqLoaded = true
  }



  // swipe
    getTouches(evt) {
        return evt.touches ||             // browser API
            evt.originalEvent.touches; // jQuery
    }                                                     
                                                                            
    handleTouchStart(evt) {
        const firstTouch = this.getTouches(evt)[0];                                      
        this.xDown = firstTouch.clientX;                                      
        this.yDown = firstTouch.clientY;                                      
    };                                                
                                                                            
    handleTouchMove(evt) {
        if ( ! this.xDown || ! this.yDown ) {
            return;
        }

        var xUp = evt.touches[0].clientX;                                    
        var yUp = evt.touches[0].clientY;

        var xDiff = this.xDown - xUp;
        var yDiff = this.yDown - yUp;
                                                                            
        if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
            if ( Math.abs( xDiff ) > 9 ) {
                if ( xDiff > 0 ) {
                    /* right swipe */ 
                    this.changeReqId(this.state.requestData.next_record_id)
                } else {
                    /* left swipe */
                    this.changeReqId(this.state.requestData.prev_record_id)
                }                       
            }
        } else {
            if ( yDiff > 0 ) {
                /* down swipe */ 
            } else { 
                /* up swipe */
            }                                                                 
        }
        /* reset values */
        this.xDown = null;
        this.yDown = null;                                             
    };

    onCreateSubReq() {
        window.location.href = `/requests/create?parent_id=${this.state.requestData.id}`
    }
}