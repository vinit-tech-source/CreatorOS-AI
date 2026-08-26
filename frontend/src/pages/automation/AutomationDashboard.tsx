import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Zap, Plus, Trash2, Settings, AlertCircle, Play, Pause } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { useAutomationStore } from '../../stores/automationStore';
import { Link } from 'react-router-dom';

export function AutomationDashboard() {
  const { activeWorkspace } = useWorkspaceStore();
  const { rules, fetchRules, createRule, deleteRule, isLoading, error } = useAutomationStore();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newRuleName, setNewRuleName] = useState('');
  const [newRuleTrigger, setNewRuleTrigger] = useState('RSS_FEED_UPDATE');
  const [newRuleAction, setNewRuleAction] = useState('GENERATE_DRAFT');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (activeWorkspace) {
      fetchRules(activeWorkspace.id);
    }
  }, [activeWorkspace]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !newRuleName) return;
    
    setIsSubmitting(true);
    try {
      await createRule(activeWorkspace.id, {
        name: newRuleName,
        trigger_type: newRuleTrigger,
        action_type: newRuleAction,
        is_active: true
      });
      setIsModalOpen(false);
      setNewRuleName('');
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!activeWorkspace) return;
    if (window.confirm('Are you sure you want to delete this automation rule?')) {
      await deleteRule(activeWorkspace.id, id);
    }
  };

  if (!activeWorkspace) {
    return (
      <div className="flex-col gap-6 w-full h-full">
        <PageHeader title="Automations" subtitle="Set up IF-THEN rules for your workspace." />
        <Card glass>
          <CardContent>
            <div className="flex flex-col items-center justify-center p-12 text-secondary">
              <AlertCircle size={40} className="mb-4" />
              <p className="font-medium text-lg text-primary">No Workspace Selected</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex-col gap-6 w-full h-full">
      <PageHeader 
        title="Automations" 
        subtitle="Create custom workflows to automatically generate and publish content."
        action={
          <div className="flex gap-2">
            <Link to="/automation/pipeline">
              <Button variant="secondary">
                <Play size={16} className="mr-2" /> View 3D Pipeline
              </Button>
            </Link>
            <Button onClick={() => setIsModalOpen(true)}>
              <Plus size={16} /> Create Rule
            </Button>
          </div>
        }
      />
      
      {error && (
        <div className="mb-4 p-4 bg-red-500/10 border border-red-500/50 text-red-500 rounded-lg">
          {error}
        </div>
      )}

      {isLoading && rules.length === 0 ? (
        <div className="flex justify-center p-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand"></div></div>
      ) : rules.length === 0 ? (
        <Card glass>
          <CardContent>
            <div className="flex flex-col items-center justify-center p-12 text-secondary">
              <Zap size={48} className="opacity-20 mb-4" />
              <p className="mb-4 text-center text-lg font-medium text-primary">No Automation Rules</p>
              <p className="mb-6 text-center max-w-md">You haven't set up any automation rules yet. Automate your workflow by creating triggers like RSS feed updates to auto-draft posts.</p>
              <Button onClick={() => setIsModalOpen(true)}>Create First Rule</Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {rules.map(rule => (
            <Card key={rule.id} glass className="flex flex-col overflow-hidden">
              <div className={`h-1 w-full ${rule.is_active ? 'bg-brand' : 'bg-secondary'}`} />
              <CardContent className="p-6 flex-1 flex flex-col">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-primary">{rule.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${rule.is_active ? 'bg-success/20 text-success' : 'bg-surface text-secondary'}`}>
                        {rule.is_active ? <Play size={10} /> : <Pause size={10} />}
                        {rule.is_active ? 'Active' : 'Paused'}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" className="text-secondary hover:text-primary">
                      <Settings size={16} />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(rule.id)} className="text-danger hover:bg-danger/10">
                      <Trash2 size={16} />
                    </Button>
                  </div>
                </div>
                
                <div className="bg-surface rounded-lg p-4 border border-border flex flex-col gap-4">
                  <div className="flex flex-col">
                    <span className="text-xs uppercase tracking-wider text-secondary font-semibold mb-1">IF</span>
                    <div className="flex items-center gap-2 text-primary bg-background p-2 rounded border border-border/50 font-medium">
                      <Zap size={16} className="text-brand" />
                      {rule.trigger_type.replace(/_/g, ' ')}
                    </div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs uppercase tracking-wider text-secondary font-semibold mb-1">THEN</span>
                    <div className="flex items-center gap-2 text-primary bg-background p-2 rounded border border-border/50 font-medium">
                      <Play size={16} className="text-brand" />
                      {rule.action_type.replace(/_/g, ' ')}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card glass className="w-full max-w-xl">
            <CardContent className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-primary">Create Automation Rule</h2>
                <button onClick={() => setIsModalOpen(false)} className="text-secondary hover:text-primary">&times;</button>
              </div>
              
              <form onSubmit={handleCreate} className="flex flex-col gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-primary">Rule Name</label>
                  <input 
                    type="text" 
                    value={newRuleName}
                    onChange={(e) => setNewRuleName(e.target.value)}
                    className="p-2 bg-surface border border-border rounded-md text-primary"
                    placeholder="e.g., Auto-draft from Blog RSS"
                    required
                  />
                </div>
                
                <div className="p-4 rounded-lg bg-surface border border-border flex flex-col gap-4">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-semibold text-brand">TRIGGER (IF)</label>
                    <select 
                      value={newRuleTrigger}
                      onChange={(e) => setNewRuleTrigger(e.target.value)}
                      className="p-3 bg-background border border-border/50 rounded-md text-primary"
                    >
                      <option value="RSS_FEED_UPDATE">RSS Feed Update</option>
                      <option value="NEW_YOUTUBE_VIDEO">New YouTube Video</option>
                      <option value="BRAND_MENTION">Brand Mention Detected</option>
                    </select>
                  </div>
                  
                  <div className="flex flex-col gap-2 mt-2">
                    <label className="text-sm font-semibold text-brand">ACTION (THEN)</label>
                    <select 
                      value={newRuleAction}
                      onChange={(e) => setNewRuleAction(e.target.value)}
                      className="p-3 bg-background border border-border/50 rounded-md text-primary"
                    >
                      <option value="GENERATE_DRAFT">Generate Draft Post</option>
                      <option value="AUTO_PUBLISH">Auto-Publish Post</option>
                      <option value="SEND_NOTIFICATION">Send Notification</option>
                    </select>
                  </div>
                </div>
                
                <div className="flex justify-end gap-3 mt-2">
                  <Button variant="outline" onClick={() => setIsModalOpen(false)} type="button">Cancel</Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Saving...' : 'Create Rule'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
