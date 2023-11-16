<script setup lang="ts">
import { ref, onMounted } from 'vue'

const searchQuery = ref('')

// Hide the fake app when the real one is loaded
onMounted(() => {
  document.getElementById('fake-app')?.remove()
})
</script>

<template>
  <aside>
    <div class="sticky-content">
      <nav class="quick-actions">
        <RouterLink to="/">
          <img src="../assets/logo/logo.svg" alt="Logo" class="logo" />
        </RouterLink>

        <FwButton icon="bi-wrench" color="secondary" />
        <FwButton icon="bi-upload" color="secondary" />
        <FwButton icon="bi-inbox" color="secondary" />

        <a
          @click.prevent
          href=""
          class="avatar"
        >
          <img
            v-if="$store.state.auth.authenticated && $store.state.auth.profile?.avatar?.urls.medium_square_crop"
            alt=""
            :src="$store.getters['instance/absoluteUrl']($store.state.auth.profile?.avatar.urls.medium_square_crop)"
          >
          <ActorAvatar
            v-else-if="$store.state.auth.authenticated"
            :actor="{preferred_username: $store.state.auth.username, full_username: $store.state.auth.username,}"
          />
          <i
            v-else
            class="cog icon"
          />
        </a>
      </nav>

      <div class="search">
        <FwInput
          v-model="searchQuery"
          icon="bi-search"
          :placeholder="$t('components.audio.SearchBar.placeholder.search')"
        />
      </div>

      <h3>Explore</h3>
      <nav class="button-list">
        <FwButton color="secondary" icon="bi-compass">All Funkwhale</FwButton>
        <FwButton color="secondary" icon="bi-music-note-beamed">Music</FwButton>
        <FwButton color="secondary" icon="bi-mic">Podcasts</FwButton>
      </nav>

      <h3>Library</h3>
      <div class="pill-list">
        <FwPill>Music</FwPill>
        <FwPill outline>Podcasts</FwPill>
        <FwPill outline>Sharing</FwPill>
      </div>
      <nav class="button-list">
        <FwButton color="secondary" icon="bi-collection">Collections</FwButton>
        <FwButton color="secondary" icon="bi-person">Artists</FwButton>
        <FwButton color="secondary" icon="bi-disc">Albums</FwButton>
        <FwButton color="secondary" icon="bi-music-note-list">Playlists</FwButton>
        <FwButton color="secondary" icon="bi-question-diamond">Radios</FwButton>
        <FwButton color="secondary" icon="bi-heart">Favorites</FwButton>
      </nav>
    </div>
  </aside>
</template>

<style scoped lang="scss">
aside {
  background: var(--fw-beige-300);
  height: 100%;

  > .sticky-content {
    position: sticky;
    height: 100%;
    max-height: 100vh;
    overflow: auto;
    top: 0;

    > .quick-actions {
      display: flex;
      align-items: center;
      padding: 12px;
      font-size: 1.3rem;


      > :first-child {
        margin-right: auto;

      }

      .avatar,
      .logo {
        height: 30px;
      }

      .avatar {
        aspect-ratio: 1;
        background: var(--fw-beige-100);
        border-radius: 100%;

        text-decoration: none !important;
        color: var(--fw-gray-700);

        > i {
          width: 100%;
          height: 100%;

          display: flex;
          justify-content: center;
          align-items: center;
          margin: 0 !important;
        }
      }
    }

    > .search {
      padding: 0 16px 23px;
    }

    > h3 {
      margin: 0;
      padding: 0 32px 8px;
      color: var(--fw-gray-700);
      font-size: 14px;
      line-height: 1.2;
    }

    > .pill-list {
      padding: 0 16px 8px;
      white-space: nowrap;
    }

    > nav.button-list {
      padding: 0 16px 32px;

      > button {
        margin: 2px 0;

        /* TODO: Fix in UI: When icon is applied, the text should be aligned left */
        justify-content: start;

        /* TODO: Fix in UI: Add `block` prop that spans 100% width */
        width: 100%;

        :deep(i) {
          font-size: 1.4em;

          /* TODO: Fix in UI: Add margin right to the icon, when content available */
          margin-right: 1ch;
        }
      }
    }

  }
}
</style>
