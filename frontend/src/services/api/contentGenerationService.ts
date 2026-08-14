export interface ContentRequest {
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

export const contentGenerationService = {
  // Mock endpoint simulating the LangGraph async workflow
  generateContent: async (request: ContentRequest): Promise<GenerationResult> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          title: `Exciting Update for ${request.platform}`,
          content: `Here is the AI-generated draft based on your request: "${request.userRequest}". It is optimized for ${request.platform} and aligned with your brand voice.\n\nEnjoy engaging your audience!`,
          platform: request.platform,
          contentType: request.contentType,
          hashtags: [
            { tag: 'CreatorOS', isNiche: false, relevanceScore: 95 },
            { tag: 'AIContent', isNiche: false, relevanceScore: 90 },
            { tag: 'SocialMediaStrategy', isNiche: true, relevanceScore: 85 }
          ],
          cta: 'Sign up today to transform your workflow!',
          imagePrompt: {
            visualStyle: 'Photorealistic',
            composition: 'Wide shot, subject in center',
            aspectRatio: '16:9',
            lighting: 'Cinematic lighting, golden hour',
            colorPalette: 'Warm tones, vibrant contrasts',
            altText: 'A professional workspace glowing with warm sunset light.',
            prompt: 'A sleek, modern desk setup with a glowing monitor displaying abstract AI nodes. Cinematic lighting, photorealistic, 8k resolution.'
          },
          brandVoice: {
            score: 92,
            isCompliant: true,
            issues: [],
            changesMade: [
              'Adjusted tone to be more professional and encouraging.',
              'Replaced generic greetings with brand-specific terminology.'
            ]
          },
          factCheck: {
            status: 'PASSED',
            issues: []
          },
          seo: {
            score: 88,
            primaryKeywords: ['AI content generation', 'social media strategy'],
            secondaryKeywords: ['CreatorOS', 'automation', 'productivity'],
            recommendations: [
              'Consider adding a keyword to the first sentence.',
              'The content length is optimal for the platform.'
            ]
          }
        });
      }, 5000); // 5 seconds delay to simulate generation
    });
  }
};
