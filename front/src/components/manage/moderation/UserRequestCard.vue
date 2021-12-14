<template>
  <div class="ui fluid user-request card">
    <div class="content">
      <h4 class="header">
        <router-link :to="{name: 'manage.moderation.requests.detail', params: {id: user_request.uuid}}">
          <translate
            translate-context="Content/Moderation/Card/Short"
            :translate-params="{id: user_request.uuid.substring(0, 8)}"
          >
            Request %{ id }
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
                    <actor-link
                      :admin="true"
                      :actor="user_request.submitter"
                    />
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
                      :date="user_request.creation_date"
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
                  <td>
                    <template v-if="user_request.status === 'pending'">
                      <i class="warning hourglass icon" />
                      <translate translate-context="Content/Library/*/Short">
                        Pending
                      </translate>
                    </template>
                    <template v-else-if="user_request.status === 'refused'">
                      <i class="danger x icon" />
                      <translate translate-context="Content/*/*/Short">
                        Refused
                      </translate>
                    </template>
                    <template v-else-if="user_request.status === 'approved'">
                      <i class="success check icon" />
                      <translate translate-context="Content/*/*/Short">
                        Approved
                      </translate>
                    </template>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Content/Moderation/*">
                      Assigned to
                    </translate>
                  </td>
                  <td>
                    <div v-if="user_request.assigned_to">
                      <actor-link
                        :admin="true"
                        :actor="user_request.assigned_to"
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
                      v-if="user_request.handled_date"
                      :date="user_request.handled_date"
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
                    {{ user_request.notes.length }}
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
          <p>
            <translate translate-context="Content/Moderation/Paragraph">
              This user wants to sign-up on your pod.
            </translate>
          </p>
          <template v-if="user_request.metadata">
            <div class="ui hidden divider" />
            <div
              v-for="k in Object.keys(user_request.metadata)"
              :key="k"
            >
              <h4>{{ k }}</h4>
              <p v-if="user_request.metadata[k] && user_request.metadata[k].length">
                {{ user_request.metadata[k] }}
              </p>
              <translate
                v-else
                translate-context="*/*/*"
              >
                N/A
              </translate>
              <div class="ui hidden divider" />
            </div>
          </template>
        </div>
        <aside class="column">
          <div v-if="user_request.status != 'approved'">
            <h3>
              <translate translate-context="Content/*/*/Noun">
                Actions
              </translate>
            </h3>
            <div class="ui labelled icon basic buttons">
              <button
                v-if="user_request.status === 'pending' || user_request.status === 'refused'"
                :class="['ui', {loading: isLoading}, 'button']"
                @click="approve(true)"
              >
                <i class="success check icon" />&nbsp;
                <translate translate-context="Content/*/Button.Label/Verb">
                  Approve
                </translate>
              </button>
              <button
                v-if="user_request.status === 'pending'"
                :class="['ui', {loading: isLoading}, 'button']"
                @click="approve(false)"
              >
                <i class="danger x icon" />&nbsp;
                <translate translate-context="Content/*/Button.Label">
                  Refuse
                </translate>
              </button>
            </div>
          </div>
          <h3>
            <translate translate-context="Content/*/*/Noun">
              Internal notes
            </translate>
          </h3>
          <notes-thread
            :notes="user_request.notes"
            @deleted="handleRemovedNote($event)"
          />
          <note-form
            :target="{type: 'request', uuid: user_request.uuid}"
            @created="user_request.notes.push($event)"
          />
        </aside>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import NoteForm from '@/components/manage/moderation/NoteForm'
import NotesThread from '@/components/manage/moderation/NotesThread'
import showdown from 'showdown'

export default {
  components: {
    NoteForm,
    NotesThread
  },
  props: {
    userRequest: { type: Object, required: true }
  },
  data () {
    return {
      markdown: new showdown.Converter(),
      isLoading: false,
      isCollapsed: false,
      user_request: this.userRequest
    }
  },
  methods: {
    approve (v) {
      const url = `manage/moderation/requests/${this.user_request.uuid}/`
      const self = this
      const newStatus = v ? 'approved' : 'refused'
      this.isLoading = true
      axios.patch(url, { status: newStatus }).then((response) => {
        self.$emit('handled', newStatus)
        self.isLoading = false
        self.user_request.status = newStatus
        if (v) {
          self.isCollapsed = true
        }
        self.$store.commit('ui/incrementNotifications', { count: -1, type: 'pendingReviewRequests' })
      }, () => {
        self.isLoading = false
      })
    },
    handleRemovedNote (uuid) {
      this.user_request.notes = this.user_request.notes.filter((note) => {
        return note.uuid !== uuid
      })
    }
  }
}
</script>
