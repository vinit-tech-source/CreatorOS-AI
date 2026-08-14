import { describe, it, expect, vi, beforeEach } from 'vitest';
import { contentGenerationService, ContentRequest } from './contentGenerationService';
import { apiClient } from './client';

vi.mock('./client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

describe('contentGenerationService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('generateContent should map payload and return data', async () => {
    const mockRequest: ContentRequest = {
      workspaceId: 'ws-123',
      projectId: 'proj-123',
      platform: 'X',
      contentType: 'Standard Post',
      userRequest: 'Tell me about AI',
      targetAudience: 'Devs',
      tone: 'Professional',
      language: 'English',
      additionalInstructions: 'Keep it short',
    };

    const mockResponse = {
      data: {
        data: {
          title: 'Draft Title',
          content: 'Hello AI',
          platform: 'X',
          contentType: 'Standard Post',
          hashtags: [],
          cta: 'Comment below!',
          imagePrompt: {},
          brandVoice: {},
          factCheck: {},
          seo: {},
        }
      }
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    const result = await contentGenerationService.generateContent(mockRequest);

    expect(apiClient.post).toHaveBeenCalledWith('/content/generate', {
      workspace_id: 'ws-123',
      project_id: 'proj-123',
      platform: 'X',
      content_type: 'Standard Post',
      user_request: 'Tell me about AI',
      target_audience: 'Devs',
      tone: 'Professional',
      language: 'English',
      additional_instructions: 'Keep it short',
    });

    expect(result).toEqual(mockResponse.data.data);
  });
});
