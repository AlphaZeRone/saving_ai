import { useState } from 'react'
import { authAPI } from '@/api/client'
import { cn } from '@/lib/utils'
import './App.css'

function App() {
  const [connectionStatus, setConnectionStatus] = useState<string>('ready to test')

  const testConnection = async () => {
    setConnectionStatus('testing...')
    console.log('🧪 Testing API connection...')

    try {
      const response = await authAPI.getCurrentUser()
      console.log('✅ API Response:', response.data)
      setConnectionStatus('connected')
    } catch (error: any) {
      if (error.response?.status === 401) {
        console.log('✅ Expected 401 - Not logged in yet')
        console.log('Backend connection working! 🎉')
        setConnectionStatus('connected (401 expected)')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('❌ Network Error - Backend may be down')
        setConnectionStatus('connection failed')
      } else {
        console.error('❌ Unexpected error:', error.response?.status, error.message)
        setConnectionStatus('error')
      }
    }
  }

  const styles = {
    container: "min-h-screen bg-gray-100 flex items-center justify-center",
    card: "bg-white p-8 rounded-lg shadow-md",
    title: "text-3xl font-bold text-blue-600",
    subtitle: "text-gray-600 mt-2",
    instruction: "text-sm text-gray-500 mt-4",
    infoBox: "mt-4 p-4 bg-blue-50 rounded",
    infoText: "text-sm"
  }

  return (
    <div className = {cn(styles.container)}>
      <div className = {cn(styles.card)}>
        <h1 className = {cn(styles.title)}>Saving AI</h1>
        <p className = {cn(styles.subtitle)}>API Connection Testing</p>
        <p className = {cn(styles.instruction)}>
          Status: <strong>{connectionStatus}</strong>
        </p>
        <button 
          onClick={testConnection}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Test API Connection
        </button>
        <div className = {cn(styles.infoBox)}>
          <p className = {cn(styles.infoText)}>
            <strong>Expected:</strong> 401 Unauthorized (normal when not logged in)
          </p>
        </div>
      </div>
    </div>
  )
}

export default App