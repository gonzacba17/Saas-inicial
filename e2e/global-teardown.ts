import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up E2E test environment...');
  
  // Clean up test data if needed
  try {
    // Could add cleanup logic here if needed
    console.log('✅ Cleanup completed');
  } catch (error) {
    console.warn('⚠️ Cleanup failed:', error);
  }
}

export default globalTeardown;