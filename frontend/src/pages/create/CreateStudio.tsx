import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Sparkles, Loader2, CheckCircle2, AlertCircle, Save, Send } from 'lucide-react';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { contentGenerationService, ContentRequest, GenerationResult } from '../../services/api/contentGenerationService';
import { projectService } from '../../services/api/projectService';
import { postManagementService } from '../../services/api/postManagementService';
import styles from './CreateStudio.module.css';

export function CreateStudio() {
  const [searchParams] = useSearchParams();
  const { activeWorkspace } = useWorkspaceStore();
  
  // Form State
  const [prompt, setPrompt] = useState(searchParams.get('q') || '');
  const [platform, setPlatform] = useState('X / Twitter');
  const [contentType, setContentType] = useState('Thread');
  const [tone, setTone] = useState('Professional');
  
  // Generation State
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState(0);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Saving State
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Step simulation for UI
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isGenerating && generationStep < 3) {
      interval = setInterval(() => {
        setGenerationStep(prev => prev + 1);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isGenerating, generationStep]);

  const handleGenerate = async () => {
    if (!activeWorkspace || !prompt.trim()) return;

    setIsGenerating(true);
    setGenerationStep(0);
    setError(null);
    setResult(null);
    setSaveSuccess(false);

    try {
      // 1. Get or create a default project to attach this content to
      const projects = await projectService.getProjects(activeWorkspace.id);
      let projectId = projects.length > 0 ? projects[0].id : null;
      
      if (!projectId) {
        const newProject = await projectService.createProject(activeWorkspace.id, {
          name: "Default Project",
          slug: "default-project",
          description: "System generated project for content."
        });
        projectId = newProject.id;
      }

      // 2. Generate Content
      const request: ContentRequest = {
        workspaceId: activeWorkspace.id,
        projectId: projectId,
        platform: platform,
        contentType: contentType,
        userRequest: prompt,
        tone: tone,
        language: 'English'
      };

      const data = await contentGenerationService.generateContent(request);
      setResult(data);
      setGenerationStep(4); // Done
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to generate content');
      setGenerationStep(0);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async (submitForReview = false) => {
    if (!activeWorkspace || !result) return;
    setIsSaving(true);
    
    try {
      const projects = await projectService.getProjects(activeWorkspace.id);
      if (projects.length === 0) throw new Error("No project found to save to.");
      
      await postManagementService.createPost(projects[0].id, {
        title: result.title,
        content: result.content,
        platform: result.platform,
        status: submitForReview ? 'PENDING_REVIEW' : 'DRAFT'
      });
      
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save post');
    } finally {
      setIsSaving(false);
    }
  };

  const steps = ["Understanding Intent", "Researching Topic", "Drafting Content", "Analyzing SEO & Brand"];


  if (!activeWorkspace) {
    return (
      <div className={styles.container}>
        <PageHeader 
          title="AI Creation Studio" 
          subtitle="Design, draft, and refine your next social post."
        />
        <Card glass className="flex-1 flex flex-col items-center justify-center p-12 text-center min-h-[500px]">
          <AlertCircle size={64} className="mb-6 opacity-50 text-warning" />
          <h3 className="text-2xl font-semibold text-primary mb-3">Workspace Required</h3>
          <p className="text-secondary max-w-md mb-8">
            You need an active workspace to generate and save content. Please create or select a workspace to continue.
          </p>
          <Link to="/workspaces">
            <Button variant="primary" size="lg">Go to Workspaces</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <PageHeader 
        title="AI Creation Studio" 
        subtitle="Design, draft, and refine your next social post."
      />
      
      <div className={styles.studioGrid}>
        {/* Left Panel: Inputs */}
        <div className={styles.leftPanel}>
          <Card glass className="flex-1 flex flex-col">
            <div className={styles.cardContent}>
              <div>
                <label className={styles.label}>What do you want to create?</label>
                <textarea
                  className={styles.textarea}
                  placeholder="e.g. A thread about the future of AI agents for beginners..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
              </div>

              <div className={styles.inputGrid}>
                <div>
                  <label className={styles.label}>Platform</label>
                  <select 
                    className={styles.select}
                    value={platform}
                    onChange={(e) => setPlatform(e.target.value)}
                  >
                    <option>X / Twitter</option>
                    <option>LinkedIn</option>
                    <option>Instagram</option>
                    <option>Bluesky</option>
                  </select>
                </div>
                <div>
                  <label className={styles.label}>Format</label>
                  <select 
                    className={styles.select}
                    value={contentType}
                    onChange={(e) => setContentType(e.target.value)}
                  >
                    <option>Post</option>
                    <option>Thread</option>
                    <option>Carousel</option>
                    <option>Article</option>
                  </select>
                </div>
              </div>

              <div>
                <label className={styles.label}>Tone</label>
                <select 
                  className={styles.select}
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                >
                  <option>Professional</option>
                  <option>Conversational</option>
                  <option>Witty</option>
                  <option>Inspirational</option>
                  <option>Educational</option>
                </select>
              </div>

              <div className={styles.generateBtnContainer}>
                <Button 
                  variant="primary" 
                  fullWidth 
                  size="lg"
                  onClick={handleGenerate}
                  disabled={isGenerating || !prompt.trim()}
                >
                  {isGenerating ? <Loader2 className="animate-spin mr-2" /> : <Sparkles className="mr-2" size={18} />}
                  {isGenerating ? 'Generating...' : 'Generate Content'}
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Panel: Preview & Insights */}
        <div className={styles.rightPanel}>
          <Card glass className={styles.rightPanelCard}>
            {error ? (
              <div className={styles.loadingOverlay}>
                <div className="flex flex-col items-center p-8 bg-danger/10 border border-danger/20 rounded-xl max-w-md text-center">
                  <AlertCircle size={48} className="text-danger mb-4" />
                  <h3 className="text-xl font-semibold text-danger mb-2">Generation Failed</h3>
                  <p className="text-secondary">{error}</p>
                  <Button variant="outline" className="mt-6" onClick={() => setError(null)}>Dismiss</Button>
                </div>
              </div>
            ) : isGenerating ? (
              <div className={styles.loadingOverlay}>
                <div className={styles.loadingBox}>
                  <div className="relative">
                    <Loader2 size={48} className="animate-spin text-primary relative z-10" />
                  </div>
                  <div className={styles.stepList}>
                    {steps.map((step, idx) => (
                      <div key={idx} className={`${styles.stepItem} ${idx > generationStep ? 'opacity-30' : 'opacity-100'}`}>
                        {idx < generationStep ? (
                          <CheckCircle2 size={20} className="text-success" />
                        ) : idx === generationStep ? (
                          <Loader2 size={20} className="animate-spin text-primary" />
                        ) : (
                          <div className={styles.stepIconEmpty} />
                        )}
                        <span className={idx === generationStep ? 'text-primary font-medium' : 'text-secondary font-medium'}>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : !result ? (
              <div className={styles.emptyState}>
                <Sparkles size={64} className={styles.emptyIcon} />
                <h3 className="text-2xl font-semibold text-primary/50 mb-2">Ready to Create</h3>
                <p>Your AI-generated content and insights will appear here once you run the generator.</p>
              </div>
            ) : (
              <div className={styles.resultContainer}>
                {/* Content Editor */}
                <div className={styles.editorArea}>
                  <div className={styles.editorHeader}>
                    <h3 className="text-lg font-semibold text-primary m-0">Generated Draft</h3>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleSave(false)} disabled={isSaving}>
                        <Save size={14} className="mr-2" /> Save Draft
                      </Button>
                      <Button variant="primary" size="sm" onClick={() => handleSave(true)} disabled={isSaving}>
                        <Send size={14} className="mr-2" /> Submit Review
                      </Button>
                    </div>
                  </div>
                  
                  {saveSuccess && (
                    <div className="mb-4 p-3 bg-success/10 border border-success/20 text-success rounded-lg text-sm flex items-center">
                      <CheckCircle2 size={16} className="mr-2" /> Successfully saved to library.
                    </div>
                  )}

                  <textarea 
                    className={styles.editorTextarea}
                    value={result.content}
                    onChange={(e) => setResult({...result, content: e.target.value})}
                  />
                </div>
                
                {/* Insights Panel */}
                <div className={styles.insightsSidebar}>
                  <div>
                    <h4 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-3">AI Insights</h4>
                    
                    <div className="flex flex-col gap-4">
                      {/* Brand Score */}
                      <div className={styles.insightCard}>
                        <div className="flex justify-between items-center mb-2">
                          <span className={styles.insightTitle} style={{marginBottom: 0}}>Brand Voice</span>
                          <span className={`text-sm font-bold ${result.brandVoice.score > 80 ? 'text-success' : 'text-warning'}`}>
                            {result.brandVoice.score}/100
                          </span>
                        </div>
                        <div className={styles.progressBarBg}>
                          <div className={styles.progressBarFill} style={{ width: `${result.brandVoice.score}%` }} />
                        </div>
                      </div>

                      {/* Fact Check */}
                      <div className={styles.insightCard}>
                        <span className={styles.insightTitle}>Fact Check Status</span>
                        <div className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                          result.factCheck.status === 'PASSED' ? 'bg-success/20 text-success' : 'bg-warning/20 text-warning'
                        }`}>
                          {result.factCheck.status}
                        </div>
                      </div>

                      {/* SEO */}
                      <div className={styles.insightCard}>
                        <span className={styles.insightTitle}>SEO Keywords</span>
                        <div className={styles.tagList}>
                          {result.seo.primaryKeywords.map(kw => (
                            <span key={kw} className={styles.tag}>{kw}</span>
                          ))}
                        </div>
                      </div>

                      {/* Image Prompt */}
                      <div className={styles.insightCard}>
                        <span className={styles.insightTitle}>Image Concept</span>
                        <p className="text-xs text-secondary leading-relaxed">{result.imagePrompt.prompt}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
