import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/layout/PageHeader';
import { CreationForm } from './components/CreationForm';
import { AIStudio3D } from './components/3d/AIStudio3D';
import { DraftResult } from './components/DraftResult';
import { contentGenerationService, ContentRequest, GenerationResult } from '../../services/api/contentGenerationService';
import { apiClient } from '../../services/api';

type CreationStage = 'FORM' | 'GENERATING' | 'RESULT';

export function ContentCreation() {
  const { workspaceId, projectId } = useParams<{ workspaceId: string, projectId: string }>();
  const navigate = useNavigate();
  
  const [stage, setStage] = useState<CreationStage>('FORM');
  const [result, setResult] = useState<GenerationResult | null>(null);
  
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!workspaceId || !projectId) {
    return (
      <div className="flex justify-center p-8 text-danger">
        Invalid route parameters. Project and Workspace IDs are required.
      </div>
    );
  }

  const handleGenerate = async (request: ContentRequest) => {
    setError(null);
    setStage('GENERATING');
    
    try {
      const generatedData = await contentGenerationService.generateContent(request);
      setResult(generatedData);
      setStage('RESULT');
    } catch (err: any) {
      setError(err.message || 'Generation failed.');
      setStage('FORM');
    }
  };

  const handleSaveDraft = async (editedData: Partial<GenerationResult>) => {
    if (!result) return;
    setIsSaving(true);
    setError(null);
    try {
      // POST to /projects/{project_id}/posts
      const payload = {
        title: editedData.title || result.title,
        content: editedData.content || result.content,
        content_type: result.contentType.toUpperCase().replace(' ', '_'),
        platform: result.platform.toUpperCase(),
        status: 'DRAFT'
      };
      
      const response = await apiClient.post(`/projects/${projectId}/posts`, payload);
      
      if (response.data.success) {
        alert('Draft saved successfully!');
        navigate('/posts');
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || err.message || 'Failed to save draft.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSubmitReview = async (editedData: Partial<GenerationResult>) => {
    if (!result) return;
    setIsSubmitting(true);
    setError(null);
    try {
      // 1. Save it first as a draft
      const createPayload = {
        title: editedData.title || result.title,
        content: editedData.content || result.content,
        content_type: result.contentType.toUpperCase().replace(' ', '_'),
        platform: result.platform.toUpperCase(),
        status: 'DRAFT'
      };
      
      const createRes = await apiClient.post(`/projects/${projectId}/posts`, createPayload);
      
      if (!createRes.data.success) throw new Error('Failed to create post');
      
      const newPostId = createRes.data.data.id;

      // 2. Submit for review
      await apiClient.post(`/projects/${projectId}/posts/${newPostId}/submit-review`);
      
      alert('Post submitted for review successfully!');
      navigate('/posts');
    } catch (err: any) {
      setError(err.response?.data?.error?.message || err.message || 'Failed to submit for review.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-col gap-6 w-full max-w-5xl mx-auto">
      <PageHeader 
        title="AI Content Creation" 
        subtitle="Generate intelligent, brand-aligned posts across all platforms."
      />

      {error && (
        <div className="bg-danger/10 text-danger border border-danger/20 p-4 rounded-md mb-6">
          {error}
        </div>
      )}

      {stage === 'FORM' && (
        <CreationForm 
          workspaceId={workspaceId}
          projectId={projectId} 
          onSubmit={handleGenerate} 
          isLoading={false} 
        />
      )}

      {stage === 'GENERATING' && (
        <AIStudio3D />
      )}

      {stage === 'RESULT' && result && (
        <DraftResult 
          result={result}
          onSaveDraft={handleSaveDraft}
          onSubmitReview={handleSubmitReview}
          isSaving={isSaving}
          isSubmitting={isSubmitting}
        />
      )}
    </div>
  );
}
