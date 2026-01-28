<!-- progress row shows column_data name id and an externally defined progress bar -->
<template>
  <tr 
    :class="`'progress-table-row' ${selected ? 'progress-table-row-selected' : ''}`"
    @click="() => selected = !selected"
    >
    
    <!-- add radio button showing sleected state -->
    <td class="progress-table-td progress-table-select">
      <input type="radio"  :checked="selected" />
    </td>
    
    <td v-for="key in Object.keys(column_data)" :key="key" :class="`progress-table-td progress-table-${key}`">
      {{ column_data[key] }}
    </td>
    
    <td 
      class="progress-table-td progress-table-progress"
      v-for="step in stepKeys" 
      :key="step" 
      >
        <div
          :class="['step-wrapper', getStepClass(step)+'-lighter']"
          :style="{gap: `${gap}`, ...cssProps}"
          >
          <div 
            :class="[getStepClass(step), 'meter']"
            :style="{ width: getStepProgress(step) }"
            >  </div>
          <div class="step-label" >{{ getStepProgress(step) }}</div>
  </div>

    </td>
    
  </tr>
</template>

<script>

export default {
  name: "ProgressRow",

  props: {
    column_data: {
      type: Object,
      required: true
    },

    style: {
      type: Object,
      default: () => ({height: "4px"})
    },
    selected: {
      type: Boolean,
      required: true
    },

    // progress bar props
    stepProgress: {
      type: Object,
      required: true,
    },
    stepOrder: {
      type: Array,
      default: () => [],
    },
    height: {
      type: [Number, String],
      default: "20px"
    },
    gap: {
      type: [Number, String],
      default: "0px"
    }
  },

  mounted() {
    // console.log("ProgressRow mounted");
    // console.log({ stepOrder: this.stepOrder, stepProgress: this.stepProgress })

  },

  methods: {
    normalizeProgress(value) {
      const num = Number(value);
      if (!Number.isFinite(num)) {
        console.warn(`Invalid progress value: ${value}`);
        return 0;
      }
      const pct = num <= 1 ? num * 100 : num;
      return Math.min(Math.max(pct, 0), 100);
    },
    getStepClass(step) {
      const pct = this.normalizeProgress(this.stepProgress[step]);
      if (pct >= 100) {
        return 'completed';
      } else if (pct > 0) {
        return 'in-progress';
      } else {
        return 'not-started';
      }
    },

    getStepProgress(step) {
      const pct = this.normalizeProgress(this.stepProgress[step]);
      return Math.round(pct) + '%';
    }
  },

  computed: {
    stepKeys() {
      if (this.stepOrder.length > 0) {
        return this.stepOrder;
      }
      return Object.keys(this.stepProgress)
        .map((value) => Number(value))
        .sort((a, b) => a - b);
    },
    cssProps() {
      return { 
        '--number-steps': this.stepKeys.length,
        '--meter-height': this.height
        }

    }
  }
};
</script>

<style>

.progress-table-row {
  cursor: auto;
}

/* left align cells */
/* add borders */
.progress-table-td {
  vertical-align: middle;
  padding-left: 5px;
  padding-right: 5px;
}

.progress-table-row-selected {
  background-color: var(--md-amber-100) !important;
  color: black;
}

.progress-table-progress {
  padding-left: 0;
  padding-right: 0;
  height: 1rem;
}

.step-wrapper {
  position: relative;
  padding-inline: 0;
  padding-block: 0;
  width: 95%;
  min-width: 15ch;
  height: inherit;
  border-radius: 999999px;  /* max out for rounded corners */
  overflow: hidden;
}

.meter {
  margin-left: 0;
  margin-right: auto;
  margin-block: auto;
  min-width: 5px;
  height: 100%;
}

.step-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%)
}

.completed {
  background-color: var(--md-cyan-700);
  
}

.completed-lighter {
  background-color: var(--md-cyan-700);
}

.in-progress {
  background-color: var(--md-cyan-700);
}

.in-progress-lighter {
  background-color: var(--md-deep-orange-300);
}

.not-started {
  background-color: var(--md-deep-orange-300);
}

.not-started-lighter {
  background-color: var(--md-deep-orange-300);
}

</style>
