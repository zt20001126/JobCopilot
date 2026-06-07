<template>
  <main class="popup">
    <span class="badge">MVP</span>
    <h1>JobCopilot</h1>
    <p>AI 求职副驾驶</p>
    <p class="description">
      在 Boss直聘岗位详情页中读取 JD，并生成针对性的求职招呼语。
    </p>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  background: #f7f8fc;
  color: #182033;
  font-family: Inter, "Microsoft YaHei", sans-serif;
}

.popup {
  box-sizing: border-box;
  width: 320px;
  padding: 22px;
}

.badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 999px;
  background: #e8edff;
  color: #3451b2;
  font-size: 12px;
}

h1 {
  margin: 12px 0 4px;
  font-size: 24px;
}

p {
  margin: 0;
  color: #566079;
}

.description {
  margin-top: 16px;
  line-height: 1.6;
}
</style>
