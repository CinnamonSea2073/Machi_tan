<template>
  <svg 
    :width="width" 
    :height="height" 
    :viewBox="pressed ? '0 0 370 708' : '0 0 354 708'" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    class="transceiver-svg"
  >
    <!-- 通常状態のSVG -->
    <g v-if="!pressed">
      <rect x="248" y="131" width="66" height="100" fill="#626262"/>
      <rect x="151" y="163" width="66" height="100" rx="8" fill="#626262"/>
      <rect x="151" y="198" width="66" height="12" fill="#EF612E"/>
      <rect x="256" width="50" height="153" rx="24" fill="#626262"/>
      <g filter="url(#filter0_d_229_1915)">
        <rect x="314" y="442" width="26" height="76" rx="13" fill="#626262"/>
      </g>
      <g filter="url(#filter1_d_229_1915)">
        <rect x="314" y="529" width="26" height="76" rx="13" fill="#626262"/>
      </g>
      <rect x="8" y="315" width="89" height="181" fill="#EF612E"/>
      <g filter="url(#filter2_d_229_1915)">
        <path d="M0 245C0 231.745 10.7452 221 24 221H330C343.255 221 354 231.745 354 245V381.432C354 385.415 353.009 389.335 351.116 392.839L333.384 425.661C331.491 429.165 330.5 433.085 330.5 437.068V676C330.5 689.255 319.755 700 306.5 700H24C10.7452 700 0 689.255 0 676V494.284C0 488.012 2.45511 481.989 6.83984 477.505L15.1602 468.995C19.5449 464.511 22 458.488 22 452.216V354.419C22 348.969 20.1453 343.682 16.7409 339.426L5.25915 325.074C1.85474 320.818 0 315.531 0 310.081V245Z" fill="#3F3F3F"/>
      </g>
      <g filter="url(#filter3_d_229_1915)">
        <rect x="242" y="263" width="79" height="115" rx="8" fill="#9D57FF"/>
      </g>
      <rect x="45" y="420" width="255" height="75" rx="8" fill="#687163"/>
      <rect x="45" y="263" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="45" y="284" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="45" y="305" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="45" y="326" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="45" y="347" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="45" y="368" width="172" height="10" rx="5" fill="#626262"/>
      <path d="M267 317C267 320.713 268.475 324.274 271.101 326.899C273.726 329.525 277.287 331 281 331M281 331C284.713 331 288.274 329.525 290.899 326.899C293.525 324.274 295 320.713 295 317M281 331V339M273 339H289M275 307C275 305.409 275.632 303.883 276.757 302.757C277.883 301.632 279.409 301 281 301C282.591 301 284.117 301.632 285.243 302.757C286.368 303.883 287 305.409 287 307V317C287 318.591 286.368 320.117 285.243 321.243C284.117 322.368 282.591 323 281 323C279.409 323 277.883 322.368 276.757 321.243C275.632 320.117 275 318.591 275 317V307Z" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <!-- 押された状態のSVG -->
    <g v-if="pressed">
      <rect x="264" y="131" width="66" height="100" fill="#626262"/>
      <rect x="167" y="163" width="66" height="100" rx="8" fill="#626262"/>
      <g filter="url(#filter0_d_229_1916)">
        <rect x="167" y="198" width="66" height="12" fill="#FF8E65"/>
      </g>
      <rect x="272" width="50" height="153" rx="24" fill="#626262"/>
      <g filter="url(#filter1_d_229_1916)">
        <rect x="330" y="442" width="26" height="76" rx="13" fill="#626262"/>
      </g>
      <g filter="url(#filter2_d_229_1916)">
        <rect x="330" y="529" width="26" height="76" rx="13" fill="#626262"/>
      </g>
      <g filter="url(#filter3_d_229_1916)">
        <rect x="24" y="315" width="89" height="181" fill="#FF8E65"/>
      </g>
      <g filter="url(#filter4_d_229_1916)">
        <path d="M16 245C16 231.745 26.7452 221 40 221H346C359.255 221 370 231.745 370 245V381.432C370 385.415 369.009 389.335 367.116 392.839L349.384 425.661C347.491 429.165 346.5 433.085 346.5 437.068V676C346.5 689.255 335.755 700 322.5 700H40C26.7452 700 16 689.255 16 676V494.284C16 488.012 18.4551 481.989 22.8398 477.505L31.1602 468.995C35.5449 464.511 38 458.488 38 452.216V354.419C38 348.969 36.1453 343.682 32.7409 339.426L21.2592 325.074C17.8547 320.818 16 315.531 16 310.081V245Z" fill="#3F3F3F"/>
      </g>
      <g filter="url(#filter5_d_229_1916)">
        <rect x="258" y="271" width="79" height="115" rx="8" fill="#BD8EFF"/>
      </g>
      <rect x="61" y="420" width="255" height="75" rx="8" fill="#687163"/>
      <rect x="61" y="263" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="61" y="284" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="61" y="305" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="61" y="326" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="61" y="347" width="172" height="10" rx="5" fill="#626262"/>
      <rect x="61" y="368" width="172" height="10" rx="5" fill="#626262"/>
      <path d="M283 325C283 328.713 284.475 332.274 287.101 334.899C289.726 337.525 293.287 339 297 339M297 339C300.713 339 304.274 337.525 306.899 334.899C309.525 332.274 311 328.713 311 325M297 339V347M289 347H305M291 315C291 313.409 291.632 311.883 292.757 310.757C293.883 309.632 295.409 309 297 309C298.591 309 300.117 309.632 301.243 310.757C302.368 311.883 303 313.409 303 315V325C303 326.591 302.368 328.117 301.243 329.243C300.117 330.368 298.591 331 297 331C295.409 331 293.883 330.368 292.757 329.243C291.632 328.117 291 326.591 291 325V315Z" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <!-- 通常状態のフィルター定義 -->
    <defs v-if="!pressed">
      <filter id="filter0_d_229_1915" x="314" y="442" width="26" height="84" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="8"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1915"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1915" result="shape"/>
      </filter>
      <filter id="filter1_d_229_1915" x="314" y="529" width="26" height="84" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="8"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1915"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1915" result="shape"/>
      </filter>
      <filter id="filter2_d_229_1915" x="0" y="221" width="354" height="487" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="8"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1915"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1915" result="shape"/>
      </filter>
      <filter id="filter3_d_229_1915" x="242" y="263" width="79" height="123" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="8"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.509184 0 0 0 0 0.268491 0 0 0 0 0.846154 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1915"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1915" result="shape"/>
      </filter>
    </defs>

    <!-- 押された状態のフィルター定義 -->
    <defs v-if="pressed">
      <filter id="filter0_d_229_1916" x="143.2" y="174.2" width="113.6" height="59.6" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset/>
        <feGaussianBlur stdDeviation="11.9"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.937255 0 0 0 0 0.380392 0 0 0 0 0.180392 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1916"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1916" result="shape"/>
      </filter>
      <filter id="filter1_d_229_1916" x="330" y="442" width="26" height="84" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="8"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1916"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1916" result="shape"/>
      </filter>
      <filter id="filter2_d_229_1916" x="330" y="529" width="26" height="84" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="8"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1916"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1916" result="shape"/>
      </filter>
      <filter id="filter3_d_229_1916" x="0.200001" y="291.2" width="136.6" height="228.6" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset/>
        <feGaussianBlur stdDeviation="11.9"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.937255 0 0 0 0 0.380392 0 0 0 0 0.180392 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1916"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1916" result="shape"/>
      </filter>
      <filter id="filter4_d_229_1916" x="16" y="221" width="354" height="487" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="8"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1916"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1916" result="shape"/>
      </filter>
      <filter id="filter5_d_229_1916" x="234.2" y="247.2" width="126.6" height="162.6" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset/>
        <feGaussianBlur stdDeviation="11.9"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.615686 0 0 0 0 0.341176 0 0 0 0 1 0 0 0 1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_229_1916"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_229_1916" result="shape"/>
      </filter>
    </defs>
  </svg>
</template>

<script setup>
defineProps({
  pressed: {
    type: Boolean,
    default: false
  },
  width: {
    type: [String, Number],
    default: 120
  },
  height: {
    type: [String, Number],
    default: 240
  }
})
</script>

<style scoped>
.transceiver-svg {
  transition: all 0.2s ease;
}
</style>