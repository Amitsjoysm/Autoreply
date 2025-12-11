import React, { useState, useEffect } from 'react';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { toast } from 'sonner';
import { 
  Zap, Send, CheckCircle2, AlertCircle, Mail, Target, Users, Calendar, 
  MessageSquare, TrendingUp, Clock, X, Check, AlertTriangle, Info
} from 'lucide-react';

const TestEmail = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [simulateReply, setSimulateReply] = useState(false);
  
  const [formData, setFormData] = useState({
    from_email: 'john.doe@techcompany.com',
    subject: 'Interested in pricing for our company',
    body: `Hi there,\n\nI'm interested in learning more about your pricing plans for our company.\n\nWe're a tech startup with about 75 employees, and we're looking for an email automation solution that can help us scale.\n\nOur budget is around $10,000 per month. Could you provide more details about your offerings?\n\nThanks,\nJohn Doe\nCEO, Tech Company Inc.`,
    simulate_reply: false,
    reply_body: `Thanks for the information!\n\nTo answer your questions:\n\n1. Company size: We have 75 employees\n2. Budget: $10,000 per month\n3. Industry: Technology/SaaS\n4. Timeline: Looking to implement within 2-3 months\n\nLooking forward to next steps!`
  });

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const status = await API.getSystemStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const handleTest = async () => {
    setLoading(true);
    setResult(null);
    try {
      const testData = {
        ...formData,
        simulate_reply: simulateReply
      };
      
      const response = await API.testCompleteFlow(testData);
      setResult(response);
      
      if (response.success) {
        toast.success('Test completed successfully!');
      } else {
        toast.error('Test completed with errors');
      }
    } catch (error) {
      toast.error('Test failed: ' + (error.response?.data?.detail || error.message));
      setResult({ 
        success: false, 
        errors: [error.response?.data?.detail || error.message],
        steps: [],
        summary: {}
      });
    } finally {
      setLoading(false);
    }
  };

  const getStepIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-amber-600" />;
      case 'skipped':
        return <X className="w-5 h-5 text-gray-400" />;
      default:
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getStepBadge = (status) => {
    const badges = {
      success: <Badge className="bg-green-500">Success</Badge>,
      error: <Badge className="bg-red-500">Error</Badge>,
      warning: <Badge className="bg-amber-500">Warning</Badge>,
      skipped: <Badge className="bg-gray-400">Skipped</Badge>,
      info: <Badge className="bg-blue-500">Info</Badge>
    };
    return badges[status] || badges.info;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">🧪 Complete Flow Test</h1>
        <p className="text-gray-600 mt-1">
          Test the entire email automation pipeline: Intents → Lead Qualification → Draft Generation → Follow-ups → Calendar Events
        </p>
      </div>

      {/* System Status */}
      {systemStatus && (
        <Card className={systemStatus.ready ? 'border-green-200 bg-green-50' : 'border-amber-200 bg-amber-50'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {systemStatus.ready ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              )}
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <Label className="text-sm text-gray-600">Intents</Label>
                <p className="text-2xl font-bold text-gray-900">{systemStatus.configuration.intents}</p>
              </div>
              <div>
                <Label className="text-sm text-gray-600">Knowledge Base</Label>
                <p className="text-2xl font-bold text-gray-900">{systemStatus.configuration.knowledge_base}</p>
              </div>
              <div>
                <Label className="text-sm text-gray-600">Qualification</Label>
                <p className="text-sm font-medium mt-1">
                  {systemStatus.configuration.global_qualification_enabled ? (
                    <Badge className="bg-green-500">Enabled</Badge>
                  ) : (
                    <Badge className="bg-gray-400">Disabled</Badge>
                  )}
                </p>
              </div>
              <div>
                <Label className="text-sm text-gray-600">Nurturing</Label>
                <p className="text-sm font-medium mt-1">
                  {systemStatus.configuration.global_nurturing_enabled ? (
                    <Badge className="bg-green-500">Enabled</Badge>
                  ) : (
                    <Badge className="bg-gray-400">Disabled</Badge>
                  )}
                </p>
              </div>
            </div>
            {systemStatus.warnings && systemStatus.warnings.length > 0 && (
              <div className="mt-4 p-3 bg-white rounded-lg border border-amber-200">
                <p className="text-sm text-amber-900 font-medium">Warnings:</p>
                {systemStatus.warnings.map((warning, idx) => (
                  <p key={idx} className="text-sm text-amber-700 mt-1">• {warning}</p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Test Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="w-5 h-5 text-purple-600" />
            Test Email Configuration
          </CardTitle>
          <CardDescription>
            Simulate an incoming email to test the complete flow
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="from_email">From Email (Lead/Customer)</Label>
            <Input
              id="from_email"
              value={formData.from_email}
              onChange={(e) => setFormData({...formData, from_email: e.target.value})}
              placeholder="john.doe@company.com"
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
              rows={8}
            />
          </div>

          {/* Simulate Reply Option */}
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <Label htmlFor="simulate_reply" className="text-blue-900 font-medium">Simulate Reply</Label>
                  <p className="text-sm text-blue-700 mt-1">Test reply detection, answer extraction & lead qualification</p>
                </div>
                <Switch
                  id="simulate_reply"
                  checked={simulateReply}
                  onCheckedChange={setSimulateReply}
                />
              </div>

              {simulateReply && (
                <div className="mt-4">
                  <Label htmlFor="reply_body">Reply Body (from Lead)</Label>
                  <Textarea
                    id="reply_body"
                    value={formData.reply_body}
                    onChange={(e) => setFormData({...formData, reply_body: e.target.value})}
                    placeholder="Lead's reply with answers..."
                    rows={6}
                    className="bg-white"
                  />
                </div>
              )}
            </CardContent>
          </Card>

          <Button 
            onClick={handleTest} 
            disabled={loading || !systemStatus?.ready}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            size="lg"
          >
            {loading ? (
              <>
                <Zap className="w-4 h-4 mr-2 animate-pulse" />
                Running Complete Flow Test...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                Run Complete Flow Test
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Test Results */}
      {result && (
        <>
          {/* Summary */}
          <Card className={result.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {result.success ? (
                  <>
                    <CheckCircle2 className="w-6 h-6 text-green-600" />
                    Test Completed Successfully
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-6 h-6 text-red-600" />
                    Test Completed with Issues
                  </>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="bg-white rounded-lg p-3 border">
                  <Target className="w-5 h-5 text-blue-600 mb-1" />
                  <p className="text-sm text-gray-600">Intent Match</p>
                  <p className="text-lg font-bold">{result.summary.intent_matched ? '✓' : '✗'}</p>
                </div>
                <div className="bg-white rounded-lg p-3 border">
                  <Users className="w-5 h-5 text-purple-600 mb-1" />
                  <p className="text-sm text-gray-600">Lead Detected</p>
                  <p className="text-lg font-bold">{result.summary.lead_detected ? '✓' : '✗'}</p>
                </div>
                <div className="bg-white rounded-lg p-3 border">
                  <Calendar className="w-5 h-5 text-green-600 mb-1" />
                  <p className="text-sm text-gray-600">Meeting Detected</p>
                  <p className="text-lg font-bold">{result.summary.meeting_detected ? '✓' : '✗'}</p>
                </div>
                <div className="bg-white rounded-lg p-3 border">
                  <MessageSquare className="w-5 h-5 text-pink-600 mb-1" />
                  <p className="text-sm text-gray-600">Draft Generated</p>
                  <p className="text-lg font-bold">{result.summary.draft_generated ? '✓' : '✗'}</p>
                </div>
                <div className="bg-white rounded-lg p-3 border">
                  <TrendingUp className="w-5 h-5 text-amber-600 mb-1" />
                  <p className="text-sm text-gray-600">Tokens Used</p>
                  <p className="text-lg font-bold">{result.summary.tokens_used || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Flow Steps */}
          <Card>
            <CardHeader>
              <CardTitle>Flow Execution Steps</CardTitle>
              <CardDescription>{result.steps.length} steps executed</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.steps.map((step, idx) => (
                  <div key={idx} className="border rounded-lg p-4 bg-white">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getStepIcon(step.status)}
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            Step {step.step}: {step.name}
                          </h3>
                        </div>
                      </div>
                      {getStepBadge(step.status)}
                    </div>

                    <div className="ml-8 space-y-2">
                      {Object.entries(step.details).map(([key, value]) => (
                        <div key={key} className="text-sm">
                          <span className="text-gray-600 font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: </span>
                          <span className="text-gray-900">
                            {Array.isArray(value) ? (
                              <ul className="mt-1 space-y-1 ml-4">
                                {value.map((item, i) => (
                                  <li key={i} className="list-disc">{typeof item === 'object' ? JSON.stringify(item) : item}</li>
                                ))}
                              </ul>
                            ) : typeof value === 'object' ? (
                              JSON.stringify(value, null, 2)
                            ) : typeof value === 'boolean' ? (
                              value ? '✓ Yes' : '✗ No'
                            ) : (
                              value
                            )}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Warnings & Errors */}
          {(result.warnings?.length > 0 || result.errors?.length > 0) && (
            <Card>
              <CardHeader>
                <CardTitle>Warnings & Errors</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {result.warnings?.map((warning, idx) => (
                  <div key={idx} className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-amber-900">{warning}</p>
                    </div>
                  </div>
                ))}
                {result.errors?.map((error, idx) => (
                  <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-red-900">{error}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Info Card */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-blue-900">What This Tests</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-blue-800">
            <p>✓ <strong>Intent Classification</strong> - Matches email to configured intents</p>
            <p>✓ <strong>Lead Detection</strong> - Identifies potential leads based on intent</p>
            <p>✓ <strong>Lead Qualification</strong> - Generates and asks qualification questions</p>
            <p>✓ <strong>Draft Generation</strong> - Creates response using Persona, KB, Intent prompts</p>
            <p>✓ <strong>Natural Question Integration</strong> - Questions woven naturally into draft</p>
            <p>✓ <strong>Meeting Detection</strong> - Identifies meeting requests</p>
            <p>✓ <strong>Follow-up Timeline</strong> - Shows when follow-ups would be created</p>
            <p>✓ <strong>Reply Simulation</strong> - Tests answer extraction and re-qualification</p>
            <p>✓ <strong>Scoring (0-100)</strong> - Qualifies/disqualifies based on answers</p>
            <p className="text-blue-900 font-medium mt-3">💡 No actual emails are sent. Test data is cleaned up automatically.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TestEmail;
