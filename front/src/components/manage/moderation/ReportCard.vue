<template>
  <div class="ui fluid report card">
    <div class="content">
      <h4 class="header">
        <router-link :to="{name: 'manage.moderation.reports.detail', params: {id: report_.uuid}}">
          <translate
            translate-context="Content/Moderation/Card/Short"
            :translate-params="{id: report_.uuid.substring(0, 8)}"
          >
            Report %{ id }
          </translate>
        </router-link>
        <collapse-link
          v-model="isCollapsed"
          class="right floated"
        />
      </h4>
      <div class="content">
        <div class="ui hidden divider" />
        <div class="ui stackable two column grid">
          <div class="column">
            <table class="ui very basic unstackable table">
              <tbody>
                <tr>
                  <td>
                    <translate translate-context="Content/Moderation/*">
                      Submitted by
                    </translate>
                  </td>
                  <td>
                    <div v-if="report_.submitter">
                      <actor-link
                        :admin="true"
                        :actor="report_.submitter"
                      />
                    </div>
                    <div v-else-if="report_.submitter_email">
                      {{ report_.submitter_email }}
                    </div>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="*/*/*">
                      Category
                    </translate>
                  </td>
                  <td>
                    <report-category-dropdown
                      :value="report_.type"
                      @input="update({type: $event})"
                    >
                      &#32;
                      <action-feedback :is-loading="updating.type" />
                    </report-category-dropdown>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Content/*/*/Noun">
                      Creation date
                    </translate>
                  </td>
                  <td>
                    <human-date
                      :date="report_.creation_date"
                      :icon="true"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="column">
            <table class="ui very basic unstackable table">
              <tbody>
                <tr>
                  <td>
                    <translate translate-context="*/*/*">
                      Status
                    </translate>
                  </td>
                  <td v-if="report_.is_handled">
                    <span v-if="report_.is_handled">
                      <i class="success check icon" />
                      <translate translate-context="Content/*/*/Short">Resolved</translate>
                    </span>
                  </td>
                  <td v-else>
                    <i class="danger x icon" />
                    <translate translate-context="Content/*/*/Short">
                      Unresolved
                    </translate>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Content/Moderation/*">
                      Assigned to
                    </translate>
                  </td>
                  <td>
                    <div v-if="report_.assigned_to">
                      <actor-link
                        :admin="true"
                        :actor="report_.assigned_to"
                      />
                    </div>
                    <translate
                      v-else
                      translate-context="*/*/*"
                    >
                      N/A
                    </translate>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Content/*/*/Noun">
                      Resolution date
                    </translate>
                  </td>
                  <td>
                    <human-date
                      v-if="report_.handled_date"
                      :date="report_.handled_date"
                      :icon="true"
                    />
                    <translate
                      v-else
                      translate-context="*/*/*"
                    >
                      N/A
                    </translate>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Content/*/*/Noun">
                      Internal notes
                    </translate>
                  </td>
                  <td>
                    <i class="comment icon" />
                    {{ report_.notes.length }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="!isCollapsed"
      class="main content"
    >
      <div class="ui stackable two column grid">
        <div class="column">
          <h3>
            <translate translate-context="*/*/Field.Label/Noun">
              Message
            </translate>
          </h3>
          <expandable-div
            v-if="report_.summary"
            class="summary"
            :content="report_.summary"
          >
            <div v-html="markdown.makeHtml(report_.summary)" />
          </expandable-div>
        </div>
        <aside class="column">
          <h3>
            <translate translate-context="Content/*/*/Short">
              Reported object
            </translate>
          </h3>
          <div
            v-if="!report_.target"
            role="alert"
            class="ui warning message"
          >
            <translate translate-context="Content/Moderation/Message">
              The object associated with this report was deleted.
            </translate>
          </div>
          <router-link
            v-if="target && configs[target.type].urls.getDetail"
            class="ui basic button"
            :to="configs[target.type].urls.getDetail(report_.target_state)"
          >
            <i class="eye icon" />
            <translate translate-context="Content/Moderation/Link">
              View public page
            </translate>
          </router-link>
          <router-link
            v-if="target && configs[target.type].urls.getAdminDetail"
            class="ui basic button"
            :to="configs[target.type].urls.getAdminDetail(report_.target_state)"
          >
            <i class="wrench icon" />
            <translate translate-context="Content/Moderation/Link">
              Open in moderation interface
            </translate>
          </router-link>
          <table class="ui very basic unstackable table">
            <tbody>
              <tr v-if="target">
                <td>
                  <translate translate-context="Content/Track/Table.Label/Noun">
                    Type
                  </translate>
                </td>
                <td colspan="2">
                  <i :class="[configs[target.type].icon, 'icon']" />
                  {{ configs[target.type].label }}
                </td>
              </tr>
              <tr v-if="report_.target_owner && (!target || target.type !== 'account')">
                <td>
                  <translate translate-context="*/*/*">
                    Owner
                  </translate>
                </td>
                <td>
                  <actor-link
                    :admin="true"
                    :actor="report_.target_owner"
                  />
                </td>
                <td>
                  <instance-policy-modal
                    v-if="!report_.target_owner.is_local"
                    class="right floated mini basic"
                    type="actor"
                    :target="report_.target_owner.full_username"
                  />
                </td>
              </tr>
              <tr v-if="target && target.type === 'account'">
                <td>
                  <translate translate-context="*/*/*/Noun">
                    Account
                  </translate>
                </td>
                <td>
                  <actor-link
                    :admin="true"
                    :actor="report_.target_owner"
                  />
                </td>
                <td>
                  <instance-policy-modal
                    v-if="!report_.target_owner.is_local"
                    class="right floated mini basic"
                    type="actor"
                    :target="report_.target_owner.full_username"
                  />
                </td>
              </tr>
              <tr v-if="report_.target_state.is_local">
                <td>
                  <translate translate-context="Content/Moderation/*/Noun">
                    Domain
                  </translate>
                </td>
                <td colspan="2">
                  <i class="home icon" />
                  <translate translate-context="Content/Moderation/*/Short, Noun">
                    Local
                  </translate>
                </td>
              </tr>
              <tr v-else-if="report_.target_state.domain">
                <td>
                  <router-link :to="{name: 'manage.moderation.domains.detail', params: {id: report_.target_state.domain }}">
                    <translate translate-context="Content/Moderation/*/Noun">
                      Domain
                    </translate>
                  </router-link>
                </td>
                <td>
                  {{ report_.target_state.domain }}
                </td>
                <td>
                  <instance-policy-modal
                    class="right floated mini basic"
                    type="domain"
                    :target="report_.target_state.domain"
                  />
                </td>
              </tr>
              <tr
                v-for="field in targetFields"
                :key="field.id"
              >
                <td>{{ field.label }}</td>
                <td
                  v-if="field.repr"
                  colspan="2"
                >
                  {{ field.repr }}
                </td>
                <td
                  v-else
                  colspan="2"
                >
                  <translate translate-context="*/*/*">
                    N/A
                  </translate>
                </td>
              </tr>
            </tbody>
          </table>
        </aside>
      </div>
      <div class="ui stackable two column grid">
        <div class="column">
          <h3>
            <translate translate-context="Content/*/*/Noun">
              Internal notes
            </translate>
          </h3>
          <notes-thread
            :notes="report_.notes"
            @deleted="handleRemovedNote($event)"
          />
          <note-form
            :target="{type: 'report', uuid: report_.uuid}"
            @created="report_.notes.push($event)"
          />
        </div>
        <div class="column">
          <h3>
            <translate translate-context="Content/*/*/Noun">
              Actions
            </translate>
          </h3>
          <div class="ui labelled icon basic buttons">
            <button
              v-if="report_.is_handled === false"
              :class="['ui', {loading: isLoading}, 'button']"
              @click="resolve(true)"
            >
              <i class="success check icon" />&nbsp;
              <translate translate-context="Content/*/Button.Label/Verb">
                Resolve
              </translate>
            </button>
            <button
              v-if="report_.is_handled === true"
              :class="['ui', {loading: isLoading}, 'button']"
              @click="resolve(false)"
            >
              <i class="warning redo icon" />&nbsp;
              <translate translate-context="Content/*/Button.Label">
                Unresolve
              </translate>
            </button>
            <template
              v-for="(action, key) in actions"
            >
              <dangerous-button
                v-if="action.dangerous && action.show(report_)"
                :key="key"
                :class="['ui', {loading: isLoading}, 'button']"
                :action="action.handler"
              >
                <i :class="[action.iconColor, action.icon, 'icon']" />&nbsp;
                {{ action.label }}
                <p slot="modal-header">
                  {{ action.modalHeader }}
                </p>
                <div slot="modal-content">
                  <p>{{ action.modalContent }}</p>
                </div>
                <p slot="modal-confirm">
                  {{ action.modalConfirmLabel }}
                </p>
              </dangerous-button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import NoteForm from '@/components/manage/moderation/NoteForm'
import NotesThread from '@/components/manage/moderation/NotesThread'
import ReportCategoryDropdown from '@/components/moderation/ReportCategoryDropdown'
import InstancePolicyModal from '@/components/manage/moderation/InstancePolicyModal'
import entities from '@/entities'
import { setUpdate } from '@/utils'
import showdown from 'showdown'

function castValue (value) {
  if (value === null || value === undefined) {
    return ''
  }
  return String(value)
}

export default {
  components: {
    NoteForm,
    NotesThread,
    ReportCategoryDropdown,
    InstancePolicyModal
  },
  props: {
    report: { type: Object, required: true },
    currentState: { type: String, required: false, default: '' }
  },
  data () {
    return {
      report_: this.report,
      markdown: new showdown.Converter(),
      isLoading: false,
      isCollapsed: false,
      updating: {
        type: false
      }
    }
  },
  computed: {
    configs: entities.getConfigs,
    previousState () {
      if (this.report_.is_applied) {
        // mutation was applied, we use the previous state that is stored
        // on the mutation itself
        return this.report_.previous_state
      }
      // mutation is not applied yet, so we use the current state that was
      // passed to the component, if any
      return this.currentState
    },
    detailUrl () {
      if (!this.target) {
        return ''
      }
      let namespace
      const id = this.target.id
      if (this.target.type === 'track') {
        namespace = 'library.tracks.edit.detail'
      }
      if (this.target.type === 'album') {
        namespace = 'library.albums.edit.detail'
      }
      if (this.target.type === 'artist') {
        namespace = 'library.artists.edit.detail'
      }
      return this.$router.resolve({ name: namespace, params: { id, editId: this.report_.uuid } }).href
    },

    targetFields () {
      if (!this.target) {
        return []
      }
      const payload = this.report_.target_state
      const fields = this.configs[this.target.type].moderatedFields
      return fields.map((fieldConfig) => {
        const dummyRepr = (v) => { return v }
        const getValueRepr = fieldConfig.getValueRepr || dummyRepr
        const d = {
          id: fieldConfig.id,
          label: fieldConfig.label,
          value: payload[fieldConfig.id],
          repr: castValue(getValueRepr(payload[fieldConfig.id]))
        }
        return d
      })
    },
    target () {
      if (this.report_.target) {
        return this.report_.target
      } else {
        return this.report_.target_state._target
      }
    },
    actions () {
      if (!this.target) {
        return []
      }
      const self = this
      const actions = []
      const typeConfig = this.configs[this.target.type]
      if (typeConfig.getDeleteUrl) {
        const deleteUrl = typeConfig.getDeleteUrl(this.target)
        actions.push({
          label: this.$pgettext('Content/Moderation/Button/Verb', 'Delete reported object'),
          modalHeader: this.$pgettext('Content/Moderation/Popup/Header', 'Delete reported object?'),
          modalContent: this.$pgettext('Content/Moderation/Popup,Paragraph', 'This will delete the object associated with this report and mark the report as resolved. The deletion is irreversible.'),
          modalConfirmLabel: this.$pgettext('*/*/*/Verb', 'Delete'),
          icon: 'x',
          iconColor: 'danger',
          show: (report) => { return !!report.target },
          dangerous: true,
          handler: () => {
            axios.delete(deleteUrl).then((response) => {
              console.log('Target deleted')
              self.report_.target = null
              self.resolve(true)
            }, () => {
              console.log('Error while deleting target')
            })
          }
        })
      }
      return actions
    }
  },
  methods: {
    update (payload) {
      const url = `manage/moderation/reports/${this.report_.uuid}/`
      const self = this
      this.isLoading = true
      setUpdate(payload, this.updating, true)
      axios.patch(url, payload).then((response) => {
        self.$emit('updated', payload)
        Object.assign(self.report_, payload)
        self.isLoading = false
        setUpdate(payload, self.updating, false)
      }, () => {
        self.isLoading = false
        setUpdate(payload, self.updating, false)
      })
    },
    resolve (v) {
      const url = `manage/moderation/reports/${this.report_.uuid}/`
      const self = this
      this.isLoading = true
      axios.patch(url, { is_handled: v }).then((response) => {
        self.$emit('handled', v)
        self.isLoading = false
        self.report_.is_handled = v
        let increment
        if (v) {
          self.isCollapsed = true
          increment = -1
        } else {
          increment = 1
        }
        self.$store.commit('ui/incrementNotifications', { count: increment, type: 'pendingReviewReports' })
      }, () => {
        self.isLoading = false
      })
    },
    handleRemovedNote (uuid) {
      this.report_.notes = this.report_.notes.filter((note) => {
        return note.uuid !== uuid
      })
    }
  }
}
</script>
