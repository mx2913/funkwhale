<script setup lang="ts">
import { useAsyncState } from '@vueuse/core';
import axios from 'axios';
import UploadGroupList from '~/ui/components/UploadGroupList.vue'
import { useUploadsStore } from '~/ui/stores/upload'

// TODO: Fetch upload history from server
const uploads = useUploadsStore()
const history = uploads.uploadGroups

const { state: data } = useAsyncState(axios.post('/api/v2/upload-groups', { baseUrl: '/' }).then(t => t.data), [])
</script>

<template>
  {{ data }}
  <UploadGroupList :groups="history" />
</template>
