import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { 
  Play, 
  Eye, 
  RotateCcw, 
  Save, 
  Upload, 
  Download,
  AlertCircle,
  CheckCircle,
  Info,
  Sparkles,
  Database,
  FileText
} from 'lucide-react'
import { toast } from 'sonner'

const sampleData = [
  { id: 1, lotId: "LOT001", weight: 850, breed: "Angus", birthDate: "2023-03-15", status: "original" },
  { id: 2, lotId: "LOT002", weight: 45, breed: "angus", birthDate: "2023-04-20", status: "flagged" },
  { id: 3, lotId: "LOT003", weight: 920, breed: "Holstein", birthDate: "2023-02-10", status: "original" },
  { id: 4, lotId: "LOT004", weight: 1200, breed: "hereford", birthDate: "invalid", status: "flagged" },
  { id: 5, lotId: "LOT005", weight: 780, breed: "Hereford", birthDate: "2023-05-08", status: "original" }
]

const previewChanges = [
  { 
    lotId: "LOT002", 
    field: "weight", 
    original: "45", 
    suggested: "450", 
    reason: "Weight appears to be missing a digit (typical calf weight 400-500 lbs)",
    confidence: 0.85
  },
  { 
    lotId: "LOT002", 
    field: "breed", 
    original: "angus", 
    suggested: "Angus", 
    reason: "Standardize breed capitalization",
    confidence: 0.95
  },
  { 
    lotId: "LOT004", 
    field: "breed", 
    original: "hereford", 
    suggested: "Hereford", 
    reason: "Standardize breed capitalization",
    confidence: 0.95
  },
  { 
    lotId: "LOT004", 
    field: "birthDate", 
    original: "invalid", 
    suggested: "2023-03-01", 
    reason: "Estimated based on weight and typical growth patterns",
    confidence: 0.65
  }
]

export default function DataCleaning() {
  const [batchId, setBatchId] = useState('')
  const [clientName, setClientName] = useState('')
  const [rules, setRules] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [progress, setProgress] = useState(0)
  const [activeTab, setActiveTab] = useState('input')

  const handlePreview = async () => {
    if (!batchId || !rules) {
      toast.error('Please fill in batch ID and cleaning rules')
      return
    }

    setIsProcessing(true)
    setProgress(0)
    
    // Simulate processing
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsProcessing(false)
          setShowPreview(true)
          setActiveTab('preview')
          toast.success('Preview generated successfully!')
          return 100
        }
        return prev + 10
      })
    }, 200)
  }

  const handleApplyChanges = async () => {
    setIsProcessing(true)
    
    // Simulate applying changes
    setTimeout(() => {
      setIsProcessing(false)
      toast.success('Changes applied successfully!')
      setActiveTab('results')
    }, 2000)
  }

  const handleRollback = () => {
    toast.info('Changes rolled back successfully!')
    setShowPreview(false)
    setActiveTab('input')
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Data Cleaning</h1>
          <p className="text-gray-600 mt-1">
            Apply intelligent rules to clean and standardize cattle data
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Upload className="w-4 h-4 mr-2" />
            Import Data
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export Results
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="input">Input & Rules</TabsTrigger>
          <TabsTrigger value="preview" disabled={!showPreview}>Preview Changes</TabsTrigger>
          <TabsTrigger value="results" disabled>Results</TabsTrigger>
          <TabsTrigger value="history" disabled>History</TabsTrigger>
        </TabsList>

        {/* Input Tab */}
        <TabsContent value="input" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Form */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  Batch Information
                </CardTitle>
                <CardDescription>
                  Specify the data batch and client details
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="batchId">Batch ID</Label>
                  <Input
                    id="batchId"
                    placeholder="e.g., ELANCO_2025_001"
                    value={batchId}
                    onChange={(e) => setBatchId(e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="clientName">Client Name</Label>
                  <Select value={clientName} onValueChange={setClientName}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select client" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="elanco_primary">Elanco Primary</SelectItem>
                      <SelectItem value="elanco_secondary">Elanco Secondary</SelectItem>
                      <SelectItem value="other">Other Client</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="rules">Cleaning Rules</Label>
                  <Textarea
                    id="rules"
                    placeholder="Describe your data cleaning rules in natural language. For example:
- Flag weights below 400 lbs or above 1500 lbs as potential errors
- Standardize breed names to proper capitalization
- Validate birth dates are within reasonable range
- Remove duplicate entries based on lot ID"
                    value={rules}
                    onChange={(e) => setRules(e.target.value)}
                    rows={8}
                  />
                </div>

                <div className="flex space-x-2">
                  <Button 
                    onClick={handlePreview} 
                    disabled={isProcessing}
                    className="flex-1"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    Preview Changes
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={handleApplyChanges}
                    disabled={!showPreview || isProcessing}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Apply Now
                  </Button>
                </div>

                {isProcessing && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Processing...</span>
                      <span>{progress}%</span>
                    </div>
                    <Progress value={progress} />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Sample Data */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Sample Data
                </CardTitle>
                <CardDescription>
                  Preview of the data that will be processed
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {sampleData.map((record) => (
                    <div key={record.id} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{record.lotId}</span>
                        <Badge 
                          variant={record.status === 'flagged' ? 'destructive' : 'secondary'}
                        >
                          {record.status}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                        <div>Weight: {record.weight} lbs</div>
                        <div>Breed: {record.breed}</div>
                        <div className="col-span-2">Birth Date: {record.birthDate}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Rule Suggestions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Sparkles className="w-5 h-5 mr-2" />
                Suggested Rules
              </CardTitle>
              <CardDescription>
                Common cleaning rules for cattle data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  "Validate weight ranges (400-1500 lbs for cattle)",
                  "Standardize breed name capitalization",
                  "Check birth date format and validity",
                  "Remove duplicate lot IDs",
                  "Flag missing or null values",
                  "Validate age consistency with weight"
                ].map((rule, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="h-auto p-3 text-left justify-start"
                    onClick={() => setRules(prev => prev + (prev ? '\n' : '') + '- ' + rule)}
                  >
                    {rule}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preview Tab */}
        <TabsContent value="preview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="w-5 h-5 mr-2" />
                Preview Changes
              </CardTitle>
              <CardDescription>
                Review the proposed changes before applying them
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Found {previewChanges.length} potential improvements. Review each change and its confidence level.
                  </AlertDescription>
                </Alert>

                <div className="space-y-4">
                  {previewChanges.map((change, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{change.lotId}</Badge>
                          <Badge variant="secondary">{change.field}</Badge>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">
                            Confidence: {Math.round(change.confidence * 100)}%
                          </span>
                          <div className={`w-3 h-3 rounded-full ${
                            change.confidence > 0.8 ? 'bg-green-500' :
                            change.confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                          }`} />
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mb-3">
                        <div>
                          <Label className="text-xs text-gray-500">Original</Label>
                          <div className="p-2 bg-red-50 border border-red-200 rounded text-sm">
                            {change.original}
                          </div>
                        </div>
                        <div>
                          <Label className="text-xs text-gray-500">Suggested</Label>
                          <div className="p-2 bg-green-50 border border-green-200 rounded text-sm">
                            {change.suggested}
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-600">
                        <strong>Reason:</strong> {change.reason}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex space-x-2 pt-4">
                  <Button onClick={handleApplyChanges} disabled={isProcessing}>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Apply All Changes
                  </Button>
                  <Button variant="outline" onClick={handleRollback}>
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Cancel
                  </Button>
                  <Button variant="outline">
                    <Save className="w-4 h-4 mr-2" />
                    Save as Rule
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Results Tab */}
        <TabsContent value="results" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-500" />
                Operation Complete
              </CardTitle>
              <CardDescription>
                Data cleaning operation completed successfully
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">2,500</div>
                  <div className="text-sm text-blue-600">Records Processed</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">4</div>
                  <div className="text-sm text-green-600">Changes Applied</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">95.2%</div>
                  <div className="text-sm text-purple-600">Data Quality Score</div>
                </div>
              </div>

              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  All changes have been applied successfully. You can now download the cleaned data or generate a detailed report.
                </AlertDescription>
              </Alert>

              <div className="flex space-x-2 mt-4">
                <Button>
                  <Download className="w-4 h-4 mr-2" />
                  Download Cleaned Data
                </Button>
                <Button variant="outline">
                  <FileText className="w-4 h-4 mr-2" />
                  Generate Report
                </Button>
                <Button variant="outline" onClick={handleRollback}>
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Rollback Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

