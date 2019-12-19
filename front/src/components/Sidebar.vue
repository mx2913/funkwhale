<template>
<aside :class="['ui', 'vertical', 'left', 'visible', 'wide', {'collapsed': isCollapsed}, 'sidebar',]">
  <header class="ui inverted segment header-wrapper">
    <router-link :title="'Funkwhale'" :to="{name: logoUrl}">
      <i class="logo bordered inverted orange big icon">
        <logo class="logo"></logo>
      </i>
    </router-link>
    <nav class="top ui compact left aligned text menu title-menu" v-if="!$store.state.auth.authenticated">
      <router-link class="item" :to="{name: logoUrl}">
        Funkwhale
      </router-link>
    </nav>
    <nav class="top ui compact right aligned grey text menu">
      <template v-if="$store.state.auth.authenticated">

        <div class="right menu">
          <div class="item" :title="labels.administration" v-if="$store.state.auth.availablePermissions['settings'] || $store.state.auth.availablePermissions['moderation']">
            <div class="item ui inline admin-dropdown dropdown">
              <i class="wrench icon"></i>
              <div
                v-if="$store.state.ui.notifications.pendingReviewEdits + $store.state.ui.notifications.pendingReviewReports > 0"
                :class="['ui', 'teal', 'mini', 'bottom floating', 'circular', 'label']">{{ $store.state.ui.notifications.pendingReviewEdits + $store.state.ui.notifications.pendingReviewReports }}</div>
              <div class="menu">
                <div class="header">
                  <translate translate-context="Sidebar/Admin/Title/Noun">Administration</translate>
                </div>
                <div class="divider"></div>
                <router-link
                  v-if="$store.state.auth.availablePermissions['library']"
                  class="item"
                  :to="{name: 'manage.library.edits', query: {q: 'is_approved:null'}}">
                  <div
                    v-if="$store.state.ui.notifications.pendingReviewEdits > 0"
                    :title="labels.pendingReviewEdits"
                    :class="['ui', 'circular', 'mini', 'right floated', 'teal', 'label']">
                    {{ $store.state.ui.notifications.pendingReviewEdits }}</div>
                  <translate translate-context="*/*/*/Noun">Library</translate>
                </router-link>
                <router-link
                  v-if="$store.state.auth.availablePermissions['moderation']"
                  class="item"
                  :to="{name: 'manage.moderation.reports.list', query: {q: 'resolved:no'}}">
                  <div
                    v-if="$store.state.ui.notifications.pendingReviewReports > 0"
                    :title="labels.pendingReviewReports"
                    :class="['ui', 'circular', 'mini', 'right floated', 'teal', 'label']">{{ $store.state.ui.notifications.pendingReviewReports }}</div>
                  <translate translate-context="*/Moderation/*">Moderation</translate>
                </router-link>
                <router-link
                  v-if="$store.state.auth.availablePermissions['settings']"
                  class="item"
                  :to="{name: 'manage.users.users.list'}">
                  <translate translate-context="*/*/*/Noun">Users</translate>
                </router-link>
                <router-link
                  v-if="$store.state.auth.availablePermissions['settings']"
                  class="item"
                  :to="{path: '/manage/settings'}">
                  <translate translate-context="*/*/*/Noun">Settings</translate>
                </router-link>
              </div>
            </div>
          </div>
        </div>
        <router-link
          class="item"
          v-if="$store.state.auth.authenticated"
          :title="labels.addContent"
          :to="{name: 'content.index'}"><i class="upload icon"></i></router-link>

        <router-link class="item" v-if="$store.state.auth.authenticated" :title="labels.notifications" :to="{name: 'notifications'}">
          <i class="bell icon"></i><div
            v-if="$store.state.ui.notifications.inbox + additionalNotifications > 0"
            :class="['ui', 'teal', 'mini', 'bottom floating', 'circular', 'label']">{{ $store.state.ui.notifications.inbox + additionalNotifications }}</div>
        </router-link>
        <div class="item">
          <div class="ui user-dropdown dropdown" >
            <div class="text">
              <img class="ui avatar image" v-if="$store.state.auth.profile.avatar.square_crop" v-lazy="$store.getters['instance/absoluteUrl']($store.state.auth.profile.avatar.square_crop)" />
              <actor-avatar v-else :actor="{preferred_username: $store.state.auth.username, full_username: $store.state.auth.username}" />
            </div>
            <div class="menu">
              <router-link class="item" :to="{name: 'profile', params: {username: $store.state.auth.username}}"><translate translate-context="*/*/*/Noun">Profile</translate></router-link>
              <router-link class="item" :to="{path: '/settings'}"></i><translate translate-context="*/*/*/Noun">Settings</translate></router-link>
              <router-link class="item" :to="{name: 'logout'}"></i><translate translate-context="Sidebar/Login/List item.Link/Verb">Logout</translate></router-link>
            </div>
          </div>
        </div>
      </template>
      <div class="item">

        <span
          @click="isCollapsed = !isCollapsed"
          :class="['ui', 'basic', 'big', {'inverted': isCollapsed}, 'orange', 'icon', 'collapse', 'button']">
            <i class="sidebar icon"></i></span>
      </div>
    </nav>
  </header>
  <search-bar @search="isCollapsed = false">
  </search-bar>
  <div v-if="!$store.state.auth.authenticated" class="ui basic signup segment">
    <router-link class="ui fluid tiny primary button" :to="{name: 'login'}"><translate translate-context="*/Login/*/Verb">Login</translate></router-link>
    <div class="ui small hidden divider"></div>
    <router-link class="ui fluid tiny button" :to="{path: '/signup'}">
      <translate translate-context="*/Signup/Link/Verb">Create an account</translate>
    </router-link>
  </div>
  <nav class="secondary" role="navigation">
    <div class="ui small hidden divider"></div>
    <section :class="['ui', 'bottom', 'attached', {active: selectedTab === 'library'}, 'tab']" :aria-label="labels.mainMenu">
      <nav class="ui inverted vertical large fluid menu" role="navigation" :aria-label="labels.mainMenu">
        <div class="item">
          <header class="header" @click="exploreExpanded = !exploreExpanded">
            <translate translate-context="*/*/*/Verb">Explore</translate>
            <i class="angle down icon" v-if="exploreExpanded"></i>
            <i class="angle right icon" v-else></i>
          </header>
          <div class="menu" v-if="exploreExpanded">
            <router-link class="item" :exact="true" :to="{name: 'library.index'}"><i class="music icon"></i><translate translate-context="Sidebar/Navigation/List item.Link/Verb">Browse</translate></router-link>
            <router-link class="item" :to="{name: 'library.albums.browse'}"><i class="compact disc icon"></i><translate translate-context="*/*/*">Albums</translate></router-link>
            <router-link class="item" :to="{name: 'library.artists.browse'}"><i class="user icon"></i><translate translate-context="*/*/*">Artists</translate></router-link>
            <router-link class="item" :to="{name: 'library.playlists.browse'}"><i class="list icon"></i><translate translate-context="*/*/*">Playlists</translate></router-link>
            <router-link class="item" :to="{name: 'library.radios.browse'}"><i class="feed icon"></i><translate translate-context="*/*/*">Radios</translate></router-link>
          </div>
        </div>
        <div class="item" v-if="$store.state.auth.authenticated" >
          <header class="header" @click="myLibraryExpanded = !myLibraryExpanded">
            <translate translate-context="*/*/*/Noun">My Library</translate>
            <i class="angle down icon" v-if="myLibraryExpanded"></i>
            <i class="angle right icon" v-else></i>
          </header>
          <div class="menu" v-if="myLibraryExpanded">
            <router-link class="item" :exact="true" :to="{name: 'library.me'}"><i class="music icon"></i><translate translate-context="Sidebar/Navigation/List item.Link/Verb">Browse</translate></router-link>
            <router-link class="item" :to="{name: 'library.albums.me'}"><i class="compact disc icon"></i><translate translate-context="*/*/*">Albums</translate></router-link>
            <router-link class="item" :to="{name: 'library.artists.me'}"><i class="user icon"></i><translate translate-context="*/*/*">Artists</translate></router-link>
            <router-link class="item" :to="{name: 'library.playlists.me'}"><i class="list icon"></i><translate translate-context="*/*/*">Playlists</translate></router-link>
            <router-link class="item" :to="{name: 'library.radios.me'}"><i class="feed icon"></i><translate translate-context="*/*/*">Radios</translate></router-link>
            <router-link class="item" :to="{name: 'favorites'}"><i class="heart icon"></i><translate translate-context="Sidebar/Favorites/List item.Link/Noun">Favorites</translate></router-link>
          </div>
        </div>
      </nav>
    </section>
    <div v-if="queue.previousQueue " class="ui black icon message">
      <i class="history icon"></i>
      <div class="content">
        <div class="header">
          <translate translate-context="Sidebar/Queue/Message">Do you want to restore your previous queue?</translate>
        </div>
        <p>
          <translate translate-context="*/*/*"
            translate-plural="%{ count } tracks"
            :translate-n="queue.previousQueue.tracks.length"
            :translate-params="{count: queue.previousQueue.tracks.length}">
            %{ count } track
          </translate>
        </p>
        <div class="ui two buttons">
          <div @click="queue.restore()" class="ui basic inverted green button"><translate translate-context="*/*/*">Yes</translate></div>
          <div @click="queue.removePrevious()" class="ui basic inverted red button"><translate translate-context="*/*/*">No</translate></div>
        </div>
      </div>
    </div>
  </nav>
  <player></player>
</aside>
</template>

<script>
import { mapState, mapActions, mapGetters } from "vuex"

import Player from "@/components/audio/Player"
import Logo from "@/components/Logo"
import SearchBar from "@/components/audio/SearchBar"
import backend from "@/audio/backend"

import $ from "jquery"

export default {
  name: "sidebar",
  components: {
    Player,
    SearchBar,
    Logo
  },
  data() {
    return {
      selectedTab: "library",
      backend: backend,
      isCollapsed: true,
      fetchInterval: null,
      exploreExpanded: false,
      myLibraryExpanded: false,
    }
  },
  destroy() {
    if (this.fetchInterval) {
      clearInterval(this.fetchInterval)
    }
  },
  computed: {
    ...mapGetters({
      additionalNotifications: "ui/additionalNotifications",
    }),
    ...mapState({
      queue: state => state.queue,
      url: state => state.route.path
    }),
    labels() {
      let mainMenu = this.$pgettext('Sidebar/*/Hidden text', "Main menu")
      let selectTrack = this.$pgettext('Sidebar/Player/Hidden text', "Play this track")
      let pendingFollows = this.$pgettext('Sidebar/Notifications/Hidden text', "Pending follow requests")
      let pendingReviewEdits = this.$pgettext('Sidebar/Moderation/Hidden text', "Pending review edits")
      return {
        pendingFollows,
        mainMenu,
        selectTrack,
        pendingReviewEdits,
        addContent: this.$pgettext("*/Library/*/Verb", 'Add content'),
        notifications: this.$pgettext("*/Notifications/*", 'Notifications'),
        administration: this.$pgettext("Sidebar/Admin/Title/Noun", 'Administration'),
      }
    },
    logoUrl() {
      if (this.$store.state.auth.authenticated) {
        return "library.index"
      } else {
        return "index"
      }
    }
  },
  methods: {
    ...mapActions({
      cleanTrack: "queue/cleanTrack"
    }),
    applyContentFilters () {
      let artistIds = this.$store.getters['moderation/artistFilters']().map((f) => {
        return f.target.id
      })

      if (artistIds.length === 0) {
        return
      }
      let self = this
      let tracks = this.tracks.slice().reverse()
      tracks.forEach(async (t, i) => {
        // we loop from the end because removing index from the start can lead to removing the wrong tracks
        let realIndex = tracks.length - i - 1
        let matchArtist = artistIds.indexOf(t.artist.id) > -1
        if (matchArtist) {
          return await self.cleanTrack(realIndex)
        }
        if (t.album && artistIds.indexOf(t.album.artist.id) > -1) {
          return await self.cleanTrack(realIndex)
        }
      })

    }
  },
  watch: {
    url: function() {
      this.isCollapsed = true
    },
    "$store.state.moderation.lastUpdate": function () {
      this.applyContentFilters()
    },
    "$store.state.auth.authenticated": {
      immediate: true,
      handler (v) {
        if (v) {
          this.myLibraryExpanded = true
          this.exploreExpanded = false
        } else {
          this.myLibraryExpanded = false
          this.exploreExpanded = true
        }
        this.$nextTick(() => {
          $(this.$el).find('.user-dropdown').dropdown({action: 'hide'})
          $(this.$el).find('.admin-dropdown').dropdown({action: 'hide'})
        })
      }
    },
    "$store.state.auth.availablePermissions": {
      immediate: true,
      handler (v) {
        this.$nextTick(() => {
          $(this.$el).find('.admin-dropdown').dropdown({action: 'hide'})
        })
      },
      deep: true,
    },
    "$route.name": {
      immediate: true,
      handler (n) {
        let mapping = {
          "library.index": 'exploreExpanded',
          "library.albums.browse": 'exploreExpanded',
          "library.albums.detail": 'exploreExpanded',
          "library.artists.browse": 'exploreExpanded',
          "library.artists.detail": 'exploreExpanded',
          "library.tracks.detail": 'exploreExpanded',
          "library.playlists.browse": 'exploreExpanded',
          "library.playlists.detail": 'exploreExpanded',
          "library.radios.browse": 'exploreExpanded',
          "library.radios.detail": 'exploreExpanded',
          'library.me': "myLibraryExpanded",
          'library.albums.me': "myLibraryExpanded",
          'library.artists.me': "myLibraryExpanded",
          'library.playlists.me': "myLibraryExpanded",
          'library.radios.me': "myLibraryExpanded",
          'favorites': "myLibraryExpanded",
        }
        if (mapping[n]) {
          // expand the menu block of the new route automatically, if applicable
          this[mapping[n]] = true
        }
      }
    },
    myLibraryExpanded: {
      handler (n) { this.exploreExpanded = !n},
      immediate: true,
    },
    exploreExpanded: {
      handler (n) { this.myLibraryExpanded = !n},
      immediate: true,
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "../style/vendor/media";

$sidebar-color: #3d3e3f;

.sidebar {
  background: $sidebar-color;
  @include media(">tablet") {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  > nav {
    flex-grow: 1;
    overflow-y: auto;
  }
  @include media(">desktop") {
    .collapse.button {
      display: none !important;
    }
  }
  @include media("<=desktop") {
    position: static !important;
    width: 100% !important;
    &.collapsed {
      .menu-area,
      .player-wrapper,
      .search,
      .signup.segment,
      nav.secondary {
        display: none;
      }
    }
  }

  > div {
    margin: 0;
    background-color: $sidebar-color;
  }
  .menu.vertical {
    background: $sidebar-color;
  }
}

.menu-area {
  .menu .item:not(.active):not(:hover) {
    opacity: 0.75;
  }

  .menu .item {
    border-radius: 0;
  }

  .menu .item.active {
    background-color: $sidebar-color;
    &:hover {
      background-color: rgba(255, 255, 255, 0.06);
    }
  }
}
.vertical.menu {
  .item .item {
    font-size: 1em;
    > i.icon {
      float: none;
      margin: 0 0.5em 0 0;
    }
    &:not(.active) {
      color: rgba(255, 255, 255, 0.75);
    }
  }
}
.tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  justify-content: space-between;
  @include media("<=desktop") {
    max-height: 500px;
  }
}
.ui.tab.active {
  display: flex;
}
.tab[data-tab="queue"] {
  flex-direction: column;
  tr {
    cursor: pointer;
  }
  td:nth-child(2) {
    width: 55px;
  }
}
.item .header .angle.icon {
  float: right;
  margin: 0;
}
.tab[data-tab="library"] {
  flex-direction: column;
  flex: 1 1 auto;
  > .menu {
    flex: 1;
    flex-grow: 1;
  }
  > .player-wrapper {
    width: 100%;
  }
}
.sidebar .segment {
  margin: 0;
  border-radius: 0;
}

.ui.menu .item.inline.admin-dropdown.dropdown > .menu {
  left: 0;
  right: auto;
}
.ui.inverted.segment.header-wrapper {
  padding: 0;
  display: flex;
  justify-content: space-between;
  height: 4em;
}
.fluid.category.search {
  height: 4em;
}
nav.top.title-menu {
  flex-grow: 1;
  .item {
    font-size: 1.5em;
  }
}

.logo {
  cursor: pointer;
  display: inline-block;
  margin: 0px;
}

.ui.search {
  display: flex;

  .collapse.button,
  .collapse.button:hover,
  .collapse.button:active {
    box-shadow: none !important;
    margin: 0px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

.ui.message.black {
  background: $sidebar-color;
}

.ui.mini.image {
  width: 100%;
}
nav.top {
  align-items: self-end;
  padding: 0.5em 0;
  > .item, > .right.menu > .item {
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 1.2em;
    &:hover, > .dropdown > .icon {
      color: rgba(255, 255, 255, 0.9) !important;
    }
    > .label, > .dropdown > .label {
      font-size: 0.5em;
      right: 1.7em;
      bottom: -0.5em;
      z-index: 0 !important;
    }
  }
}
.ui.user-dropdown > .text > .label {
  margin-right: 0;
}
</style>

<style lang="scss">
aside.ui.sidebar {
  overflow-y: visible !important;
  .ui.search .input {
    flex: 1;
    .prompt {
      border-radius: 0;
    }
  }
  .ui.search .results {
    vertical-align: middle;
  }
  .ui.search .name {
    vertical-align: middle;
  }
}
.ui.tiny.avatar.image {
  position: relative;
  top: -0.5em;
  width: 3em;
}

:not(.active) button.title {
  outline-color: white;
}
</style>
