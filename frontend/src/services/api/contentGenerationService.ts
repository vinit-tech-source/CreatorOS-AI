export interface ContentRequest {
  workspaceId: string;
  projectId: string;
  platform: string;
  contentType: string;
  userRequest: string;
  targetAudience?: string;
  tone?: string;
  language: string;
  additionalInstructions?: string;
}

export interface GenerationResult {
  title: string;
  content: string;
  platform: string;
  contentType: string;
  hashtags: { tag: string; isNiche: boolean; relevanceScore: number }[];
  cta: string;
  imagePrompt: {
    visualStyle: string;
    composition: string;
    aspectRatio: string;
    lighting: string;
    colorPalette: string;
    altText: string;
    prompt: string;
  };
  brandVoice: {
    score: number;
    isCompliant: boolean;
    issues: string[];
    changesMade: string[];
  };
  factCheck: {
    status: 'PASSED' | 'NEEDS_REVIEW' | 'FAILED';
    issues: {
      claim: string;
      status: string;
      explanation: string;
      confidence: number;
      evidence?: string;
    }[];
  };
  seo: {
    score: number;
    primaryKeywords: string[];
    secondaryKeywords: string[];
    recommendations: string[];
  };
}

import { apiClient } from './client';

export const contentGenerationService = {
  generateContent: async (request: ContentRequest): Promise<GenerationResult> => {
    // Map camelCase to snake_case if necessary for backend mapping, 
    // although our Pydantic schema expects snake_case, the Axios client or schema 
    // needs to send the right structure.
    const payload = {
      workspace_id: request.workspaceId,
      project_id: request.projectId,
      platform: request.platform,
      content_type: request.contentType,
      user_request: request.userRequest,
      target_audience: request.targetAudience,
      tone: request.tone,
      language: request.language,
      additional_instructions: request.additionalInstructions
    };
    
    const response = await apiClient.post('/content/generate', payload);
    return response.data.data;
  }
};
