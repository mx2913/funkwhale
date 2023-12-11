<script setup lang="ts">
import { onMounted, nextTick } from 'vue'
import Sidebar from '~/ui/components/Sidebar.vue'

// Fake content
onMounted(async () => {
  await nextTick()
  document.getElementById('fake-app')?.remove()
})
</script>

<template>
  <div class="grid">
    <Sidebar />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped lang="scss">
.grid {
  display: grid !important;
  grid-template-columns: 300px 5fr;
  min-height: 100vh;
}
</style>
