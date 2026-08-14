import { useState } from 'react';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { Badge } from '../../../components/ui/Badge';
import { GenerationResult } from '../../../services/api/contentGenerationService';
import { ShieldCheck, ShieldAlert, Sparkles, Target, Hash, Image as ImageIcon, X } from 'lucide-react';

interface DraftResultProps {
  result: GenerationResult;
  onSaveDraft: (data: Partial<GenerationResult>) => Promise<void>;
  onSubmitReview: (data: Partial<GenerationResult>) => Promise<void>;
  isSaving: boolean;
  isSubmitting: boolean;
}

export function DraftResult({ result, onSaveDraft, onSubmitReview, isSaving, isSubmitting }: DraftResultProps) {
  const [title, setTitle] = useState(result.title);
  const [content, setContent] = useState(result.content);
  const [cta, setCta] = useState(result.cta);
  const [hashtags, setHashtags] = useState(result.hashtags);
  
  // Image metadata editing
  const [imagePrompt, setImagePrompt] = useState(result.imagePrompt.prompt);
  const [altText, setAltText] = useState(result.imagePrompt.altText);

  const removeHashtag = (tagToRemove: string) => {
    setHashtags(hashtags.filter(h => h.tag !== tagToRemove));
  };

  const getEditedData = () => ({
    title,
    content,
    cta,
    hashtags,
    imagePrompt: { ...result.imagePrompt, prompt: imagePrompt, altText }
  });

  return (
    <div className="flex flex-col gap-6">
      
      {/* Editor Section */}
      <Card glass>
        <CardHeader 
          title="Generated Draft" 
          subtitle={`Optimized for ${result.platform} - ${result.contentType}`} 
        />
        <CardContent className="flex flex-col gap-4">
          <Input 
            label="Title (Internal)"
            value={title}
            onChange={e => setTitle(e.target.value)}
          />
          
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium">Post Content</label>
            <textarea
              className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary min-h-[150px] resize-y"
              value={content}
              onChange={e => setContent(e.target.value)}
            />
          </div>

          <Input 
            label="Call to Action (CTA)"
            value={cta}
            onChange={e => setCta(e.target.value)}
          />

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Hash size={16} /> Hashtags
            </label>
            <div className="flex flex-wrap gap-2">
              {hashtags.map(h => (
                <div key={h.tag} className="flex items-center gap-1 px-2 py-1 bg-surface border border-border rounded-full text-xs font-medium">
                  #{h.tag}
                  <button type="button" onClick={() => removeHashtag(h.tag)} className="text-secondary hover:text-danger rounded-full p-0.5">
                    <X size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Fact Check */}
        <Card glass>
          <CardHeader title={<><ShieldCheck size={18} className="inline-block mr-2" />Fact Check</>} />
          <CardContent>
            <div className="mb-4">
              <Badge variant={result.factCheck.status === 'PASSED' ? 'success' : result.factCheck.status === 'FAILED' ? 'danger' : 'warning'}>
                {result.factCheck.status}
              </Badge>
            </div>
            {result.factCheck.issues.length === 0 ? (
              <p className="text-sm text-secondary">No factual issues detected.</p>
            ) : (
              <ul className="text-sm flex flex-col gap-2">
                {result.factCheck.issues.map((issue, i) => (
                  <li key={i} className="flex gap-2 bg-danger/10 p-2 rounded-md">
                    <ShieldAlert size={16} className="text-danger flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-danger">{issue.claim}</p>
                      <p className="text-xs text-secondary mt-1">{issue.explanation}</p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Brand Voice */}
        <Card glass>
          <CardHeader title={<><Sparkles size={18} className="inline-block mr-2" />Brand Voice</>} />
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium">Score</span>
              <span className={`text-lg font-bold ${result.brandVoice.score >= 90 ? 'text-success' : 'text-warning'}`}>
                {result.brandVoice.score}/100
              </span>
            </div>
            <div className="text-sm text-secondary">
              <p className="font-semibold mb-1 text-text-primary">Changes made:</p>
              <ul className="list-disc pl-4 flex flex-col gap-1">
                {result.brandVoice.changesMade.map((change, i) => (
                  <li key={i}>{change}</li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* SEO */}
        <Card glass>
          <CardHeader title={<><Target size={18} className="inline-block mr-2" />SEO Optimization</>} />
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium">Score</span>
              <span className="text-lg font-bold text-success">{result.seo.score}/100</span>
            </div>
            <div className="text-sm text-secondary flex flex-col gap-3">
              <div>
                <p className="font-semibold text-text-primary">Keywords</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {result.seo.primaryKeywords.map(k => <span key={k} className="px-1.5 py-0.5 bg-primary/10 text-primary text-xs rounded">{k}</span>)}
                </div>
              </div>
              <div>
                <p className="font-semibold text-text-primary">Recommendations</p>
                <ul className="list-disc pl-4 mt-1">
                  {result.seo.recommendations.map((rec, i) => <li key={i}>{rec}</li>)}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Image Prompt Metadata */}
      <Card glass>
        <CardHeader title={<><ImageIcon size={18} className="inline-block mr-2" />Suggested Visuals</>} />
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium">Image Prompt</label>
            <textarea
              className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary min-h-[60px] resize-y"
              value={imagePrompt}
              onChange={e => setImagePrompt(e.target.value)}
            />
          </div>
          <Input 
            label="Accessibility (Alt Text)"
            value={altText}
            onChange={e => setAltText(e.target.value)}
          />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-secondary mt-2">
            <div className="bg-surface p-2 rounded border border-border"><b>Style:</b> {result.imagePrompt.visualStyle}</div>
            <div className="bg-surface p-2 rounded border border-border"><b>Comp:</b> {result.imagePrompt.composition}</div>
            <div className="bg-surface p-2 rounded border border-border"><b>Ratio:</b> {result.imagePrompt.aspectRatio}</div>
            <div className="bg-surface p-2 rounded border border-border"><b>Light:</b> {result.imagePrompt.lighting}</div>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 mt-4">
        <Button 
          variant="outline" 
          onClick={() => onSaveDraft(getEditedData())}
          isLoading={isSaving}
          disabled={isSubmitting}
        >
          Save Draft
        </Button>
        <Button 
          variant="primary" 
          onClick={() => onSubmitReview(getEditedData())}
          isLoading={isSubmitting}
          disabled={isSaving}
        >
          Submit for Review
        </Button>
      </div>

    </div>
  );
}
