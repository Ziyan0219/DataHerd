import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/sonner'
import Layout from '@/components/Layout'
import ErrorBoundary from '@/components/ErrorBoundary'
import Welcome from '@/pages/Welcome'
import Dashboard from '@/pages/Dashboard'
import DataCleaning from '@/pages/DataCleaning'
import RuleManagement from '@/pages/RuleManagementSimple'
import Reports from '@/pages/Reports'
import Settings from '@/pages/Settings'
import './App.css'

function App() {
  return (
    <ErrorBoundary showDetails={true}>
      <ThemeProvider defaultTheme="light" storageKey="dataherd-ui-theme">
        <Router>
          <div className="min-h-screen bg-background">
            <Routes>
              <Route path="/" element={<Welcome />} />
              <Route path="/dashboard" element={
                <Layout>
                  <Dashboard />
                </Layout>
              } />
              <Route path="/cleaning" element={
                <Layout>
                  <DataCleaning />
                </Layout>
              } />
              <Route path="/rules" element={
                <Layout>
                  <ErrorBoundary>
                    <RuleManagement />
                  </ErrorBoundary>
                </Layout>
              } />
              <Route path="/reports" element={
                <Layout>
                  <ErrorBoundary>
                    <Reports />
                  </ErrorBoundary>
                </Layout>
              } />
              <Route path="/settings" element={
                <Layout>
                  <Settings />
                </Layout>
              } />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App

