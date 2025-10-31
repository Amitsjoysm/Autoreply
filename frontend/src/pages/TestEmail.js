import React, { useState } from 'react';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { Zap, Send, CheckCircle2, AlertCircle } from 'lucide-react';

const TestEmail = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    from_email: 'test@example.com',
    subject: 'Test Email - Meeting Request',
    body: `Hi,\n\nI'd like to schedule a meeting with you to discuss the new project.\n\nAre you available next Monday at 2 PM?\n\nBest regards,\nJohn Doe`
  });

  const handleTest = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await API.testEmailProcessing();
      setResult(response);
      toast.success('Test completed successfully');
    } catch (error) {
      toast.error('Test failed');
      setResult({ error: error.response?.data?.detail || 'Test failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Test Email Processing</h1>
        <p className="text-gray-600 mt-1">Test the AI email processing pipeline end-to-end</p>
      </div>

      {/* Test Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-purple-600" />
            Test Configuration
          </CardTitle>
          <CardDescription>
            Simulate an incoming email to test intent classification, draft generation, and validation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="from_email">From Email</Label>
            <Input
              id="from_email"
              value={formData.from_email}
              onChange={(e) => setFormData({...formData, from_email: e.target.value})}
              placeholder="sender@example.com"
            />
          </div>

          <div>
            <Label htmlFor="subject">Subject</Label>
            <Input
              id="subject"
              value={formData.subject}
              onChange={(e) => setFormData({...formData, subject: e.target.value})}
              placeholder="Email subject"
            />
          </div>

          <div>
            <Label htmlFor="body">Email Body</Label>
            <Textarea
              id="body"
              value={formData.body}
              onChange={(e) => setFormData({...formData, body: e.target.value})}
              placeholder="Email content..."
              rows={10}
            />
          </div>

          <Button 
            onClick={handleTest} 
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            {loading ? (
              <>
                <Zap className="w-4 h-4 mr-2 animate-pulse" />
                Processing...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                Run Test
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Test Results */}
      {result && (
        <Card className={result.error ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {result.error ? (
                <>
                  <AlertCircle className="w-5 h-5 text-red-600" />
                  Test Failed
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  Test Results
                </>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {result.error ? (
              <div className="bg-white border border-red-200 rounded-lg p-4">
                <p className="text-red-900 font-medium">Error:</p>
                <p className="text-red-700 mt-2">{result.error}</p>
              </div>
            ) : (
              <>
                {/* Intent Classification */}
                {result.intent_classified !== undefined && (
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">Intent Classification</h3>
                      <Badge className={result.intent_classified ? 'bg-green-500' : 'bg-gray-500'}>
                        {result.intent_classified ? 'Matched' : 'No Match'}
                      </Badge>
                    </div>
                    {result.intent_name && (
                      <div>
                        <Label className="text-sm text-gray-600">Detected Intent:</Label>
                        <p className="text-gray-900 font-medium mt-1">{result.intent_name}</p>
                      </div>
                    )}
                    {result.intent_confidence !== undefined && (
                      <div className="mt-2">
                        <Label className="text-sm text-gray-600">Confidence:</Label>
                        <p className="text-gray-900 font-medium">{(result.intent_confidence * 100).toFixed(1)}%</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Draft Generation */}
                {result.draft && (
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">Generated Draft</h3>
                      <Badge className="bg-blue-500">
                        <Send className="w-3 h-3 mr-1" />
                        Ready
                      </Badge>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-gray-900 whitespace-pre-wrap">{result.draft}</p>
                    </div>
                  </div>
                )}

                {/* Validation */}
                {result.validation_passed !== undefined && (
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">Validation</h3>
                      <Badge className={result.validation_passed ? 'bg-green-500' : 'bg-amber-500'}>
                        {result.validation_passed ? 'Passed' : 'Issues Found'}
                      </Badge>
                    </div>
                    {result.validation_issues && result.validation_issues.length > 0 && (
                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                        <p className="text-sm font-medium text-amber-900 mb-2">Issues:</p>
                        <ul className="text-sm text-amber-800 list-disc list-inside space-y-1">
                          {result.validation_issues.map((issue, idx) => (
                            <li key={idx}>{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Token Usage */}
                {result.total_tokens_used && (
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 mb-2">Token Usage</h3>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{result.total_tokens_used} tokens</Badge>
                      <span className="text-sm text-gray-600">used in this test</span>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Info Card */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-blue-900">About Testing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-blue-800">
            <p>• This test simulates the complete email processing pipeline</p>
            <p>• Tests intent classification, draft generation, and validation agents</p>
            <p>• No actual emails are sent during testing</p>
            <p>• Token usage is counted against your daily quota</p>
            <p>• Use this to verify your intents and knowledge base configuration</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TestEmail;