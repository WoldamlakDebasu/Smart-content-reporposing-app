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
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  // Mock data for demo
  const mockResults = {
    id: 1,
    title: "The Future of Artificial Intelligence in Business",
    status: "completed",
    progress: 1.0,
    analysis_results: {
      main_theme: "AI in Business",
      key_topics: ["artificial intelligence", "business automation", "machine learning", "digital transformation"],
      keywords: ["AI", "automation", "productivity", "innovation", "technology"],
      sentiment: "positive",
      tone: "professional",
      target_audience: "Business leaders and technology professionals",
      key_takeaways: [
        "AI is revolutionizing business operations",
        "Automation reduces costs and improves efficiency", 
        "Strategic AI adoption provides competitive advantages"
      ],
      summary_short: "AI is transforming business through automation and data-driven insights.",
      summary_medium: "Artificial Intelligence is revolutionizing business operations by automating tasks, providing insights, and enhancing customer experiences.",
      summary_long: "Artificial Intelligence technologies are becoming integral to modern business operations, offering advantages in data processing, automation, and customer service while presenting challenges in implementation and ethics."
    },
    repurposed_outputs: {
      social_posts: [
        {
          platform: "linkedin",
          text: "🚀 The future of business is AI-powered! From automating routine tasks to providing deep insights through data analysis, AI technologies are becoming essential for modern operations. Companies leveraging machine learning and NLP are seeing enhanced productivity and improved customer experiences. #AI #BusinessInnovation #DigitalTransformation",
          hashtags: ["AI", "BusinessInnovation", "DigitalTransformation", "MachineLearning"],
          character_count: 287
        },
        {
          platform: "twitter",
          text: "AI is revolutionizing business! 🤖 From automation to predictive analytics, companies are gaining competitive advantages through strategic AI adoption. The future belongs to organizations that balance innovation with responsibility. #AI #Business #Innovation",
          hashtags: ["AI", "Business", "Innovation", "Automation"],
          character_count: 234
        },
        {
          platform: "facebook",
          text: "The business landscape is changing rapidly with AI at the forefront! 🌟 Companies across industries are using machine learning, natural language processing, and computer vision to enhance productivity and customer experiences. While challenges exist around privacy and implementation, the potential for growth is enormous. What's your experience with AI in your business?",
          hashtags: ["AI", "Business", "Technology", "Innovation"],
          character_count: 398
        },
        {
          platform: "instagram",
          text: "AI is transforming how we do business! 💼✨ From chatbots to predictive analytics, the possibilities are endless. Swipe to learn more about the future of AI in business! 📊 #AI #Business #Innovation #TechTrends #FutureOfWork",
          hashtags: ["AI", "Business", "Innovation", "TechTrends", "FutureOfWork"],
          character_count: 198
        }
      ],
      email_snippets: [
        {
          type: "newsletter_teaser",
          subject: "🤖 How AI is Reshaping Business Operations",
          content: "Discover how leading companies are leveraging artificial intelligence to automate processes, enhance customer experiences, and gain competitive advantages. From machine learning algorithms to natural language processing, AI is no longer a futuristic concept—it's today's business reality.",
          cta: "Read the Full Article",
          word_count: 45
        },
        {
          type: "promotional",
          subject: "Transform Your Business with AI - Essential Insights Inside",
          content: "Ready to unlock the power of AI for your business? Our latest analysis reveals how artificial intelligence is revolutionizing operations across industries. Learn about the key advantages, implementation challenges, and strategic approaches that successful companies are using to thrive in the AI-driven future.",
          cta: "Get Your AI Strategy Guide",
          word_count: 52
        }
      ],
      short_article: {
        headline: "How AI is Revolutionizing Modern Business Operations",
        introduction: "The integration of artificial intelligence into business processes is no longer a distant possibility—it's happening now. Companies across industries are discovering that AI technologies offer unprecedented opportunities to enhance efficiency, improve customer experiences, and gain competitive advantages in an increasingly digital marketplace.",
        main_content: "The advantages of AI implementation are compelling. Organizations can process vast amounts of data in real-time, enabling faster decision-making and more accurate predictive analytics. Automation of routine tasks frees up human resources for strategic initiatives, while AI-powered customer service tools provide 24/7 support with personalized experiences. However, successful AI adoption requires careful planning, significant investment in infrastructure, and ongoing attention to ethical considerations including data privacy and algorithmic bias.",
        conclusion: "As we look toward the future, businesses that embrace AI strategically and responsibly will be best positioned to thrive. The key lies in developing comprehensive AI strategies, investing in talent development, and maintaining ethical standards throughout the implementation process.",
        word_count: 387,
        reading_time: "2 min read"
      },
      infographic_data: {
        title: "AI in Business: Key Statistics and Insights",
        statistics: [
          {
            label: "Productivity Increase",
            value: "40%",
            icon_suggestion: "trending-up"
          },
          {
            label: "Cost Reduction",
            value: "25%",
            icon_suggestion: "dollar-sign"
          },
          {
            label: "Customer Satisfaction",
            value: "35%",
            icon_suggestion: "heart"
          },
          {
            label: "Decision Speed",
            value: "60%",
            icon_suggestion: "zap"
          }
        ],
        sections: [
          {
            title: "Key Benefits",
            description: "Automation, insights, and enhanced customer experiences"
          },
          {
            title: "Main Challenges", 
            description: "Privacy concerns, implementation costs, and skill gaps"
          },
          {
            title: "Future Outlook",
            description: "Continued growth in AI adoption across all industries"
          }
        ],
        cta: "Learn More About AI Implementation"
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!content.title.trim() || !content.text.trim()) {
      setError('Please provide both title and content.')
      return
    }

    setIsProcessing(true)
    setError(null)
    setResults(null)
    setProgress(0)

    // Simulate processing with progress updates
    const progressSteps = [10, 30, 60, 80, 100]
    const messages = [
      "Analyzing content structure and themes...",
      "Extracting key insights and keywords...", 
      "Generating repurposed content formats...",
      "Optimizing for different platforms...",
      "Processing completed!"
    ]

    for (let i = 0; i < progressSteps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1500))
      setProgress(progressSteps[i])
    }

    // Set mock results
    setResults({
      ...mockResults,
      title: content.title,
      original_content: content.text
    })
    setIsProcessing(false)
  }

  const handleDistribute = async (platforms) => {
    alert(`Distribution scheduled for: ${platforms.join(', ')}`)
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="h-8 w-8 text-indigo-600" />
            <h1 className="text-4xl font-bold text-gray-900">Smart Content Repurposing Engine</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Transform your long-form content into engaging, platform-optimized formats with AI-powered automation
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          {!results ? (
            /* Upload Form */
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload Your Content
                </CardTitle>
                <CardDescription>
                  Provide your long-form content and let our AI transform it into multiple engaging formats
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Content Title</label>
                    <Input
                      placeholder="Enter a descriptive title for your content..."
                      value={content.title}
                      onChange={(e) => setContent({...content, title: e.target.value})}
                      disabled={isProcessing}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Long-form Content</label>
                    <Textarea
                      placeholder="Paste your blog post, article, whitepaper, or any long-form content here..."
                      value={content.text}
                      onChange={(e) => setContent({...content, text: e.target.value})}
                      rows={12}
                      disabled={isProcessing}
                    />
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full" 
                    disabled={isProcessing}
                    size="lg"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing Content...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Start AI Processing
                      </>
                    )}
                  </Button>
                </form>

                {/* Processing Status */}
                {isProcessing && (
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon('processing')}
                      <span className="font-medium">Processing Status</span>
                    </div>
                    <Progress value={progress} className="mb-2" />
                    <p className="text-sm text-gray-600">
                      {progress < 30 && "Analyzing content structure and themes..."}
                      {progress >= 30 && progress < 60 && "Extracting key insights and keywords..."}
                      {progress >= 60 && progress < 100 && "Generating repurposed content formats..."}
                      {progress >= 100 && "Processing completed!"}
                    </p>
                  </div>
                )}

                {error && (
                  <Alert className="mt-4" variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          ) : (
            /* Results Display */
            <div className="space-y-6">
              {/* Header with original content info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    Processing Complete
                  </CardTitle>
                  <CardDescription>
                    Your content "{results.title}" has been successfully analyzed and repurposed
                  </CardDescription>
                </CardHeader>
              </Card>

              {/* Analysis Results */}
              {results.analysis_results && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      Content Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div>
                        <h4 className="font-medium mb-2">Main Theme</h4>
                        <Badge variant="secondary">{results.analysis_results.main_theme}</Badge>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2">Tone</h4>
                        <Badge variant="outline">{results.analysis_results.tone}</Badge>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2">Sentiment</h4>
                        <Badge variant={results.analysis_results.sentiment === 'positive' ? 'default' : 'secondary'}>
                          {results.analysis_results.sentiment}
                        </Badge>
                      </div>
                    </div>

                    <Separator className="my-4" />

                    <div className="space-y-3">
                      <div>
                        <h4 className="font-medium mb-2">Key Topics</h4>
                        <div className="flex flex-wrap gap-2">
                          {results.analysis_results.key_topics?.map((topic, index) => (
                            <Badge key={index} variant="outline">{topic}</Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Keywords</h4>
                        <div className="flex flex-wrap gap-2">
                          {results.analysis_results.keywords?.map((keyword, index) => (
                            <Badge key={index} variant="secondary">{keyword}</Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Repurposed Content */}
              {results.repurposed_outputs && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Share2 className="h-5 w-5" />
                      Repurposed Content
                    </CardTitle>
                    <CardDescription>
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
                          <Card key={index}>
                            <CardHeader>
                              <CardTitle className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <MessageSquare className="h-4 w-4" />
                                  {post.platform.charAt(0).toUpperCase() + post.platform.slice(1)}
                                </div>
                                <div className="flex gap-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => copyToClipboard(post.text)}
                                  >
                                    <Copy className="h-3 w-3" />
                                  </Button>
                                </div>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="mb-3">{post.text}</p>
                              <div className="flex flex-wrap gap-1 mb-2">
                                {post.hashtags?.map((tag, tagIndex) => (
                                  <Badge key={tagIndex} variant="secondary" className="text-xs">
                                    #{tag}
                                  </Badge>
                                ))}
                              </div>
                              <p className="text-xs text-gray-500">
                                {post.character_count} characters
                              </p>
                            </CardContent>
                          </Card>
                        ))}
                      </TabsContent>

                      {/* Email Snippets */}
                      <TabsContent value="email" className="space-y-4">
                        {results.repurposed_outputs.email_snippets?.map((email, index) => (
                          <Card key={index}>
                            <CardHeader>
                              <CardTitle className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <Mail className="h-4 w-4" />
                                  {email.type.replace('_', ' ').toUpperCase()}
                                </div>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => copyToClipboard(`Subject: ${email.subject}\n\n${email.content}\n\n${email.cta}`)}
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3">
                                <div>
                                  <h5 className="font-medium text-sm">Subject Line</h5>
                                  <p className="text-sm bg-gray-50 p-2 rounded">{email.subject}</p>
                                </div>
                                <div>
                                  <h5 className="font-medium text-sm">Content</h5>
                                  <p className="text-sm">{email.content}</p>
                                </div>
                                <div>
                                  <h5 className="font-medium text-sm">Call to Action</h5>
                                  <Badge variant="default">{email.cta}</Badge>
                                </div>
                                <p className="text-xs text-gray-500">
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
                          <Card>
                            <CardHeader>
                              <CardTitle className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <FileText className="h-4 w-4" />
                                  Short Article
                                </div>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => copyToClipboard(`${results.repurposed_outputs.short_article.headline}\n\n${results.repurposed_outputs.short_article.introduction}\n\n${results.repurposed_outputs.short_article.main_content}\n\n${results.repurposed_outputs.short_article.conclusion}`)}
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-4">
                                <div>
                                  <h3 className="text-xl font-bold mb-2">
                                    {results.repurposed_outputs.short_article.headline}
                                  </h3>
                                  <Badge variant="outline">
                                    {results.repurposed_outputs.short_article.reading_time}
                                  </Badge>
                                </div>
                                
                                <div className="prose max-w-none">
                                  <p>{results.repurposed_outputs.short_article.introduction}</p>
                                  <p>{results.repurposed_outputs.short_article.main_content}</p>
                                  <p>{results.repurposed_outputs.short_article.conclusion}</p>
                                </div>
                                
                                <p className="text-xs text-gray-500">
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
                          <Card>
                            <CardHeader>
                              <CardTitle className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <BarChart3 className="h-4 w-4" />
                                  Infographic Data
                                </div>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => copyToClipboard(JSON.stringify(results.repurposed_outputs.infographic_data, null, 2))}
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-4">
                                <h3 className="text-lg font-bold">
                                  {results.repurposed_outputs.infographic_data.title}
                                </h3>
                                
                                <div>
                                  <h4 className="font-medium mb-2">Key Statistics</h4>
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {results.repurposed_outputs.infographic_data.statistics?.map((stat, index) => (
                                      <div key={index} className="bg-gray-50 p-3 rounded">
                                        <div className="text-2xl font-bold text-indigo-600">{stat.value}</div>
                                        <div className="text-sm">{stat.label}</div>
                                        <div className="text-xs text-gray-500">Icon: {stat.icon_suggestion}</div>
                                      </div>
                                    ))}
                                  </div>
                                </div>

                                <div>
                                  <h4 className="font-medium mb-2">Sections</h4>
                                  <div className="space-y-2">
                                    {results.repurposed_outputs.infographic_data.sections?.map((section, index) => (
                                      <div key={index} className="border-l-4 border-indigo-500 pl-3">
                                        <h5 className="font-medium">{section.title}</h5>
                                        <p className="text-sm text-gray-600">{section.description}</p>
                                      </div>
                                    ))}
                                  </div>
                                </div>

                                <div>
                                  <h4 className="font-medium mb-2">Call to Action</h4>
                                  <Badge variant="default">{results.repurposed_outputs.infographic_data.cta}</Badge>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )}
                      </TabsContent>
                    </Tabs>

                    {/* Distribution Section */}
                    <Separator className="my-6" />
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Share2 className="h-5 w-5" />
                        Distribute Content
                      </h3>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <Button
                          variant="outline"
                          onClick={() => handleDistribute(['linkedin'])}
                          className="flex items-center gap-2"
                        >
                          <ExternalLink className="h-4 w-4" />
                          LinkedIn
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => handleDistribute(['twitter'])}
                          className="flex items-center gap-2"
                        >
                          <ExternalLink className="h-4 w-4" />
                          Twitter
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => handleDistribute(['facebook'])}
                          className="flex items-center gap-2"
                        >
                          <ExternalLink className="h-4 w-4" />
                          Facebook
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => handleDistribute(['email'])}
                          className="flex items-center gap-2"
                        >
                          <Mail className="h-4 w-4" />
                          Email
                        </Button>
                      </div>
                      
                      <Button
                        onClick={() => handleDistribute(['linkedin', 'twitter', 'facebook', 'email'])}
                        className="w-full"
                        size="lg"
                      >
                        <Share2 className="mr-2 h-4 w-4" />
                        Distribute to All Platforms
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Reset Button */}
              <div className="text-center">
                <Button
                  variant="outline"
                  onClick={() => {
                    setResults(null)
                    setContent({ title: '', text: '' })
                    setProgress(0)
                    setError(null)
                  }}
                  size="lg"
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

