<template>
  <div class="app-container min-h-screen bg-sci-midnight bg-hex-grid bg-grid bg-circuit-pattern scrollbar-sci-fi relative overflow-hidden app-background">
    <!-- Binary Code Rain Effect -->
    <div class="binary-rain"></div>

    <!-- Scanline Effect Overlay -->
    <div class="scanline-overlay fixed inset-0 pointer-events-none z-0"></div>

    <!-- Radial Glow Background -->
    <div class="fixed inset-0 bg-radial-glow pointer-events-none z-0"></div>

    <!-- Animated Background Particles -->
    <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <div class="absolute top-20 left-20 w-2 h-2 bg-sci-cyan/40 rounded-full animate-float"></div>
      <div class="absolute top-40 right-32 w-1.5 h-1.5 bg-sci-cyan/30 rounded-full animate-float" style="animation-delay: 1s;"></div>
      <div class="absolute bottom-32 left-1/4 w-2 h-2 bg-sci-gold/30 rounded-full animate-float" style="animation-delay: 2s;"></div>
      <div class="absolute top-1/3 right-1/4 w-1 h-1 bg-sci-cyan/50 rounded-full animate-float" style="animation-delay: 0.5s;"></div>
      <div class="absolute top-1/2 left-1/3 w-1.5 h-1.5 bg-sci-gold/20 rounded-full animate-float" style="animation-delay: 1.5s;"></div>
      <div class="absolute bottom-1/4 right-1/3 w-1 h-1 bg-sci-cyan/30 rounded-full animate-float" style="animation-delay: 2.5s;"></div>
    </div>

    <el-container class="relative z-10">
      <!-- Quantum Command Center Header -->
      <el-header class="app-header h-20 w-full px-6">
        <div class="header-content flex items-center justify-between h-full">
          <!-- Logo Section with AURUM ANALYTICS Branding -->
          <div class="flex items-center space-x-5">
            <div class="logo-container flex items-center space-x-4 fui-reticle">
              <div class="logo-icon w-14 h-14 flex items-center justify-center
                            bg-sci-cyan/15 border border-sci-cyan/50 rounded-lg
                            shadow-glow-cyan data-conduit relative overflow-hidden">
                <span class="text-sci-cyan text-2xl relative z-10">⚡</span>
                <div class="absolute inset-0 bg-gradient-to-br from-sci-cyan/20 to-transparent"></div>
              </div>
              <div>
                <h1 class="app-title font-tech font-bold text-xl tracking-widest text-white">
                  AURUM <span class="text-sci-cyan text-glow-cyan-enhanced">ANALYTICS</span>
                </h1>
                <div class="text-xs text-sci-cyan/70 font-data tracking-widest flex items-center space-x-2">
                  <span>// FUND COMMAND v4.5.1</span>
                  <span class="w-1 h-1 bg-sci-gold rounded-full"></span>
                  <span class="text-sci-gold/80">QUANTUM INTERFACE</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Navigation Menu -->
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            :router="true"
            class="nav-menu flex-1 max-w-2xl mx-12"
          >
            <el-menu-item index="/" class="nav-item">
              <span class="nav-item-text font-modern">首页</span>
            </el-menu-item>
            <el-menu-item index="/funds" class="nav-item">
              <span class="nav-item-text font-modern">基金管理</span>
            </el-menu-item>
            <el-menu-item index="/holdings" class="nav-item">
              <span class="nav-item-text font-modern">持仓管理</span>
            </el-menu-item>
            <el-menu-item index="/analysis" class="nav-item">
              <span class="nav-item-text font-modern">收益分析</span>
            </el-menu-item>
          </el-menu>

          <!-- System Status Indicators -->
          <div class="flex items-center space-x-5">
            <div class="flex items-center space-x-2 px-4 py-2
                          bg-navy-900/60 border border-sci-cyan/30 rounded-lg
                          backdrop-blur-sm shadow-glass">
              <span class="status-dot status-pulse w-2 h-2 bg-sci-success rounded-full"></span>
              <span class="text-xs text-gray-300 font-data tracking-wider">SYSTEM ONLINE</span>
            </div>
            <div class="text-right">
              <div class="text-sm text-sci-cyan font-data tracking-widest" id="current-time">
                {{ currentTime }}
              </div>
              <div class="text-xs text-sci-gold/80 font-tech tracking-wide">
                v4.4.1
              </div>
            </div>
          </div>
        </div>
      </el-header>

      <!-- Main Content Area -->
      <el-main class="app-main px-6 py-8">
        <div class="max-w-[1800px] mx-auto">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { syncAllNav } from '@/api/fund'
import dayjs from 'dayjs'

const route = useRoute()
const activeMenu = computed(() => route.path)
const currentTime = ref('')

const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm:ss')
}

// 自动同步功能
const autoSyncOnLoad = async () => {
  const lastSync = localStorage.getItem('lastSyncTime')
  const now = dayjs()

  // 如果从未同步过，或距离上次同步超过 24 小时
  if (!lastSync || now.diff(dayjs(lastSync), 'hour') >= 24) {
    console.log('自动同步基金数据...')
    try {
      await syncAllNav()
      localStorage.setItem('lastSyncTime', now.format('YYYY-MM-DD HH:mm:ss'))
      console.log('自动同步完成')
    } catch (error) {
      console.error('自动同步失败:', error)
    }
  } else {
    console.log(`距离上次同步不足24小时，跳过自动同步`)
  }
}

let timeInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

  // 页面加载时自动同步
  autoSyncOnLoad()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style>
/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Rajdhani', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* App Container */
.app-container {
  position: relative;
  overflow-x: hidden;
}

/* Background Image */
.app-background {
  background-image: url('/figures/background.png');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  background-repeat: no-repeat;
}

/* Header Styles - Enhanced Quantum Look */
.app-header {
  background: linear-gradient(
    135deg,
    rgba(5, 8, 16, 0.98) 0%,
    rgba(10, 15, 26, 0.95) 100%
  );
  backdrop-filter: blur(25px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
  box-shadow:
    0 4px 40px rgba(0, 0, 0, 0.6),
    0 0 30px rgba(0, 212, 255, 0.15),
    inset 0 1px 0 rgba(0, 212, 255, 0.1);
  padding: 0 !important;
  position: sticky;
  top: 0;
  z-index: 100;
}

/* Header decorative line with animated gradient */
.app-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 212, 255, 0.2) 20%,
    rgba(0, 212, 255, 0.8) 50%,
    rgba(255, 215, 0, 0.6) 80%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: headerLineGlow 4s ease-in-out infinite;
}

@keyframes headerLineGlow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.header-content {
  height: 100%;
}

/* Logo Styles */
.logo-container {
  position: relative;
}

.logo-icon {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.logo-icon:hover {
  transform: scale(1.05);
  box-shadow: 0 0 40px rgba(0, 212, 255, 0.7);
}

.app-title {
  letter-spacing: 0.15em;
  text-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}

/* Navigation Menu Override - Enhanced */
.nav-menu {
  background: transparent !important;
  border: none !important;
  display: flex;
  justify-content: center;
}

.nav-menu.el-menu--horizontal {
  border-bottom: none !important;
}

.nav-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.7) !important;
  border-bottom: 2px solid transparent !important;
  padding: 0 24px !important;
  height: 54px !important;
  line-height: 54px !important;
  position: relative;
  transition: all 0.3s ease;
  font-size: 15px;
}

.nav-menu .el-menu-item::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.nav-menu .el-menu-item:hover {
  background: rgba(0, 212, 255, 0.15) !important;
  color: #00d4ff !important;
}

.nav-menu .el-menu-item:hover::before {
  width: 100%;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.8);
}

.nav-menu .el-menu-item.is-active {
  background: rgba(0, 212, 255, 0.2) !important;
  color: #00d4ff !important;
  border-bottom-color: transparent !important;
}

.nav-menu .el-menu-item.is-active::before {
  width: 100%;
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.9);
}

.nav-item-text {
  position: relative;
  z-index: 1;
  letter-spacing: 0.05em;
}

/* Status Dot Animation - Enhanced */
@keyframes statusPulse {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 8px rgba(34, 197, 94, 1);
  }
  50% {
    opacity: 0.7;
    box-shadow: 0 0 4px rgba(34, 197, 94, 0.5);
  }
}

/* Main Content Area */
.app-main {
  min-height: calc(100vh - 80px);
}

/* Element Plus Menu Popper Override - Enhanced */
.el-menu--popup {
  background: rgba(5, 8, 16, 0.98) !important;
  backdrop-filter: blur(25px);
  border: 1px solid rgba(0, 212, 255, 0.4) !important;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.6),
    0 0 30px rgba(0, 212, 255, 0.2) !important;
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Custom selection color - Enhanced */
::selection {
  background: rgba(0, 212, 255, 0.4);
  color: #ffffff;
}
</style>
