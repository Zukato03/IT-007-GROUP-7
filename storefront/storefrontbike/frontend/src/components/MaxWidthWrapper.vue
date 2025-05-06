<template>
    <div :class="cn('h-full mx-auto w-full max-w-screen-xl px-2.5 md:px-20', classname)">
      <slot />
    </div>
  </template>
  
  <script setup>
  import { cn } from "@/lib/utils";
  import { computed } from "vue";
  import { defineProps } from "vue";
  
  const props = defineProps({
    classname: {
      type: String,
      default: '',
    }
  });
  </script>
  