<template>
  <section>
    <artist-entries
      :key="object.uploads_count"
      :display-actions="false"
      :search="true"
      :filters="{playable: true, library: object.uuid, ordering: '-creation_date'}">
      <empty-state slot="empty-state">
        <p>
          <translate key="1" v-if="isOwner" translate-context="*/*/*">This library is empty, you should upload something in it!</translate>
          <translate key="2" v-else translate-context="*/*/*">You may need to follow this library to see its content.</translate>
        </p>
      </empty-state>
    </artist-entries>
  </section>
</template>

<script>
import ArtistEntries from '@/components/audio/ArtistEntries'

export default {
  props: ['object', 'isOwner'],
  components: {
    ArtistEntries,
  },
}
</script>
