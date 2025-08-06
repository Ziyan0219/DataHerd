import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Sparkles, 
  Database, 
  BarChart3, 
  Shield, 
  Users, 
  Clock,
  ArrowRight,
  CheckCircle
} from 'lucide-react'

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Rules",
    description: "Natural language processing for intelligent data cleaning rules"
  },
  {
    icon: Database,
    title: "Smart Data Processing",
    description: "Preview changes before applying with confidence scoring"
  },
  {
    icon: BarChart3,
    title: "Comprehensive Reports",
    description: "Detailed analytics and audit trails for compliance"
  },
  {
    icon: Shield,
    title: "Data Security",
    description: "Complete rollback capability and audit logging"
  }
]

export default function Welcome() {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    navigate('/cleaning')
  }

  const handleViewDashboard = () => {
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-blue-600 shadow-lg">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900">DataHerd</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Welcome! Your intelligent cattle data cleaning platform is ready to help you process and clean data with AI-powered rules.
          </p>
          <p className="text-lg text-blue-600 font-medium">
            🎉 Wish you have a happy day! 🎉
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="border-0 shadow-md hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                      <Icon className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
                      <p className="text-gray-600 text-sm">{feature.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Quick Stats */}
        <Card className="border-0 shadow-md">
          <CardHeader>
            <CardTitle className="text-center">System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
              <div className="space-y-2">
                <div className="flex items-center justify-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  <span className="font-semibold text-gray-900">AI Engine</span>
                </div>
                <p className="text-sm text-green-600">Ready</p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  <span className="font-semibold text-gray-900">Database</span>
                </div>
                <p className="text-sm text-green-600">Connected</p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-center">
                  <Users className="h-5 w-5 text-blue-500 mr-2" />
                  <span className="font-semibold text-gray-900">Active Rules</span>
                </div>
                <p className="text-sm text-gray-600">23</p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-center">
                  <Clock className="h-5 w-5 text-purple-500 mr-2" />
                  <span className="font-semibold text-gray-900">Uptime</span>
                </div>
                <p className="text-sm text-gray-600">99.9%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <Button 
            size="lg" 
            onClick={handleGetStarted}
            className="px-8 py-3"
          >
            <Sparkles className="w-5 h-5 mr-2" />
            Start Data Cleaning
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
          <Button 
            variant="outline" 
            size="lg" 
            onClick={handleViewDashboard}
            className="px-8 py-3"
          >
            <BarChart3 className="w-5 h-5 mr-2" />
            View Dashboard
          </Button>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          DataHerd v1.0 - Intelligent Cattle Data Management Platform
        </div>
      </div>
    </div>
  )
}