import { useState } from 'react';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { ContentRequest } from '../../../services/api/contentGenerationService';

interface CreationFormProps {
  projectId: string;
  onSubmit: (request: ContentRequest) => void;
  isLoading: boolean;
}

export function CreationForm({ projectId, onSubmit, isLoading }: CreationFormProps) {
  const [platform, setPlatform] = useState('X');
  const [contentType, setContentType] = useState('Standard Post');
  const [userRequest, setUserRequest] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [tone, setTone] = useState('');
  const [language, setLanguage] = useState('English');
  const [additionalInstructions, setAdditionalInstructions] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      projectId,
      platform,
      contentType,
      userRequest,
      targetAudience,
      tone,
      language,
      additionalInstructions
    });
  };

  return (
    <Card glass>
      <CardHeader title="Create Content" subtitle="Provide details to generate your AI post" />
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Platform *</label>
              <select 
                className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary"
                value={platform}
                onChange={e => setPlatform(e.target.value)}
                required
              >
                <option value="X">X (Twitter)</option>
                <option value="LINKEDIN">LinkedIn</option>
                <option value="INSTAGRAM">Instagram</option>
                <option value="FACEBOOK">Facebook</option>
                <option value="THREADS">Threads</option>
                <option value="BLUESKY">Bluesky</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Content Type *</label>
              <select 
                className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary"
                value={contentType}
                onChange={e => setContentType(e.target.value)}
                required
              >
                <option value="Standard Post">Standard Post</option>
                <option value="Thread">Thread</option>
                <option value="Carousel">Carousel</option>
                <option value="Video Script">Video Script</option>
              </select>
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium">What do you want to post about? *</label>
            <textarea
              className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary min-h-[100px] resize-y"
              value={userRequest}
              onChange={e => setUserRequest(e.target.value)}
              placeholder="E.g., Announce our new AI features launching next week..."
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input 
              label="Target Audience (Optional)"
              value={targetAudience}
              onChange={e => setTargetAudience(e.target.value)}
              placeholder="E.g., Tech Founders, Marketing Managers"
            />
            <Input 
              label="Tone (Optional)"
              value={tone}
              onChange={e => setTone(e.target.value)}
              placeholder="E.g., Professional, witty, urgent"
            />
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Language *</label>
              <select 
                className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary"
                value={language}
                onChange={e => setLanguage(e.target.value)}
                required
              >
                <option value="English">English</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="German">German</option>
              </select>
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium">Additional Instructions (Optional)</label>
            <textarea
              className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary min-h-[60px] resize-y"
              value={additionalInstructions}
              onChange={e => setAdditionalInstructions(e.target.value)}
              placeholder="Any specific constraints or ideas..."
            />
          </div>

          <div className="flex justify-end mt-4">
            <Button type="submit" variant="primary" isLoading={isLoading}>
              Generate Content
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
