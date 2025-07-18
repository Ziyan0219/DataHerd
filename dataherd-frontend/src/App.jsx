import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">DataHerd</h1>
        <p className="text-lg text-gray-600 mb-8">Intelligent Cattle Data Cleaning Platform</p>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Welcome to DataHerd</h2>
          <p className="text-gray-600 mb-6">
            This is a powerful AI-driven data cleaning platform designed specifically for cattle lot management.
          </p>
          
          <Button onClick={() => setCount(count + 1)} className="mb-4">
            Test Button (clicked {count} times)
          </Button>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900">Data Cleaning</h3>
              <p className="text-blue-700 text-sm">Apply intelligent rules to clean cattle data</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900">Preview Changes</h3>
              <p className="text-green-700 text-sm">Review changes before applying them</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-900">Generate Reports</h3>
              <p className="text-purple-700 text-sm">Create detailed operation reports</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

