import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { 
  Upload, 
  Sparkles, 
  Share2, 
  FileText, 
  Mail, 
  MessageSquare, 
  BarChart3,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  Copy,
  ExternalLink
} from 'lucide-react'
import './App.css'

function App() {
  const [content, setContent] = useState({
    title: '',
    text: ''
  })
  const [uploadMode, setUploadMode] = useState('text') // 'text' or 'file'
  const [selectedFile, setSelectedFile] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    setSelectedFile(file)
    if (file && !content.title) {
      // Auto-fill title with filename (without extension)
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "")
      setContent({...content, title: nameWithoutExt})
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validation based on upload mode
    if (uploadMode === 'text') {
      if (!content.title.trim() || !content.text.trim()) {
        setError('Please provide both title and content.')
        return
      }
    } else if (uploadMode === 'file') {
      if (!selectedFile) {
        setError('Please select a file to upload.')
        return
      }
    }

    setIsProcessing(true)
    setError(null)
    setResults(null)
    setProgress(0)

    // Simulate progress UI
    const progressSteps = [10, 30, 60, 80, 100]
    for (let i = 0; i < progressSteps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 500))
      setProgress(progressSteps[i])
    }

    try {
      let response
      
      if (uploadMode === 'text') {
        // Text upload
        console.log('🔄 Attempting to connect to:', '/api/content/upload')
        response = await fetch('/api/content/upload', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: content.title,
            content: content.text
          })
        })
        console.log('✅ Response received:', response.status)
      } else {
        // File upload
        const formData = new FormData()
        formData.append('file', selectedFile)
        formData.append('title', content.title)
        
        response = await fetch('/api/content/upload-file', {
          method: 'POST',
          body: formData
        })
      }
      if (!response.ok) {
        throw new Error('Failed to process content. Please try again.')
      }
      const data = await response.json()
      
      // Start polling for content status
      if (data.content_id) {
        await pollContentStatus(data.content_id)
      } else {
        setResults(data)
      }
    } catch (err) {
      console.error('❌ Upload error:', err)
      console.error('❌ Error details:', {
        message: err.message,
        name: err.name,
        stack: err.stack
      })
      setError(err.message || 'An error occurred while processing content.')
      setIsProcessing(false)
    }
  }

  const pollContentStatus = async (contentId) => {
    try {
      const maxAttempts = 60 // 60 seconds max (increased timeout)
      let attempts = 0
      
      while (attempts < maxAttempts) {
        const statusResponse = await fetch(`/api/content/${contentId}/status`)
        if (!statusResponse.ok) {
          throw new Error('Failed to check content status')
        }
        
        const statusData = await statusResponse.json()
        console.log(`Polling attempt ${attempts + 1}: Status = ${statusData.status}, Progress = ${statusData.progress}`)
        
        if (statusData.status === 'completed') {
          setResults(statusData)
          setIsProcessing(false)
          return
        } else if (statusData.status === 'error') {
          throw new Error('Content processing failed: ' + (statusData.error || 'Unknown error'))
        }
        
        // Update progress if available
        if (statusData.progress) {
          setProgress(Math.round(statusData.progress * 100))
        }
        
        // Wait 1 second before next poll
        await new Promise(resolve => setTimeout(resolve, 1000))
        attempts++
      }
      
      throw new Error('Content processing timed out after 60 seconds. The content may still be processing in the background.')
    } catch (err) {
      setError(err.message || 'An error occurred while checking content status.')
      setIsProcessing(false)
    }
  }

  const [isDistributing, setIsDistributing] = useState(false)
  const [distributionResults, setDistributionResults] = useState([])
  const [distributionError, setDistributionError] = useState(null)

  const handleDistribute = async (platforms) => {
    if (!results || !results.id) {
      setDistributionError('No content available for distribution')
      return
    }

    if (isDistributing) {
      return // Prevent multiple simultaneous distributions
    }

    setIsDistributing(true)
    setDistributionResults([])
    setDistributionError(null)

    try {
      // Call backend distribution API
      const response = await fetch(`/api/content/${results.id}/distribute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platforms: platforms
        })
      })

      if (!response.ok) {
        throw new Error('Failed to distribute content')
      }

      const data = await response.json()

      // Poll for distribution logs
      await pollDistributionLogs(results.id, platforms)

    } catch (error) {
      setDistributionError(error.message)
    } finally {
      setIsDistributing(false)
    }
  }

  // Poll backend for distribution logs/results
  const pollDistributionLogs = async (contentId, platforms) => {
    const maxAttempts = 30 // 30 seconds max
    let attempts = 0
    let logs = []
    while (attempts < maxAttempts) {
      try {
        const logResponse = await fetch(`/api/distribution_logs?content_id=${contentId}`)
        if (!logResponse.ok) {
          throw new Error('Failed to fetch distribution logs')
        }
        const logData = await logResponse.json()
        logs = logData.logs || []
        // Only show logs for selected platforms
        const filtered = logs.filter(log => platforms.includes(log.platform))
        setDistributionResults(filtered)
        // If all are posted or failed, stop polling
        if (filtered.length > 0 && filtered.every(log => ['posted', 'failed'].includes(log.status))) {
          return
        }
      } catch (err) {
        setDistributionError(err.message)
        return
      }
      await new Promise(resolve => setTimeout(resolve, 1000))
      attempts++
    }
    setDistributionError('Distribution timed out. Some platforms may still be posting.')
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  const getStatusIcon = (status) => {
    if (isProcessing) {
      return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
    }
    return <CheckCircle className="h-4 w-4 text-green-500" />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-indigo-900 to-blue-900 text-white font-sans">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="h-10 w-10 text-indigo-400 animate-bounce" />
            <h1 className="text-5xl font-extrabold tracking-tight text-white drop-shadow-lg">Smart Content Repurposing Engine</h1>
          </div>
          <p className="text-2xl text-indigo-200 max-w-2xl mx-auto font-light">
            Transform your long-form content into engaging, platform-optimized formats with <span className="font-semibold text-blue-300">AI-powered automation</span>
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          {!results ? (
            /* Upload Form */
            <Card className="mb-12 shadow-2xl border-0 bg-gradient-to-br from-indigo-800 to-blue-800 animate-fade-in">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-white">
                  <Upload className="h-6 w-6" />
                  <span className="text-2xl font-bold">Upload Your Content</span>
                </CardTitle>
                <CardDescription className="text-indigo-200">
                  Provide your long-form content and let our <span className="font-semibold text-blue-300">AI</span> transform it into multiple engaging formats
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs value={uploadMode} onValueChange={setUploadMode} className="mb-6">
                  <TabsList className="grid w-full grid-cols-2 bg-gray-800">
                    <TabsTrigger value="text" className="text-white data-[state=active]:bg-indigo-600">
                      <MessageSquare className="mr-2 h-4 w-4" />
                      Text Input
                    </TabsTrigger>
                    <TabsTrigger value="file" className="text-white data-[state=active]:bg-indigo-600">
                      <Upload className="mr-2 h-4 w-4" />
                      File Upload
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="text">
                    <form onSubmit={handleSubmit} className="space-y-6">
                      <div>
                        <label className="block text-base font-semibold mb-2 text-indigo-200">Content Title</label>
                        <Input
                          className="bg-gray-800 text-white border-0 focus:ring-2 focus:ring-indigo-500"
                          placeholder="Enter a descriptive title for your content..."
                          value={content.title}
                          onChange={(e) => setContent({...content, title: e.target.value})}
                          disabled={isProcessing}
                        />
                      </div>
                      <div>
                        <label className="block text-base font-semibold mb-2 text-indigo-200">Long-form Content</label>
                        <Textarea
                          className="bg-gray-800 text-white border-0 focus:ring-2 focus:ring-indigo-500"
                          placeholder="Paste your blog post, article, whitepaper, or any long-form content here..."
                          value={content.text}
                          onChange={(e) => setContent({...content, text: e.target.value})}
                          rows={12}
                          disabled={isProcessing}
                        />
                      </div>
                      <Button 
                        type="submit" 
                        className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold text-lg py-3 rounded-xl shadow-lg hover:scale-105 transition-transform duration-200"
                        disabled={isProcessing}
                        size="lg"
                      >
                        {isProcessing ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Processing Content...
                          </>
                        ) : (
                          <>
                            <Sparkles className="mr-2 h-5 w-5 animate-bounce" />
                            Start AI Processing
                          </>
                        )}
                      </Button>
                    </form>
                  </TabsContent>
                  
                  <TabsContent value="file">
                    <form onSubmit={handleSubmit} className="space-y-6">
                      <div>
                        <label className="block text-base font-semibold mb-2 text-indigo-200">Content Title (Optional)</label>
                        <Input
                          className="bg-gray-800 text-white border-0 focus:ring-2 focus:ring-indigo-500"
                          placeholder="Enter title or leave blank to use filename..."
                          value={content.title}
                          onChange={(e) => setContent({...content, title: e.target.value})}
                          disabled={isProcessing}
                        />
                      </div>
                      <div>
                        <label className="block text-base font-semibold mb-2 text-indigo-200">Upload Document</label>
                        <div className="flex items-center justify-center w-full">
                          <label htmlFor="file-upload" className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-800 hover:bg-gray-700">
                            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                              {selectedFile ? (
                                <>
                                  <FileText className="w-8 h-8 mb-2 text-green-400" />
                                  <p className="text-sm text-green-400 font-semibold">{selectedFile.name}</p>
                                  <p className="text-xs text-gray-400">Click to change file</p>
                                </>
                              ) : (
                                <>
                                  <Upload className="w-8 h-8 mb-2 text-gray-400" />
                                  <p className="mb-2 text-sm text-gray-400">
                                    <span className="font-semibold">Click to upload</span> or drag and drop
                                  </p>
                                  <p className="text-xs text-gray-400">PDF, DOCX, TXT, XLSX files supported</p>
                                </>
                              )}
                            </div>
                            <input
                              id="file-upload"
                              type="file"
                              className="hidden"
                              accept=".pdf,.docx,.doc,.txt,.xlsx,.xls"
                              onChange={handleFileChange}
                              disabled={isProcessing}
                            />
                          </label>
                        </div>
                      </div>
                      <Button 
                        type="submit" 
                        className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold text-lg py-3 rounded-xl shadow-lg hover:scale-105 transition-transform duration-200"
                        disabled={isProcessing || !selectedFile}
                        size="lg"
                      >
                        {isProcessing ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Processing File...
                          </>
                        ) : (
                          <>
                            <Upload className="mr-2 h-5 w-5" />
                            Process File with AI
                          </>
                        )}
                      </Button>
                    </form>
                  </TabsContent>
                </Tabs>
                {/* Processing Status */}
                {isProcessing && (
                  <div className="mt-8 p-6 bg-gradient-to-r from-indigo-900 to-blue-900 rounded-xl shadow-lg animate-pulse">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon('processing')}
                      <span className="font-semibold text-indigo-200">Processing Status</span>
                    </div>
                    <Progress value={progress} className="mb-2" />
                    <p className="text-base text-indigo-200">
                      {progress < 30 && "Analyzing content structure and themes..."}
                      {progress >= 30 && progress < 60 && "Extracting key insights and keywords..."}
                      {progress >= 60 && progress < 100 && "Generating repurposed content formats..."}
                      {progress >= 100 && "Processing completed!"}
                    </p>
                  </div>
                )}
                {error && (
                  <Alert className="mt-6" variant="destructive">
                    <AlertCircle className="h-5 w-5" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          ) : (
            /* Results Display */
            <div className="space-y-10 animate-fade-in">
              {/* Header with original content info */}
              <Card className="shadow-xl border-0 bg-gradient-to-br from-indigo-800 to-blue-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3 text-white">
                    <CheckCircle className="h-6 w-6 text-green-400" />
                    <span className="text-2xl font-bold">Processing Complete</span>
                  </CardTitle>
                  <CardDescription className="text-indigo-200">
                    Your content "{results.title}" has been successfully analyzed and repurposed
                  </CardDescription>
                </CardHeader>
              </Card>
              {/* Analysis Results */}
              {results.analysis_results && (
                <Card className="shadow-lg border-0 bg-gradient-to-br from-indigo-900 to-blue-900">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-white">
                      <BarChart3 className="h-6 w-6" />
                      <span className="text-xl font-bold">Content Analysis</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      <div>
                        <h4 className="font-semibold mb-2 text-indigo-200">Main Theme</h4>
                        <Badge variant="secondary" className="text-base px-3 py-1 bg-blue-700 text-white">{results.analysis_results.main_theme}</Badge>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2 text-indigo-200">Tone</h4>
                        <Badge variant="outline" className="text-base px-3 py-1 bg-indigo-700 text-white">{results.analysis_results.tone}</Badge>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2 text-indigo-200">Sentiment</h4>
                        <Badge variant={results.analysis_results.sentiment === 'positive' ? 'default' : 'secondary'} className="text-base px-3 py-1 bg-green-700 text-white">
                          {results.analysis_results.sentiment}
                        </Badge>
                      </div>
                    </div>
                    <Separator className="my-6" />
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2 text-indigo-200">Key Topics</h4>
                        <div className="flex flex-wrap gap-2">
                          {results.analysis_results.key_topics?.map((topic, index) => (
                            <Badge key={index} variant="outline" className="bg-indigo-800 text-white px-2 py-1">{topic}</Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2 text-indigo-200">Keywords</h4>
                        <div className="flex flex-wrap gap-2">
                          {results.analysis_results.keywords?.map((keyword, index) => (
                            <Badge key={index} variant="secondary" className="bg-blue-800 text-white px-2 py-1">{keyword}</Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
              {/* Repurposed Content */}
              {results.repurposed_outputs && (
                <Card className="shadow-lg border-0 bg-gradient-to-br from-indigo-900 to-blue-900">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-white">
                      <Share2 className="h-6 w-6" />
                      <span className="text-xl font-bold">Repurposed Content</span>
                    </CardTitle>
                    <CardDescription className="text-indigo-200">
                      Your content has been transformed into multiple platform-optimized formats
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Tabs defaultValue="social" className="w-full">
                      <TabsList className="grid w-full grid-cols-4">
                        <TabsTrigger value="social">Social Media</TabsTrigger>
                        <TabsTrigger value="email">Email</TabsTrigger>
                        <TabsTrigger value="article">Article</TabsTrigger>
                        <TabsTrigger value="infographic">Infographic</TabsTrigger>
                      </TabsList>
                      {/* Social Media Posts */}
                      <TabsContent value="social" className="space-y-4">
                        {results.repurposed_outputs.social_posts?.map((post, index) => (
                          <Card key={index} className="bg-gradient-to-r from-blue-800 to-indigo-800 border-0 shadow-md">
                            <CardHeader>
                              <CardTitle className="flex items-center justify-between text-white">
                                <div className="flex items-center gap-2">
                                  <MessageSquare className="h-5 w-5" />
                                  {post.platform.charAt(0).toUpperCase() + post.platform.slice(1)}
                                </div>
                                <div className="flex gap-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => copyToClipboard(post.text)}
                                    className="bg-indigo-700 text-white border-0 hover:bg-indigo-600"
                                  >
                                    <Copy className="h-4 w-4" />
                                  </Button>
                                </div>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="mb-3 text-indigo-100 text-base font-medium">{post.text}</p>
                              <div className="flex flex-wrap gap-1 mb-2">
                                {post.hashtags?.map((tag, tagIndex) => (
                                  <Badge key={tagIndex} variant="secondary" className="text-xs bg-blue-700 text-white">
                                    #{tag}
                                  </Badge>
                                ))}
                              </div>
                              <p className="text-xs text-indigo-300">
                                {post.character_count} characters
                              </p>
                            </CardContent>
                          </Card>
                        ))}
                      </TabsContent>
                      {/* Email Snippets */}
                      <TabsContent value="email" className="space-y-4">
                        {results.repurposed_outputs.email_snippets?.map((email, index) => (
                          <Card key={index} className="bg-gradient-to-r from-blue-800 to-indigo-800 border-0 shadow-md">
                            <CardHeader>
                              <CardTitle className="flex items-center justify-between text-white">
                                <div className="flex items-center gap-2">
                                  <Mail className="h-5 w-5" />
                                  {email.type.replace('_', ' ').toUpperCase()}
                                </div>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => copyToClipboard(`Subject: ${email.subject}\n\n${email.content}\n\n${email.cta}`)}
                                  className="bg-indigo-700 text-white border-0 hover:bg-indigo-600"
                                >
                                  <Copy className="h-4 w-4" />
                                </Button>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3">
                                <div>
                                  <h5 className="font-semibold text-sm text-indigo-200">Subject Line</h5>
                                  <p className="text-sm bg-indigo-900 p-2 rounded text-white">{email.subject}</p>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-sm text-indigo-200">Content</h5>
                                  <p className="text-sm text-indigo-100">{email.content}</p>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-sm text-indigo-200">Call to Action</h5>
                                  <Badge variant="default" className="bg-blue-700 text-white">{email.cta}</Badge>
                                </div>
                                <p className="text-xs text-indigo-300">
                                  {email.word_count} words
                                </p>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </TabsContent>
                      {/* Short Article */}
                      <TabsContent value="article">
                        {results.repurposed_outputs.short_article && (
                          <Card className="bg-gradient-to-r from-blue-800 to-indigo-800 border-0 shadow-md">
                            <CardHeader>
                              <CardTitle className="flex items-center justify-between text-white">
                                <div className="flex items-center gap-2">
                                  <FileText className="h-5 w-5" />
                                  Short Article
                                </div>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => copyToClipboard(`${results.repurposed_outputs.short_article.headline}\n\n${results.repurposed_outputs.short_article.introduction}\n\n${results.repurposed_outputs.short_article.main_content}\n\n${results.repurposed_outputs.short_article.conclusion}`)}
                                  className="bg-indigo-700 text-white border-0 hover:bg-indigo-600"
                                >
                                  <Copy className="h-4 w-4" />
                                </Button>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-4">
                                <div>
                                  <h3 className="text-2xl font-bold mb-2 text-white">
                                    {results.repurposed_outputs.short_article.headline}
                                  </h3>
                                  <Badge variant="outline" className="bg-indigo-700 text-white">
                                    {results.repurposed_outputs.short_article.reading_time}
                                  </Badge>
                                </div>
                                <div className="prose max-w-none text-indigo-100">
                                  <p>{results.repurposed_outputs.short_article.introduction}</p>
                                  <p>{results.repurposed_outputs.short_article.main_content}</p>
                                  <p>{results.repurposed_outputs.short_article.conclusion}</p>
                                </div>
                                <p className="text-xs text-indigo-300">
                                  Approximately {results.repurposed_outputs.short_article.word_count} words
                                </p>
                              </div>
                            </CardContent>
                          </Card>
                        )}
                      </TabsContent>
                      {/* Infographic Data */}
                      <TabsContent value="infographic">
                        {results.repurposed_outputs.infographic_data && (
                          <Card className="bg-gradient-to-r from-blue-800 to-indigo-800 border-0 shadow-md">
                            <CardHeader>
                              <CardTitle className="flex items-center justify-between text-white">
                                <div className="flex items-center gap-2">
                                  <BarChart3 className="h-5 w-5" />
                                  Infographic Data
                                </div>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => copyToClipboard(JSON.stringify(results.repurposed_outputs.infographic_data, null, 2))}
                                  className="bg-indigo-700 text-white border-0 hover:bg-indigo-600"
                                >
                                  <Copy className="h-4 w-4" />
                                </Button>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-4">
                                <h3 className="text-xl font-bold text-white">
                                  {results.repurposed_outputs.infographic_data.title}
                                </h3>
                                <div>
                                  <h4 className="font-semibold mb-2 text-indigo-200">Key Statistics</h4>
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {results.repurposed_outputs.infographic_data.statistics?.map((stat, index) => (
                                      <div key={index} className="bg-indigo-900 p-3 rounded shadow">
                                        <div className="text-2xl font-bold text-blue-300">{stat.value}</div>
                                        <div className="text-sm text-indigo-100">{stat.label}</div>
                                        <div className="text-xs text-indigo-400">Icon: {stat.icon_suggestion}</div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                                <div>
                                  <h4 className="font-semibold mb-2 text-indigo-200">Sections</h4>
                                  <div className="space-y-2">
                                    {results.repurposed_outputs.infographic_data.sections?.map((section, index) => (
                                      <div key={index} className="border-l-4 border-blue-400 pl-3">
                                        <h5 className="font-semibold text-white">{section.title}</h5>
                                        <p className="text-sm text-indigo-100">{section.description}</p>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                                <div>
                                  <h4 className="font-semibold mb-2 text-indigo-200">Call to Action</h4>
                                  <Badge variant="default" className="bg-blue-700 text-white">{results.repurposed_outputs.infographic_data.cta}</Badge>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )}
                      </TabsContent>
                    </Tabs>
                    {/* Distribution Section */}
                    <Separator className="my-10" />
                    <div className="space-y-6">
                      <h3 className="text-2xl font-bold flex items-center gap-3 text-white">
                        <Share2 className="h-6 w-6" />
                        Distribute Content
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <Button
                          variant="outline"
                          onClick={() => handleDistribute(['linkedin'])}
                          className="flex items-center gap-2 bg-indigo-700 text-white border-0 hover:bg-indigo-600 shadow-lg"
                          disabled={isDistributing}
                        >
                          {isDistributing ? <Loader2 className="h-5 w-5 animate-spin" /> : <ExternalLink className="h-5 w-5" />}
                          LinkedIn
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => handleDistribute(['twitter'])}
                          className="flex items-center gap-2 bg-indigo-700 text-white border-0 hover:bg-indigo-600 shadow-lg"
                          disabled={isDistributing}
                        >
                          {isDistributing ? <Loader2 className="h-5 w-5 animate-spin" /> : <ExternalLink className="h-5 w-5" />}
                          Twitter
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => handleDistribute(['facebook'])}
                          className="flex items-center gap-2 bg-indigo-700 text-white border-0 hover:bg-indigo-600 shadow-lg"
                          disabled={isDistributing}
                        >
                          {isDistributing ? <Loader2 className="h-5 w-5 animate-spin" /> : <ExternalLink className="h-5 w-5" />}
                          Facebook
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => handleDistribute(['email'])}
                          className="flex items-center gap-2 bg-indigo-700 text-white border-0 hover:bg-indigo-600 shadow-lg"
                          disabled={isDistributing}
                        >
                          {isDistributing ? <Loader2 className="h-5 w-5 animate-spin" /> : <Mail className="h-5 w-5" />}
                          Email
                        </Button>
                      </div>
                      <Button
                        onClick={() => handleDistribute(['linkedin', 'twitter', 'facebook', 'email'])}
                        className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold text-lg py-4 rounded-xl shadow-xl hover:scale-105 transition-transform duration-200"
                        size="lg"
                        disabled={isDistributing}
                      >
                        {isDistributing ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Distributing to All Platforms...
                          </>
                        ) : (
                          <>
                            <Share2 className="mr-2 h-5 w-5" />
                            Distribute to All Platforms
                          </>
                        )}
                      </Button>
                      {/* Distribution Results Section */}
                      {(distributionResults.length > 0 || distributionError) && (
                        <div className="mt-8 p-6 bg-gradient-to-r from-indigo-900 to-blue-900 rounded-xl shadow-lg animate-fade-in">
                          <h4 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <Share2 className="h-5 w-5" />
                            Distribution Results
                          </h4>
                          {distributionError && (
                            <Alert variant="destructive" className="mb-4">
                              <AlertCircle className="h-5 w-5" />
                              <AlertDescription>{distributionError}</AlertDescription>
                            </Alert>
                          )}
                          <div className="space-y-4">
                            {distributionResults.map((log, idx) => (
                              <Card key={idx} className="bg-gradient-to-r from-blue-800 to-indigo-800 border-0 shadow-md">
                                <CardHeader>
                                  <CardTitle className="flex items-center gap-3 text-white">
                                    <ExternalLink className="h-5 w-5" />
                                    {log.platform.charAt(0).toUpperCase() + log.platform.slice(1)}
                                    <span className="ml-2">
                                      {log.status === 'posted' && <Badge className="bg-green-700 text-white">Posted</Badge>}
                                      {log.status === 'failed' && <Badge className="bg-red-700 text-white">Failed</Badge>}
                                      {log.status === 'posting' && <Badge className="bg-yellow-700 text-white">Posting...</Badge>}
                                    </span>
                                  </CardTitle>
                                </CardHeader>
                                <CardContent>
                                  {log.status === 'posted' && log.post_url && (
                                    <a href={log.post_url} target="_blank" rel="noopener noreferrer" className="text-blue-300 underline flex items-center gap-2">
                                      <ExternalLink className="h-4 w-4" />
                                      {log.post_url}
                                    </a>
                                  )}
                                  {log.status === 'failed' && log.error_message && (
                                    <p className="text-red-300">Error: {log.error_message}</p>
                                  )}
                                  {log.status === 'posting' && (
                                    <p className="text-yellow-300">Posting in progress...</p>
                                  )}
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
              {/* Reset Button */}
              <div className="text-center mt-10">
                <Button
                  variant="outline"
                  onClick={() => {
                    setResults(null)
                    setContent({ title: '', text: '' })
                    setProgress(0)
                    setError(null)
                  }}
                  size="lg"
                  className="bg-gray-800 text-white border-0 hover:bg-gray-700 py-3 px-8 rounded-xl shadow-lg"
                >
                  Process New Content
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App

