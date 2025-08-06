import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  Database, 
  FileText, 
  TrendingUp, 
  Users, 
  AlertCircle,
  CheckCircle,
  Clock,
  Sparkles
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

const recentOperations = [
  {
    id: 1,
    batch: "ELANCO_2025_001",
    operation: "Weight Validation",
    status: "completed",
    timestamp: "2025-01-19 14:30",
    recordsProcessed: 2500,
    issuesFound: 45
  },
  {
    id: 2,
    batch: "ELANCO_2025_002", 
    operation: "Breed Standardization",
    status: "in_progress",
    timestamp: "2025-01-19 15:15",
    recordsProcessed: 1200,
    issuesFound: 32
  },
  {
    id: 3,
    batch: "ELANCO_2025_003",
    operation: "Date Validation",
    status: "completed",
    timestamp: "2025-01-19 13:45",
    recordsProcessed: 1800,
    issuesFound: 12
  }
]

const weeklyData = [
  { name: 'Mon', operations: 12, issues: 45 },
  { name: 'Tue', operations: 19, issues: 32 },
  { name: 'Wed', operations: 15, issues: 28 },
  { name: 'Thu', operations: 22, issues: 51 },
  { name: 'Fri', operations: 18, issues: 38 },
  { name: 'Sat', operations: 8, issues: 15 },
  { name: 'Sun', operations: 5, issues: 8 }
]

const clientData = [
  { name: 'Elanco Primary', value: 65, color: '#3b82f6' },
  { name: 'Elanco Secondary', value: 25, color: '#10b981' },
  { name: 'Other Clients', value: 10, color: '#f59e0b' }
]

export default function Dashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalOperations: 156,
    activeRules: 23,
    recordsProcessed: 125000,
    dataQualityScore: 94.2
  })

  const handleStartCleaning = () => {
    navigate('/cleaning')
  }

  const handleManageRules = () => {
    navigate('/rules')
  }

  const handleGenerateReport = () => {
    navigate('/reports')
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome to DataHerd - Your intelligent cattle data cleaning platform
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-green-600 border-green-200">
            <CheckCircle className="w-3 h-3 mr-1" />
            System Healthy
          </Badge>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Operations</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalOperations}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeRules}</div>
            <p className="text-xs text-muted-foreground">
              +3 new rules this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Records Processed</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.recordsProcessed.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +8.2% from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Quality Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.dataQualityScore}%</div>
            <Progress value={stats.dataQualityScore} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Operations Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Operations</CardTitle>
            <CardDescription>
              Operations and issues found over the past week
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="operations" fill="#3b82f6" name="Operations" />
                <Bar dataKey="issues" fill="#ef4444" name="Issues Found" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Client Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Client Distribution</CardTitle>
            <CardDescription>
              Data processing distribution by client
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={clientData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {clientData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {clientData.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded-full mr-2" 
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium">{item.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Operations */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Operations</CardTitle>
          <CardDescription>
            Latest data cleaning operations and their status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentOperations.map((operation) => (
              <div key={operation.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {operation.status === 'completed' ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : operation.status === 'in_progress' ? (
                      <Clock className="h-5 w-5 text-yellow-500" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium">{operation.batch}</div>
                    <div className="text-sm text-gray-500">{operation.operation}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {operation.recordsProcessed.toLocaleString()} records
                  </div>
                  <div className="text-sm text-gray-500">
                    {operation.issuesFound} issues found
                  </div>
                </div>
                <div className="text-right">
                  <Badge 
                    variant={operation.status === 'completed' ? 'default' : 
                            operation.status === 'in_progress' ? 'secondary' : 'destructive'}
                  >
                    {operation.status.replace('_', ' ')}
                  </Badge>
                  <div className="text-xs text-gray-500 mt-1">
                    {operation.timestamp}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and shortcuts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={handleStartCleaning}
            >
              <Sparkles className="h-6 w-6" />
              <span>Start New Cleaning</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={handleManageRules}
            >
              <Database className="h-6 w-6" />
              <span>Manage Rules</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={handleGenerateReport}
            >
              <FileText className="h-6 w-6" />
              <span>Generate Report</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

