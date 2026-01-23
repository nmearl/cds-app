<template>
  <!-- Just a copy from Solara FileDrop -->
  <div class="solara-file-input">
    <label class="solara-file-input__label" @click="$refs.fileinput.click()" @keyup.enter="$refs.fileinput.click()" tabindex="0">
        Or click to select files
    </label>
      <input
        ref="fileinput"
        class="solara-file-input__native"
        type="file"
        :multiple="multiple"
        :accept="accept"
        @change="onChange"
      />

  <span class="solara-file-input__filename">
    <span v-for="file in file_info" :key="file.name">
      file name. csv
    </span >
  </span>
    
  </div>
</template>

<script>
module.exports = {
  mounted() {
    this.chunk_size = 2 * 1024 * 1024;
  },
  
  methods: {
    onChange(event) {
      event.preventDefault();
      const input = event.target;
      const nativeFiles = Array.from(input.files || []);
      console.log("Selected files:", nativeFiles);
      this.native_file_info = nativeFiles;
      this.file_info = nativeFiles.map(({ name, size }) => ({
        name,
        isFile: true,
        size,
      }));

      // important: allow re-selecting same file to trigger change
      // input.value = "";
    },

    jupyter_clear() {
      this.native_file_info = [];
      this.file_info = [];

      // clear native input too (optional)
      // if (this.$refs.fileinput) this.$refs.fileinput.value = "";
    },

    jupyter_read(chunk) {
      console.log("jupyter_read", chunk);
      const { id, file_index, offset, length } = chunk;
      let to_do = length;
      let sub_offset = offset;

      (async () => {
        while (to_do > 0) {
          const sub_length = Math.min(to_do, this.chunk_size);

          const file = this.native_file_info[file_index];
          const blob = file.slice(sub_offset, sub_offset + sub_length);
          const buff = await blob.arrayBuffer();

          const msg = { id, file_index, offset: sub_offset, length: sub_length };
          this.upload(msg, [buff]); // keeps your current upload contract

          to_do -= sub_length;
          sub_offset += sub_length;
        }
      })();
    },
  },
};
</script>

<style id="solara-file-input">
.solara-file-input {
  margin: 8px 0;
}

.solara-file-input__native {
  display: none;
}
.solara-file-input__label {
  display: inline-block;
  padding: 2px 4px;
  background-color: var(--solara-primary-color, #969696);
  color: black;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  font-size: 14px;
  text-align: center;
}

.solara-file-input__label:hover {
  background-color: var(--primary);
  color: white;
}

/* focus state */
.solara-file-input__label:focus {
  outline: 2px solid var(--solara-primary-color, #969696);
  outline-offset: 2px;
}


</style>
