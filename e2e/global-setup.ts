import { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up E2E test environment...');
  
  // Wait for backend to be ready
  const maxRetries = 30;
  let retries = 0;
  
  while (retries < maxRetries) {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        console.log('✅ Backend is ready');
        break;
      }
    } catch (error) {
      retries++;
      if (retries >= maxRetries) {
        throw new Error('❌ Backend failed to start within timeout');
      }
      console.log(`⏳ Waiting for backend... (${retries}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  // Wait for frontend to be ready
  retries = 0;
  while (retries < maxRetries) {
    try {
      const response = await fetch('http://localhost:3000');
      if (response.ok) {
        console.log('✅ Frontend is ready');
        break;
      }
    } catch (error) {
      retries++;
      if (retries >= maxRetries) {
        throw new Error('❌ Frontend failed to start within timeout');
      }
      console.log(`⏳ Waiting for frontend... (${retries}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  // Create test users and data
  try {
    console.log('📝 Creating test data...');
    
    // Register test user
    await fetch('http://localhost:8000/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'e2etest',
        email: 'e2etest@example.com',
        password: 'E2ETest123!',
        full_name: 'E2E Test User'
      })
    });
    
    // Register admin user
    await fetch('http://localhost:8000/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'e2eadmin',
        email: 'e2eadmin@example.com',
        password: 'E2EAdmin123!',
        full_name: 'E2E Admin User',
        role: 'admin'
      })
    });
    
    console.log('✅ Test data created successfully');
  } catch (error) {
    console.warn('⚠️ Failed to create test data:', error);
  }
  
  console.log('🎯 E2E test environment ready!');
}

export default globalSetup;