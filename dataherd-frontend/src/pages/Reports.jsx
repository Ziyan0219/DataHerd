import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DatePickerWithRange } from '@/components/ui/date-range-picker'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { 
  FileText, 
  Download, 
  Calendar, 
  BarChart3, 
  PieChart, 
  TrendingUp,
  Users,
  Database,
  CheckCircle,
  AlertCircle,
  Clock,
  Filter
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart as RechartsPieChart, Pie, Cell, AreaChart, Area } from 'recharts'
import { toast } from 'sonner'

const operationData = [
  { date: '2025-01-13', operations: 8, success: 7, failed: 1, records: 12000 },
  { date: '2025-01-14', operations: 12, success: 11, failed: 1, records: 18500 },
  { date: '2025-01-15', operations: 15, success: 14, failed: 1, records: 22000 },
  { date: '2025-01-16', operations: 10, success: 9, failed: 1, records: 15000 },
  { date: '2025-01-17', operations: 18, success: 17, failed: 1, records: 28000 },
  { date: '2025-01-18', operations: 14, success: 13, failed: 1, records: 21000 },
  { date: '2025-01-19', operations: 16, success: 15, failed: 1, records: 24500 }
]

const clientData = [
  { name: 'Elanco Primary', operations: 45, records: 75000, color: '#3b82f6' },
  { name: 'Elanco Secondary', operations: 28, records: 42000, color: '#10b981' },
  { name: 'Other Clients', operations: 12, records: 18000, color: '#f59e0b' }
]

const ruleUsageData = [
  { rule: 'Weight Validation', usage: 45, success: 94.2 },
  { rule: 'Breed Standardization', usage: 38, success: 98.1 },
  { rule: 'Date Validation', usage: 32, success: 87.5 },
  { rule: 'Duplicate Removal', usage: 28, success: 96.3 },
  { rule: 'Missing Values', usage: 22, success: 82.1 }
]

const qualityTrend = [
  { date: '2025-01-13', score: 89.2 },
  { date: '2025-01-14', score: 90.1 },
  { date: '2025-01-15', score: 91.5 },
  { date: '2025-01-16', score: 90.8 },
  { date: '2025-01-17', score: 92.3 },
  { date: '2025-01-18', score: 93.1 },
  { date: '2025-01-19', score: 94.2 }
]

const recentReports = [
  {
    id: 1,
    name: "Weekly Operations Summary",
    type: "Operations",
    dateRange: "Jan 13-19, 2025",
    status: "completed",
    createdAt: "2025-01-19 16:30",
    size: "2.4 MB"
  },
  {
    id: 2,
    name: "Elanco Primary Client Report",
    type: "Client-Specific",
    dateRange: "Jan 1-19, 2025",
    status: "completed",
    createdAt: "2025-01-19 14:15",
    size: "1.8 MB"
  },
  {
    id: 3,
    name: "Data Quality Analysis",
    type: "Quality",
    dateRange: "Dec 2024",
    status: "completed",
    createdAt: "2025-01-18 11:20",
    size: "3.1 MB"
  }
]

export default function Reports() {
  const [reportType, setReportType] = useState('')
  const [clientFilter, setClientFilter] = useState('')
  const [dateRange, setDateRange] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedReports, setGeneratedReports] = useState([])
  const [showReportModal, setShowReportModal] = useState(false)
  const [currentReport, setCurrentReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Initialize data safely
  React.useEffect(() => {
    try {
      console.log('Reports: Initializing with sample data')
      setGeneratedReports(recentReports || [])
      setLoading(false)
    } catch (err) {
      console.error('Reports: Initialization error:', err)
      setError(err.message)
      setLoading(false)
    }
  }, [])

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-red-800">Error Loading Reports</h2>
          <p className="text-red-600 mt-2">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Reload Page
          </button>
        </div>
      </div>
    )
  }

  const handleGenerateReport = async () => {
    try {
      console.log('Generating report...', { reportType, clientFilter, dateRange })

      if (!reportType) {
        toast.error('Please select a report type')
        return
      }

      // Validate specific requirements for different report types
      if (reportType === 'client' && !clientFilter) {
        toast.error('Please select a client for client-specific reports')
        return
      }

      setIsGenerating(true)
      
      // Simulate report generation with realistic progress
      const steps = [
        'Collecting data...',
        'Processing operations...',
        'Analyzing quality metrics...',
        'Generating visualizations...',
        'Finalizing report...'
      ]
      
      for (let i = 0; i < steps.length; i++) {
        try {
          await new Promise(resolve => setTimeout(resolve, 400))
          toast.info(steps[i])
        } catch (err) {
          console.warn('Toast notification failed:', err)
        }
      }
      
      // Create mock report data
      const reportData = {
        id: Date.now(),
        name: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`,
        type: reportType,
        dateRange: dateRange ? 
          `${dateRange.from?.toLocaleDateString() || 'N/A'} - ${dateRange.to?.toLocaleDateString() || 'N/A'}` : 
          'All time',
        status: 'completed',
        createdAt: new Date().toISOString().replace('T', ' ').split('.')[0],
        size: `${(Math.random() * 3 + 1).toFixed(1)} MB`,
        client: clientFilter || 'All Clients'
      }
      
      console.log('Generated report data:', reportData)
      
      // Add to recent reports
      setGeneratedReports(prev => {
        const newReports = [reportData, ...prev]
        return newReports.slice(0, 10) // Keep only latest 10
      })
      
      setIsGenerating(false)
      setReportType('')
      setClientFilter('')
      setDateRange(null)
      
      toast.success(`${reportData.name} generated successfully! Check the Recent Reports section to download.`)
    } catch (error) {
      console.error('Error generating report:', error)
      setIsGenerating(false)
      toast.error('Error generating report: ' + error.message)
    }
  }

  const handleDownloadReport = (reportId) => {
    const report = generatedReports.find(r => r.id === reportId)
    if (report) {
      // Create mock report content
      const reportContent = generateReportContent(report)
      
      // Create and download file
      const blob = new Blob([reportContent], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${report.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast.success(`${report.name} download started!`)
    } else {
      toast.error('Report not found')
    }
  }

  const handleViewReport = (report) => {
    setCurrentReport(report)
    setShowReportModal(true)
  }

  const generateReportContent = (report) => {
    return `
DataHerd - ${report.name}
${'='.repeat(50)}

Generated: ${report.createdAt}
Type: ${report.type.toUpperCase()}
Client: ${report.client || 'All Clients'}
Date Range: ${report.dateRange}
Status: ${report.status.toUpperCase()}

EXECUTIVE SUMMARY
${'='.repeat(50)}
This ${report.type} report provides comprehensive analysis of cattle data processing operations.

KEY METRICS
${'='.repeat(50)}
- Total Records Processed: 12,450
- Data Quality Score: 94.2%
- Rules Applied: 15
- Issues Resolved: 287
- Processing Time: 3.2 minutes

DETAILED ANALYSIS
${'='.repeat(50)}
1. Data Quality Assessment
   - Completeness: 98.1%
   - Accuracy: 96.3%
   - Consistency: 92.7%

2. Rule Application Summary
   - Weight Validation: 45 records flagged
   - Breed Standardization: 132 records updated  
   - Date Validation: 23 records corrected
   - Duplicate Removal: 15 records removed

3. Quality Improvements
   - Before Processing: 87.3%
   - After Processing: 94.2%
   - Improvement: +6.9 percentage points

RECOMMENDATIONS
${'='.repeat(50)}
- Continue monitoring weight validation thresholds
- Consider implementing automated breed standardization
- Review data sources for consistency improvements

---
Generated by DataHerd - Intelligent Cattle Data Cleaning Platform
Report ID: ${report.id}
`
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-1">
            Generate comprehensive reports and analytics for your data cleaning operations
          </p>
        </div>
        <Button onClick={handleGenerateReport} disabled={isGenerating}>
          <FileText className="w-4 h-4 mr-2" />
          {isGenerating ? 'Generating...' : 'Generate Report'}
        </Button>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="operations">Operations</TabsTrigger>
          <TabsTrigger value="quality">Data Quality</TabsTrigger>
          <TabsTrigger value="generate">Generate</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Operations</p>
                    <p className="text-2xl font-bold">93</p>
                    <p className="text-xs text-green-600">+12% this week</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Records Processed</p>
                    <p className="text-2xl font-bold">141K</p>
                    <p className="text-xs text-green-600">+8.2% this week</p>
                  </div>
                  <Database className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Success Rate</p>
                    <p className="text-2xl font-bold">94.6%</p>
                    <p className="text-xs text-green-600">+2.1% this week</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Clients</p>
                    <p className="text-2xl font-bold">3</p>
                    <p className="text-xs text-gray-500">No change</p>
                  </div>
                  <Users className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Operations Trend */}
            <Card>
              <CardHeader>
                <CardTitle>Operations Trend</CardTitle>
                <CardDescription>Daily operations over the past week</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={operationData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                    <YAxis />
                    <Tooltip labelFormatter={(value) => new Date(value).toLocaleDateString()} />
                    <Area type="monotone" dataKey="operations" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Client Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Client Distribution</CardTitle>
                <CardDescription>Operations by client</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={clientData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="operations"
                    >
                      {clientData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPieChart>
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
                      <span className="text-sm font-medium">{item.operations} ops</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Operations Tab */}
        <TabsContent value="operations" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Success vs Failed Operations */}
            <Card>
              <CardHeader>
                <CardTitle>Operation Success Rate</CardTitle>
                <CardDescription>Success vs failed operations over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={operationData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                    <YAxis />
                    <Tooltip labelFormatter={(value) => new Date(value).toLocaleDateString()} />
                    <Bar dataKey="success" fill="#10b981" name="Successful" />
                    <Bar dataKey="failed" fill="#ef4444" name="Failed" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Rule Usage */}
            <Card>
              <CardHeader>
                <CardTitle>Rule Usage Statistics</CardTitle>
                <CardDescription>Most frequently used rules</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {ruleUsageData.map((rule, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium">{rule.rule}</span>
                          <span className="text-sm text-gray-500">{rule.usage} uses</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${(rule.usage / 50) * 100}%` }}
                          />
                        </div>
                      </div>
                      <Badge variant="outline" className="ml-4">
                        {rule.success}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Records Processed */}
          <Card>
            <CardHeader>
              <CardTitle>Records Processed</CardTitle>
              <CardDescription>Volume of records processed daily</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={operationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value) => [value.toLocaleString(), 'Records']}
                  />
                  <Area type="monotone" dataKey="records" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Quality Tab */}
        <TabsContent value="quality" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Data Quality Trend</CardTitle>
              <CardDescription>Data quality score improvement over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={qualityTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                  <YAxis domain={[80, 100]} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value) => [`${value}%`, 'Quality Score']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#8b5cf6" 
                    strokeWidth={3}
                    dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <TrendingUp className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-green-600">+5.0%</div>
                <div className="text-sm text-gray-600">Quality Improvement</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <AlertCircle className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-orange-600">2.1%</div>
                <div className="text-sm text-gray-600">False Positive Rate</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <CheckCircle className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-600">97.9%</div>
                <div className="text-sm text-gray-600">Accuracy Rate</div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Generate Tab */}
        <TabsContent value="generate" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Report Generation Form */}
            <Card>
              <CardHeader>
                <CardTitle>Generate New Report</CardTitle>
                <CardDescription>
                  Create a custom report with specific filters and date ranges
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="reportType">Report Type</Label>
                  <Select value={reportType} onValueChange={setReportType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select report type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="operations">Operations Summary</SelectItem>
                      <SelectItem value="client">Client-Specific Report</SelectItem>
                      <SelectItem value="quality">Data Quality Analysis</SelectItem>
                      <SelectItem value="rules">Rule Performance Report</SelectItem>
                      <SelectItem value="comprehensive">Comprehensive Report</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="clientFilter">Client Filter</Label>
                  <Select value={clientFilter} onValueChange={setClientFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All clients" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All Clients</SelectItem>
                      <SelectItem value="elanco_primary">Elanco Primary</SelectItem>
                      <SelectItem value="elanco_secondary">Elanco Secondary</SelectItem>
                      <SelectItem value="other">Other Clients</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Date Range</Label>
                  <DatePickerWithRange date={dateRange} setDate={setDateRange} />
                </div>

                <Button 
                  onClick={handleGenerateReport} 
                  disabled={isGenerating}
                  className="w-full"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  {isGenerating ? 'Generating Report...' : 'Generate Report'}
                </Button>
              </CardContent>
            </Card>

            {/* Recent Reports */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Reports</CardTitle>
                <CardDescription>
                  Previously generated reports available for download
                </CardDescription>
              </CardHeader>
              <CardContent>
                {generatedReports.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>No reports generated yet</p>
                    <p className="text-sm">Create your first report above</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {generatedReports.map((report) => (
                      <div key={report.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                        <div className="flex-1">
                          <div className="font-medium">{report.name}</div>
                          <div className="text-sm text-gray-500">
                            {report.type} • {report.dateRange}
                          </div>
                          <div className="text-xs text-gray-400">
                            Created: {report.createdAt} • Size: {report.size}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge 
                            variant={report.status === 'completed' ? 'default' : 'secondary'}
                          >
                            {report.status}
                          </Badge>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewReport(report)}
                          >
                            <FileText className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDownloadReport(report.id)}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Report Preview Modal */}
      <Dialog open={showReportModal} onOpenChange={setShowReportModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Report Preview</DialogTitle>
            <DialogDescription>
              {currentReport && `${currentReport.name} - Generated on ${currentReport.createdAt}`}
            </DialogDescription>
          </DialogHeader>
          
          {currentReport && (
            <div className="space-y-6">
              {/* Report Metadata */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-500">Type</div>
                  <div className="font-medium">{currentReport.type.toUpperCase()}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Client</div>
                  <div className="font-medium">{currentReport.client}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Date Range</div>
                  <div className="font-medium">{currentReport.dateRange}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Size</div>
                  <div className="font-medium">{currentReport.size}</div>
                </div>
              </div>

              {/* Mock Report Content */}
              <Card>
                <CardHeader>
                  <CardTitle>Executive Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p>This {currentReport.type} report provides comprehensive analysis of cattle data processing operations for the specified time period.</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">12,450</div>
                      <div className="text-sm text-blue-600">Records Processed</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">94.2%</div>
                      <div className="text-sm text-green-600">Data Quality Score</div>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">287</div>
                      <div className="text-sm text-purple-600">Issues Resolved</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quality Assessment</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span>Data Completeness</span>
                      <span className="font-medium">98.1%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Data Accuracy</span>
                      <span className="font-medium">96.3%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Consistency Score</span>
                      <span className="font-medium">92.7%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Rule Application Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span>Weight Validation</span>
                      <Badge>45 records flagged</Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span>Breed Standardization</span>
                      <Badge variant="secondary">132 records updated</Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span>Date Validation</span>
                      <Badge variant="outline">23 records corrected</Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span>Duplicate Removal</span>
                      <Badge variant="destructive">15 records removed</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  variant="outline" 
                  onClick={() => handleDownloadReport(currentReport.id)}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Report
                </Button>
                <Button onClick={() => setShowReportModal(false)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

