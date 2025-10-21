<template>
  <div v-if="message" :class="['global-message', messageType]" @click="closeMessage">
    {{ message.text }}
    <button class="close-btn" @click.stop="closeMessage">&times;</button>
  </div>
</template>

<script>
export default {
  name: 'GlobalMessage',
  data() {
    return {
      message: null,
      messageType: '',
      timeoutId: null
    };
  },
  beforeUnmount() {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
  },
  methods: {
    showMessage(messageData) {
      this.message = messageData;
      this.messageType = messageData.type;

      // Auto-hide message after 4 seconds
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }
      this.timeoutId = setTimeout(() => {
        this.closeMessage();
      }, 4000);
    },

    closeMessage() {
      this.message = null;
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
        this.timeoutId = null;
      }
    }
  }
};
</script>

<style scoped>
.global-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  max-width: 350px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.global-message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.global-message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.global-message.warning {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  margin-left: 1rem;
  cursor: pointer;
  opacity: 0.7;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  opacity: 1;
}
</style>