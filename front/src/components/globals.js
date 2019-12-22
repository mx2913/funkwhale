import Vue from 'vue'

function lazyLoad(name) {
    return () => import(/* webpackChunkName: "common-[request]" */ `@/components/common/${name}.vue`)
}

Vue.component('human-date', lazyLoad("HumanDate"))
Vue.component('username', lazyLoad("Username"))
Vue.component('user-link', lazyLoad("UserLink"))
Vue.component('actor-link', lazyLoad("ActorLink"))
Vue.component('actor-avatar', lazyLoad("ActorAvatar"))
Vue.component('duration', lazyLoad("Duration"))
Vue.component('dangerous-button', lazyLoad("DangerousButton"))
Vue.component('message', lazyLoad("Message"))
Vue.component('copy-input', lazyLoad("CopyInput"))
Vue.component('ajax-button', lazyLoad("AjaxButton"))
Vue.component('tooltip', lazyLoad("Tooltip"))
Vue.component('empty-state', lazyLoad("EmptyState"))
Vue.component('expandable-div', lazyLoad("ExpandableDiv"))
Vue.component('collapse-link', lazyLoad("CollapseLink"))
Vue.component('action-feedback', lazyLoad("ActionFeedback"))

export default {}
