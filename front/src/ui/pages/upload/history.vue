<script setup lang="ts">
import UploadGroupList from '~/ui/components/UploadGroupList.vue'
import { useUploadsStore } from '~/ui/stores/upload'

// TODO: Fetch upload history from server
const uploads = useUploadsStore()
const history = uploads.uploadGroups
</script>

<template>
  <UploadGroupList :groups="history" />
</template>
