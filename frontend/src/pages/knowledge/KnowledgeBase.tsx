import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Database, UploadCloud, Trash2, FileText, Link as LinkIcon, AlertCircle } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { useKnowledgeStore } from '../../stores/knowledgeStore';

export function KnowledgeBase() {
  const { activeWorkspace } = useWorkspaceStore();
  const { sources, fetchSources, createSource, deleteSource, isLoading, error } = useKnowledgeStore();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newSourceName, setNewSourceName] = useState('');
  const [newSourceType, setNewSourceType] = useState<'TEXT' | 'URL'>('TEXT');
  const [newSourceContent, setNewSourceContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (activeWorkspace) {
      fetchSources(activeWorkspace.id);
    }
  }, [activeWorkspace]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !newSourceName || !newSourceContent) return;
    
    setIsSubmitting(true);
    try {
      await createSource(activeWorkspace.id, {
        name: newSourceName,
        source_type: newSourceType,
        content: newSourceContent
      });
      setIsModalOpen(false);
      setNewSourceName('');
      setNewSourceContent('');
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!activeWorkspace) return;
    if (window.confirm('Are you sure you want to delete this knowledge source?')) {
      await deleteSource(activeWorkspace.id, id);
    }
  };

  if (!activeWorkspace) {
    return (
      <div className="flex-col gap-6 w-full h-full">
        <PageHeader title="Workspace Knowledge" subtitle="Manage AI context." />
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
        title="Workspace Knowledge" 
        subtitle="Manage the documents and context the AI uses to understand your brand."
        action={
          <Button onClick={() => setIsModalOpen(true)}>
            <UploadCloud size={16} /> Add Source
          </Button>
        }
      />
      
      {error && (
        <div className="mb-4 p-4 bg-red-500/10 border border-red-500/50 text-red-500 rounded-lg">
          {error}
        </div>
      )}

      {isLoading && sources.length === 0 ? (
        <div className="flex justify-center p-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand"></div></div>
      ) : sources.length === 0 ? (
        <Card glass>
          <CardContent>
            <div className="flex flex-col items-center justify-center p-12 text-secondary">
              <Database size={48} className="opacity-20 mb-4" />
              <p className="mb-4 text-center text-lg font-medium text-primary">No Knowledge Sources</p>
              <p className="mb-6 text-center max-w-md">Upload text or URLs to train your AI on your specific business context, tone, and product details.</p>
              <Button onClick={() => setIsModalOpen(true)}>Add First Source</Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sources.map(source => (
            <Card key={source.id} glass className="flex flex-col">
              <CardContent className="p-6 flex-1 flex flex-col">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-surface rounded-md text-brand">
                      {source.source_type === 'TEXT' ? <FileText size={20} /> : <LinkIcon size={20} />}
                    </div>
                    <div>
                      <h3 className="font-medium text-primary">{source.name}</h3>
                      <span className="text-xs text-secondary">{new Date(source.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(source.id)} className="text-danger hover:bg-danger/10">
                    <Trash2 size={16} />
                  </Button>
                </div>
                
                <div className="mt-auto pt-4 border-t border-border flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    source.status === 'PROCESSED' ? 'bg-success/20 text-success' : 
                    source.status === 'PENDING' ? 'bg-warning/20 text-warning' : 
                    'bg-danger/20 text-danger'
                  }`}>
                    {source.status}
                  </span>
                  <span className="text-xs text-secondary">{source.source_type}</span>
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
                <h2 className="text-xl font-semibold text-primary">Add Knowledge Source</h2>
                <button onClick={() => setIsModalOpen(false)} className="text-secondary hover:text-primary">&times;</button>
              </div>
              
              <form onSubmit={handleCreate} className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-primary">Source Name</label>
                  <input 
                    type="text" 
                    value={newSourceName}
                    onChange={(e) => setNewSourceName(e.target.value)}
                    className="p-2 bg-surface border border-border rounded-md text-primary"
                    placeholder="e.g., Product FAQs"
                    required
                  />
                </div>
                
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-primary">Source Type</label>
                  <select 
                    value={newSourceType}
                    onChange={(e) => setNewSourceType(e.target.value as 'TEXT' | 'URL')}
                    className="p-2 bg-surface border border-border rounded-md text-primary"
                  >
                    <option value="TEXT">Raw Text</option>
                    <option value="URL">Website URL (Text content)</option>
                  </select>
                </div>
                
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-primary">Content</label>
                  <textarea 
                    value={newSourceContent}
                    onChange={(e) => setNewSourceContent(e.target.value)}
                    className="p-2 bg-surface border border-border rounded-md text-primary min-h-[150px] resize-y"
                    placeholder={newSourceType === 'TEXT' ? "Paste your text content here..." : "https://example.com/about"}
                    required
                  />
                </div>
                
                <div className="flex justify-end gap-3 mt-4">
                  <Button variant="outline" onClick={() => setIsModalOpen(false)} type="button">Cancel</Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Processing...' : 'Add Source'}
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
