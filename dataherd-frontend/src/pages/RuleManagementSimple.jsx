import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { 
  Plus, 
  Edit, 
  Trash2,
  Search,
  Database,
  Sparkles,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { toast } from 'sonner'

const sampleRules = [
  {
    id: 1,
    name: "Weight Validation - Yearlings",
    description: "Flag yearlings with weights below 400 lbs or above 900 lbs",
    client: "Elanco Primary",
    category: "Validation",
    field: "weight",
    condition: "< 400 or > 900",
    action: "flag",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-19",
    usageCount: 45,
    successRate: 94.2
  },
  {
    id: 2,
    name: "Weight Validation - Adult Cattle",
    description: "Flag adult cattle with weights below 800 lbs or above 2200 lbs",
    client: "Elanco Primary", 
    category: "Validation",
    field: "weight",
    condition: "< 800 or > 2200",
    action: "flag",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-18",
    usageCount: 67,
    successRate: 96.8
  },
  {
    id: 3,
    name: "Breed Name Standardization",
    description: "Standardize breed names to proper capitalization and common abbreviations",
    client: "All Clients",
    category: "Standardization", 
    field: "breed",
    condition: "non-standard case",
    action: "standardize",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-19",
    usageCount: 89,
    successRate: 98.7
  },
  {
    id: 4,
    name: "Birth Date Format Validation",
    description: "Validate birth dates are in proper format and within reasonable range",
    client: "All Clients",
    category: "Validation",
    field: "birth_date", 
    condition: "invalid format",
    action: "flag",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-17",
    usageCount: 34,
    successRate: 91.2
  },
  {
    id: 5,
    name: "Future Birth Date Check",
    description: "Flag cattle with birth dates in the future",
    client: "All Clients",
    category: "Validation",
    field: "birth_date",
    condition: "future date", 
    action: "flag",
    isActive: true,
    isPermanent: false,
    lastUsed: "2025-01-16",
    usageCount: 12,
    successRate: 100.0
  },
  {
    id: 6,
    name: "Duplicate Lot ID Detection",
    description: "Flag duplicate lot IDs within the same batch",
    client: "Elanco Secondary",
    category: "Validation",
    field: "lot_id",
    condition: "duplicate",
    action: "flag",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-18",
    usageCount: 23,
    successRate: 87.5
  },
  {
    id: 7,
    name: "Health Status Standardization", 
    description: "Standardize health status codes to approved values",
    client: "All Clients",
    category: "Standardization",
    field: "health_status",
    condition: "invalid status",
    action: "standardize",
    isActive: true,
    isPermanent: false,
    lastUsed: "2025-01-15",
    usageCount: 56,
    successRate: 93.8
  },
  {
    id: 8,
    name: "Age Consistency Check",
    description: "Flag cattle where calculated age doesn't match birth date",
    client: "Elanco Primary",
    category: "Validation",
    field: "age",
    condition: "inconsistent with birth_date",
    action: "flag",
    isActive: false,
    isPermanent: false,
    lastUsed: "2025-01-10",
    usageCount: 8,
    successRate: 78.3
  },
  {
    id: 9,
    name: "Missing Weight Estimation",
    description: "Estimate missing weights based on breed, age, and similar cattle",
    client: "Elanco Secondary",
    category: "Estimation", 
    field: "weight",
    condition: "missing",
    action: "estimate",
    isActive: true,
    isPermanent: false,
    lastUsed: "2025-01-14",
    usageCount: 19,
    successRate: 82.1
  },
  {
    id: 10,
    name: "Invalid Breed Name Cleanup",
    description: "Remove or flag cattle records with clearly invalid breed names",
    client: "All Clients",
    category: "Cleaning",
    field: "breed",
    condition: "invalid breed",
    action: "flag",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-13",
    usageCount: 41,
    successRate: 89.7
  },
  {
    id: 11,
    name: "Lot ID Format Validation",
    description: "Validate lot ID follows proper format (e.g., FARM123-LOT456)",
    client: "Elanco Primary",
    category: "Validation",
    field: "lot_id",
    condition: "invalid format",
    action: "flag",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-12",
    usageCount: 28,
    successRate: 94.6
  },
  {
    id: 12,
    name: "Calf Weight Validation",
    description: "Flag calves (under 12 months) with weights above 600 lbs",
    client: "All Clients", 
    category: "Validation",
    field: "weight",
    condition: "> 600",
    action: "flag",
    isActive: true,
    isPermanent: false,
    lastUsed: "2025-01-11",
    usageCount: 15,
    successRate: 91.3
  },
  {
    id: 13,
    name: "Missing Birth Date Cleanup",
    description: "Remove records with missing birth dates that cannot be estimated",
    client: "Other",
    category: "Cleaning",
    field: "birth_date",
    condition: "missing",
    action: "remove",
    isActive: false,
    isPermanent: false,
    lastUsed: "Never",
    usageCount: 0,
    successRate: null
  },
  {
    id: 14,
    name: "Breed Name Contains Numbers",
    description: "Flag breed names that contain numeric characters",
    client: "All Clients",
    category: "Validation", 
    field: "breed",
    condition: "contains numbers",
    action: "flag",
    isActive: true,
    isPermanent: false,
    lastUsed: "2025-01-09",
    usageCount: 7,
    successRate: 85.7
  },
  {
    id: 15,
    name: "Health Status Missing Values",
    description: "Flag records with missing health status for follow-up",
    client: "Elanco Secondary",
    category: "Validation",
    field: "health_status", 
    condition: "missing",
    action: "flag",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-08",
    usageCount: 33,
    successRate: 96.4
  }
]

const categories = ["Validation", "Standardization", "Cleaning", "Estimation"]
const clients = ["All Clients", "Elanco Primary", "Elanco Secondary", "Other"]
const fields = ["weight", "breed", "birth_date", "lot_id", "health_status", "age"]
const conditions = {
  weight: ["< value", "> value", "between values", "missing"],
  breed: ["missing", "non-standard case", "invalid breed", "contains numbers"],
  birth_date: ["missing", "invalid format", "future date", "too old"],
  lot_id: ["missing", "duplicate", "invalid format"],
  health_status: ["missing", "invalid status"],
  age: ["< value", "> value", "inconsistent with birth_date"]
}
const actions = ["flag", "remove", "standardize", "estimate", "validate", "correct"]

export default function RuleManagementSimple() {
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedClient, setSelectedClient] = useState('All Clients')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingRule, setEditingRule] = useState(null)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  
  const [newRule, setNewRule] = useState({
    name: '',
    client: '',
    category: '',
    field: '',
    condition: '',
    conditionValue: '',
    action: '',
    isActive: true,
    isPermanent: false
  })

  // Initialize data safely
  useEffect(() => {
    try {
      console.log('RuleManagement: Initializing with sample data')
      setRules(sampleRules)
      setLoading(false)
    } catch (err) {
      console.error('RuleManagement: Initialization error:', err)
      setLoading(false)
      toast.error('Failed to load rules')
    }
  }, [])

  const filteredRules = rules.filter(rule => {
    const matchesSearch = rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         rule.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || rule.category === selectedCategory
    const matchesClient = selectedClient === 'All Clients' || rule.client === selectedClient
    
    return matchesSearch && matchesCategory && matchesClient
  })

  const handleCreateRule = () => {
    try {
      console.log('Creating rule:', newRule)
      
      if (!newRule.name || !newRule.client || !newRule.category || !newRule.field || !newRule.condition || !newRule.action) {
        toast.error('Please fill in all required fields')
        return
      }

      const description = generateRuleDescription(newRule)
      
      const rule = {
        id: Date.now(),
        name: newRule.name,
        description,
        client: newRule.client,
        category: newRule.category,
        field: newRule.field,
        condition: newRule.condition + (newRule.conditionValue ? ` (${newRule.conditionValue})` : ''),
        action: newRule.action,
        isActive: newRule.isActive,
        isPermanent: newRule.isPermanent,
        lastUsed: 'Never',
        usageCount: 0,
        successRate: null
      }

      console.log('New rule created:', rule)
      setRules(prev => [...prev, rule])
      
      // Reset form
      setNewRule({
        name: '',
        client: '',
        category: '',
        field: '',
        condition: '',
        conditionValue: '',
        action: '',
        isActive: true,
        isPermanent: false
      })
      
      setIsCreateDialogOpen(false)
      toast.success('Rule created successfully!')
    } catch (error) {
      console.error('Error creating rule:', error)
      toast.error('Error creating rule: ' + error.message)
    }
  }

  const generateRuleDescription = (rule) => {
    const fieldName = rule.field.replace('_', ' ')
    const actionText = {
      flag: 'flag as error',
      remove: 'remove record',
      standardize: 'standardize value',
      estimate: 'estimate missing value',
      validate: 'validate format',
      correct: 'correct value'
    }
    
    return `${rule.action === 'flag' ? 'Flag' : rule.action.charAt(0).toUpperCase() + rule.action.slice(1)} records where ${fieldName} ${rule.condition}${rule.conditionValue ? ` ${rule.conditionValue}` : ''}`
  }

  const handleEditRule = (rule) => {
    setEditingRule(rule)
    setNewRule({
      name: rule.name,
      client: rule.client,
      category: rule.category,
      field: rule.field,
      condition: rule.condition.split(' (')[0], // Remove value part
      conditionValue: rule.condition.includes('(') ? rule.condition.split('(')[1]?.replace(')', '') : '',
      action: rule.action,
      isActive: rule.isActive,
      isPermanent: rule.isPermanent
    })
    setIsEditDialogOpen(true)
  }

  const handleUpdateRule = () => {
    try {
      if (!newRule.name || !newRule.client || !newRule.category || !newRule.field || !newRule.condition || !newRule.action) {
        toast.error('Please fill in all required fields')
        return
      }

      const description = generateRuleDescription(newRule)
      
      const updatedRule = {
        ...editingRule,
        name: newRule.name,
        description,
        client: newRule.client,
        category: newRule.category,
        field: newRule.field,
        condition: newRule.condition + (newRule.conditionValue ? ` (${newRule.conditionValue})` : ''),
        action: newRule.action,
        isActive: newRule.isActive,
        isPermanent: newRule.isPermanent
      }

      setRules(rules.map(rule => rule.id === editingRule.id ? updatedRule : rule))
      
      setEditingRule(null)
      setNewRule({
        name: '',
        client: '',
        category: '',
        field: '',
        condition: '',
        conditionValue: '',
        action: '',
        isActive: true,
        isPermanent: false
      })
      setIsEditDialogOpen(false)
      toast.success('Rule updated successfully!')
    } catch (error) {
      console.error('Error updating rule:', error)
      toast.error('Error updating rule: ' + error.message)
    }
  }

  const handleToggleRule = (id) => {
    setRules(rules.map(rule => 
      rule.id === id ? { ...rule, isActive: !rule.isActive } : rule
    ))
    toast.success('Rule status updated!')
  }

  const handleDeleteRule = (id) => {
    setRules(rules.filter(rule => rule.id !== id))
    toast.success('Rule deleted successfully!')
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Rule Management</h1>
          <p className="text-gray-600 mt-1">
            Create and manage data cleaning rules with simple parameter selection
          </p>
        </div>
        
        {/* Create Rule Dialog */}
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Rule
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Rule</DialogTitle>
              <DialogDescription>
                Create a data cleaning rule by selecting parameters
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Rule Name *</Label>
                  <Input
                    placeholder="e.g., Weight Validation"
                    value={newRule.name}
                    onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Category *</Label>
                  <Select value={newRule.category} onValueChange={(value) => setNewRule({...newRule, category: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(cat => (
                        <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Client *</Label>
                <Select value={newRule.client} onValueChange={(value) => setNewRule({...newRule, client: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select client" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.map(client => (
                      <SelectItem key={client} value={client}>{client}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Field *</Label>
                  <Select value={newRule.field} onValueChange={(value) => setNewRule({...newRule, field: value, condition: ''})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select field" />
                    </SelectTrigger>
                    <SelectContent>
                      {fields.map(field => (
                        <SelectItem key={field} value={field}>{field.replace('_', ' ')}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Condition *</Label>
                  <Select 
                    value={newRule.condition} 
                    onValueChange={(value) => setNewRule({...newRule, condition: value})}
                    disabled={!newRule.field}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select condition" />
                    </SelectTrigger>
                    <SelectContent>
                      {newRule.field && conditions[newRule.field]?.map(condition => (
                        <SelectItem key={condition} value={condition}>{condition}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {(newRule.condition?.includes('value') || newRule.condition?.includes('between')) && (
                <div className="space-y-2">
                  <Label>Value {newRule.condition?.includes('between') ? '(min-max)' : ''}</Label>
                  <Input
                    placeholder={newRule.condition?.includes('between') ? "400-1500" : "400"}
                    value={newRule.conditionValue}
                    onChange={(e) => setNewRule({...newRule, conditionValue: e.target.value})}
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label>Action *</Label>
                <Select value={newRule.action} onValueChange={(value) => setNewRule({...newRule, action: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select action" />
                  </SelectTrigger>
                  <SelectContent>
                    {actions.map(action => (
                      <SelectItem key={action} value={action}>
                        {action.charAt(0).toUpperCase() + action.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={newRule.isActive}
                    onCheckedChange={(checked) => setNewRule({...newRule, isActive: checked})}
                  />
                  <Label>Active</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={newRule.isPermanent}
                    onCheckedChange={(checked) => setNewRule({...newRule, isPermanent: checked})}
                  />
                  <Label>Permanent Rule</Label>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateRule}>
                  Create Rule
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Edit Rule Dialog */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Edit Rule</DialogTitle>
              <DialogDescription>
                Modify the existing rule parameters
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Rule Name *</Label>
                  <Input
                    placeholder="e.g., Weight Validation"
                    value={newRule.name}
                    onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Category *</Label>
                  <Select value={newRule.category} onValueChange={(value) => setNewRule({...newRule, category: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(cat => (
                        <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Client *</Label>
                <Select value={newRule.client} onValueChange={(value) => setNewRule({...newRule, client: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select client" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.map(client => (
                      <SelectItem key={client} value={client}>{client}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Field *</Label>
                  <Select value={newRule.field} onValueChange={(value) => setNewRule({...newRule, field: value, condition: ''})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select field" />
                    </SelectTrigger>
                    <SelectContent>
                      {fields.map(field => (
                        <SelectItem key={field} value={field}>{field.replace('_', ' ')}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Condition *</Label>
                  <Select 
                    value={newRule.condition} 
                    onValueChange={(value) => setNewRule({...newRule, condition: value})}
                    disabled={!newRule.field}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select condition" />
                    </SelectTrigger>
                    <SelectContent>
                      {newRule.field && conditions[newRule.field]?.map(condition => (
                        <SelectItem key={condition} value={condition}>{condition}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {(newRule.condition?.includes('value') || newRule.condition?.includes('between')) && (
                <div className="space-y-2">
                  <Label>Value {newRule.condition?.includes('between') ? '(min-max)' : ''}</Label>
                  <Input
                    placeholder={newRule.condition?.includes('between') ? "400-1500" : "400"}
                    value={newRule.conditionValue}
                    onChange={(e) => setNewRule({...newRule, conditionValue: e.target.value})}
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label>Action *</Label>
                <Select value={newRule.action} onValueChange={(value) => setNewRule({...newRule, action: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select action" />
                  </SelectTrigger>
                  <SelectContent>
                    {actions.map(action => (
                      <SelectItem key={action} value={action}>
                        {action.charAt(0).toUpperCase() + action.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={newRule.isActive}
                    onCheckedChange={(checked) => setNewRule({...newRule, isActive: checked})}
                  />
                  <Label>Active</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={newRule.isPermanent}
                    onCheckedChange={(checked) => setNewRule({...newRule, isPermanent: checked})}
                  />
                  <Label>Permanent Rule</Label>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => {
                  setIsEditDialogOpen(false)
                  setEditingRule(null)
                  setNewRule({
                    name: '',
                    client: '',
                    category: '',
                    field: '',
                    condition: '',
                    conditionValue: '',
                    action: '',
                    isActive: true,
                    isPermanent: false
                  })
                }}>
                  Cancel
                </Button>
                <Button onClick={handleUpdateRule}>
                  Update Rule
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Rules</p>
                <p className="text-2xl font-bold">{rules.length}</p>
              </div>
              <Database className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Rules</p>
                <p className="text-2xl font-bold">{rules.filter(r => r.isActive).length}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Permanent Rules</p>
                <p className="text-2xl font-bold">{rules.filter(r => r.isPermanent).length}</p>
              </div>
              <Sparkles className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Success Rate</p>
                <p className="text-2xl font-bold">
                  {(() => {
                    const rulesWithSuccessRate = rules.filter(r => r.successRate !== null)
                    if (rulesWithSuccessRate.length === 0) return 'N/A'
                    return Math.round(rulesWithSuccessRate.reduce((acc, r) => acc + r.successRate, 0) / rulesWithSuccessRate.length) + '%'
                  })()}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search rules..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All">All Categories</SelectItem>
                {categories.map(category => (
                  <SelectItem key={category} value={category}>{category}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedClient} onValueChange={setSelectedClient}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {clients.map(client => (
                  <SelectItem key={client} value={client}>{client}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Rules List */}
      <div className="space-y-4">
        {filteredRules.map((rule) => (
          <Card key={rule.id}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold">{rule.name}</h3>
                    <Badge variant={rule.category === 'Validation' ? 'default' : 
                                  rule.category === 'Standardization' ? 'secondary' :
                                  rule.category === 'Cleaning' ? 'outline' : 'destructive'}>
                      {rule.category}
                    </Badge>
                    <Badge variant="outline">{rule.client}</Badge>
                    {rule.isPermanent && (
                      <Badge variant="secondary">
                        <Sparkles className="w-3 h-3 mr-1" />
                        Permanent
                      </Badge>
                    )}
                  </div>
                  
                  <p className="text-gray-600 mb-4">{rule.description}</p>
                  
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Field:</span>
                      <div className="font-medium">{rule.field?.replace('_', ' ')}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Condition:</span>
                      <div className="font-medium">{rule.condition}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Action:</span>
                      <div className="font-medium">{rule.action}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Success Rate:</span>
                      <div className="font-medium">
                        {rule.successRate === null ? 'N/A' : `${rule.successRate}%`}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={rule.isActive}
                    onCheckedChange={() => handleToggleRule(rule.id)}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEditRule(rule)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDeleteRule(rule.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredRules.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No rules found</h3>
            <p className="text-gray-600 mb-4">
              No rules match your current filters. Try adjusting your search criteria.
            </p>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Rule
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}