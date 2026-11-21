<script setup lang="ts">
import { computed, ref } from 'vue'
import { reviewSource, type Review } from './api'
const source = ref('def binarize(pixel):\n    return 255 if pixel >= threshold else 0\n')
const loading = ref(false)
const error = ref('')
const result = ref<Review | null>(null)
const count = computed(() => result.value?.findings.length ?? 0)
async function review() {
  loading.value = true; error.value = ''; result.value = null
  try {
    result.value = await reviewSource(source.value)
  } catch (e) { error.value = e instanceof Error ? e.message : '无法连接评审服务' }
  finally { loading.value = false }
}
</script>

<template>
  <div class="shell">
    <aside class="rail"><div class="brand">知</div><div class="rail-icon active">⌘</div><div class="rail-icon">▤</div><div class="rail-icon">⚙</div><div class="avatar">助</div></aside>
    <main>
      <header><div><div class="eyebrow">TEACHING ASSISTANT / TASK 07</div><h1>代码智能评审</h1><p>静态建议与代码变化检查 · 学生代码不会在此运行</p></div><span class="badge">本地演示</span></header>
      <section class="stats"><article><span>评审模式</span><b>静态分析</b><small>不执行学生提交</small></article><article><span>检查维度</span><b>括号 · 未定义名称 · 裸 except</b><small>Python 静态检查</small></article><article><span>算法工具</span><b>接口待接入</b><small>仅允许预封装教学算法</small></article></section>
      <section class="workspace">
        <div class="panel editor"><div class="panel-head"><div><strong>提交代码</strong><small>本地演示文本 · Python</small></div><span class="file">⌁ submission.py</span></div><textarea v-model="source" spellcheck="false" aria-label="待评审代码"></textarea><div class="editor-foot"><span>静态检查不会运行或导入代码</span><button @click="review" :disabled="loading">{{ loading ? '分析中…' : '✦ 开始评审' }}</button></div></div>
        <div class="panel result"><div class="panel-head"><div><strong>评审结果</strong><small>仅供教学参考，由教师确认</small></div><span class="count">{{ count }} 条</span></div>
          <div v-if="error" class="notice error">{{ error }}</div><div v-else-if="!result" class="empty"><div class="spark">✦</div><b>等待开始评审</b><span>提交代码后，建议会显示在这里。</span></div>
          <div v-else class="findings">
            <div class="summary" role="status">{{ result.summary }} · 规则版本 {{ result.rule_version }}</div>
            <article v-for="finding in result.findings" :key="finding.id" class="finding">
              <div class="finding-top">
                <span :class="['severity', finding.severity]">
                  {{ finding.category === 'style' ? '代码风格' : '潜在正确性问题' }}
                </span>
                <span>{{ finding.file }} · 第 {{ finding.line_start }} 行</span>
              </div>
              <b>{{ finding.title }}</b>
              <p>{{ finding.description }}</p>
              <small>{{ finding.suggestion }}</small>
            </article>
            <div v-if="!count" class="notice">当前规则未发现建议。静态检查不能判断算法的运行结果。</div>
          </div>
        </div>
      </section>
      <footer>助教工作台 <span>·</span> 代码仅用于静态文本检查，不会发送给外部模型或执行</footer>
    </main>
  </div>
</template>

<style scoped src="./review.css"></style>
