<template>
    <svg
      v-bind="props"
      viewBox="0 0 687 155"
      stroke="currentColor"
      stroke-width="7"
      fill="none"
      fill-rule="evenodd"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <g>
        <path
          d="M20 98c27-13.3333333 54-20 81-20 40.5 0 40.5 20 81 20s40.626917-20 81-20 40.123083 20 80.5 20 40.5-20 81-20 40.5 20 81 20 40.626917-20 81-20c26.915389 0 53.748722 6.6666667 80.5 20"
          opacity=".3"
        ></path>
        <path d="M20 118c27-13.3333333 54-20 81-20 40.5 0 40.5 20 81 20s40.626917-20 81-20 40.123083 20 80.5 20 40.5-20 81-20 40.5 20 81 20 40.626917-20 81-20c26.915389 0 53.748722 6.6666667 80.5 20"></path>
      </g>
    </svg>
  </template>
  
  <script>
  export default {
    name: "Icons",
    props: {
      props: {
        type: Object,
        required: true,
      },
    },
  };
  </script>
  