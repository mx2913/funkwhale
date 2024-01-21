<script setup lang="ts">
import UploadGroupList from '~/ui/components/UploadGroupList.vue'
import { useUploadsStore } from '~/ui/stores/upload'
const uploads = useUploadsStore()
</script>

<template>
  <UploadGroupList :groups="uploads.uploadGroups" :is-uploading="true" />
</template>
