import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Plus, 
  Edit, 
  Trash2, 
  Copy, 
  Play, 
  Pause,
  Search,
  Filter,
  Database,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react'
import { toast } from 'sonner'

const sampleRules = [
  {
    id: 1,
    name: "Weight Validation",
    description: "Flag weights below 400 lbs or above 1500 lbs as potential errors",
    client: "Elanco Primary",
    category: "Validation",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-19",
    usageCount: 45,
    successRate: 94.2
  },
  {
    id: 2,
    name: "Breed Standardization",
    description: "Standardize breed names to proper capitalization and common naming conventions",
    client: "All Clients",
    category: "Standardization",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-19",
    usageCount: 32,
    successRate: 98.7
  },
  {
    id: 3,
    name: "Date Format Validation",
    description: "Ensure all birth dates are in YYYY-MM-DD format and within reasonable ranges",
    client: "Elanco Secondary",
    category: "Validation",
    isActive: false,
    isPermanent: false,
    lastUsed: "2025-01-15",
    usageCount: 12,
    successRate: 87.5
  },
  {
    id: 4,
    name: "Duplicate Removal",
    description: "Remove duplicate entries based on lot ID and other identifying characteristics",
    client: "Elanco Primary",
    category: "Cleaning",
    isActive: true,
    isPermanent: true,
    lastUsed: "2025-01-18",
    usageCount: 28,
    successRate: 96.1
  },
  {
    id: 5,
    name: "Missing Value Handling",
    description: "Flag or estimate missing values in critical fields like weight and breed",
    client: "All Clients",
    category: "Cleaning",
    isActive: true,
    isPermanent: false,
    lastUsed: "2025-01-17",
    usageCount: 19,
    successRate: 82.3
  }
]

const categories = ["All", "Validation", "Standardization", "Cleaning", "Estimation"]
const clients = ["All Clients", "Elanco Primary", "Elanco Secondary", "Other"]

export default function RuleManagement() {
  const [rules, setRules] = useState(sampleRules)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedClient, setSelectedClient] = useState('All Clients')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingRule, setEditingRule] = useState(null)
  const [newRule, setNewRule] = useState({
    name: '',
    description: '',
    client: '',
    category: '',
    isActive: true,
    isPermanent: false
  })

  const filteredRules = rules.filter(rule => {
    const matchesSearch = rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         rule.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || rule.category === selectedCategory
    const matchesClient = selectedClient === 'All Clients' || rule.client === selectedClient
    
    return matchesSearch && matchesCategory && matchesClient
  })

  const handleCreateRule = () => {
    if (!newRule.name || !newRule.description) {
      toast.error('Please fill in all required fields')
      return
    }

    const rule = {
      id: Date.now(),
      ...newRule,
      lastUsed: new Date().toISOString().split('T')[0],
      usageCount: 0,
      successRate: 0
    }

    setRules([...rules, rule])
    setNewRule({
      name: '',
      description: '',
      client: '',
      category: '',
      isActive: true,
      isPermanent: false
    })
    setIsCreateDialogOpen(false)
    toast.success('Rule created successfully!')
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

  const handleDuplicateRule = (rule) => {
    const duplicatedRule = {
      ...rule,
      id: Date.now(),
      name: `${rule.name} (Copy)`,
      usageCount: 0,
      lastUsed: new Date().toISOString().split('T')[0]
    }
    setRules([...rules, duplicatedRule])
    toast.success('Rule duplicated successfully!')
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Rule Management</h1>
          <p className="text-gray-600 mt-1">
            Create, manage, and monitor your data cleaning rules
          </p>
        </div>
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
                Define a new data cleaning rule with natural language description
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="ruleName">Rule Name</Label>
                  <Input
                    id="ruleName"
                    placeholder="e.g., Weight Validation"
                    value={newRule.name}
                    onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ruleCategory">Category</Label>
                  <Select value={newRule.category} onValueChange={(value) => setNewRule({...newRule, category: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Validation">Validation</SelectItem>
                      <SelectItem value="Standardization">Standardization</SelectItem>
                      <SelectItem value="Cleaning">Cleaning</SelectItem>
                      <SelectItem value="Estimation">Estimation</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="ruleClient">Client</Label>
                <Select value={newRule.client} onValueChange={(value) => setNewRule({...newRule, client: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select client" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="All Clients">All Clients</SelectItem>
                    <SelectItem value="Elanco Primary">Elanco Primary</SelectItem>
                    <SelectItem value="Elanco Secondary">Elanco Secondary</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="ruleDescription">Rule Description</Label>
                <Textarea
                  id="ruleDescription"
                  placeholder="Describe your rule in natural language..."
                  value={newRule.description}
                  onChange={(e) => setNewRule({...newRule, description: e.target.value})}
                  rows={4}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="isActive"
                    checked={newRule.isActive}
                    onCheckedChange={(checked) => setNewRule({...newRule, isActive: checked})}
                  />
                  <Label htmlFor="isActive">Active</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="isPermanent"
                    checked={newRule.isPermanent}
                    onCheckedChange={(checked) => setNewRule({...newRule, isPermanent: checked})}
                  />
                  <Label htmlFor="isPermanent">Permanent Rule</Label>
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
                  {Math.round(rules.reduce((acc, r) => acc + r.successRate, 0) / rules.length)}%
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
                  
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Last Used:</span>
                      <div className="font-medium">{rule.lastUsed}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Usage Count:</span>
                      <div className="font-medium">{rule.usageCount}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Success Rate:</span>
                      <div className="font-medium">{rule.successRate}%</div>
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
                    onClick={() => handleDuplicateRule(rule)}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setEditingRule(rule)}
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

