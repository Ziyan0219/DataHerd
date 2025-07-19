import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/sonner'
import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import DataCleaning from '@/pages/DataCleaning'
import RuleManagement from '@/pages/RuleManagement'
import Reports from '@/pages/Reports'
import Settings from '@/pages/Settings'
import './App.css'

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="dataherd-ui-theme">
      <Router>
        <div className="min-h-screen bg-background">
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/cleaning" element={<DataCleaning />} />
              <Route path="/rules" element={<RuleManagement />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
          <Toaster />
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App

