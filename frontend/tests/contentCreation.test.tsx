import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ContentCreation } from '../src/pages/content-creation/ContentCreation';
import { contentGenerationService } from '../src/services/api/contentGenerationService';
import { apiClient } from '../src/services/api';

vi.mock('../src/services/api/contentGenerationService', () => ({
  contentGenerationService: {
    generateContent: vi.fn()
  }
}));

vi.mock('../src/services/api', () => ({
  apiClient: {
    post: vi.fn()
  }
}));

// Mock react-router-dom params
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ workspaceId: 'ws-1', projectId: 'proj-1' }),
    useNavigate: () => vi.fn()
  };
});

const renderContentCreation = () => {
  return render(
    <BrowserRouter>
      <ContentCreation />
    </BrowserRouter>
  );
};

describe('Content Creation Workflow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders creation form initially', () => {
    renderContentCreation();
    expect(screen.getByText('Create Content')).toBeInTheDocument();
    expect(screen.getByText('Generate Content')).toBeInTheDocument();
  });

  it('transitions to generating state and then result state', async () => {
    const mockResult = {
      title: 'Mock Title',
      content: 'Mock Content',
      platform: 'X',
      contentType: 'Standard Post',
      hashtags: [{ tag: 'test', isNiche: false, relevanceScore: 100 }],
      cta: 'Click here',
      imagePrompt: { visualStyle: '', composition: '', aspectRatio: '', lighting: '', colorPalette: '', altText: '', prompt: 'mock prompt' },
      brandVoice: { score: 100, isCompliant: true, issues: [], changesMade: [] },
      factCheck: { status: 'PASSED', issues: [] },
      seo: { score: 100, primaryKeywords: [], secondaryKeywords: [], recommendations: [] }
    };

    (contentGenerationService.generateContent as any).mockResolvedValue(mockResult);

    renderContentCreation();

    // Fill the required user request field
    const requestInput = screen.getByPlaceholderText(/E.g., Announce our new AI features/i);
    fireEvent.change(requestInput, { target: { value: 'Write a post about AI' } });

    // Submit form
    const generateBtn = screen.getByText('Generate Content');
    fireEvent.click(generateBtn);

    // Should show generating progress
    expect(screen.getByText('Generating Content...')).toBeInTheDocument();

    // Eventually shows result
    await waitFor(() => {
      expect(screen.getByText('Generated Draft')).toBeInTheDocument();
      expect(screen.getByText('Save Draft')).toBeInTheDocument();
    });
  });

  it('calls backend to save draft', async () => {
    const mockResult = {
      title: 'Mock Title',
      content: 'Mock Content',
      platform: 'X',
      contentType: 'Standard Post',
      hashtags: [],
      cta: 'Click here',
      imagePrompt: { visualStyle: '', composition: '', aspectRatio: '', lighting: '', colorPalette: '', altText: '', prompt: 'mock prompt' },
      brandVoice: { score: 100, isCompliant: true, issues: [], changesMade: [] },
      factCheck: { status: 'PASSED', issues: [] },
      seo: { score: 100, primaryKeywords: [], secondaryKeywords: [], recommendations: [] }
    };

    (contentGenerationService.generateContent as any).mockResolvedValue(mockResult);
    (apiClient.post as any).mockResolvedValue({ data: { success: true } });

    // mock window alert
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});

    renderContentCreation();

    const requestInput = screen.getByPlaceholderText(/E.g., Announce our new AI features/i);
    fireEvent.change(requestInput, { target: { value: 'Write a post about AI' } });
    fireEvent.click(screen.getByText('Generate Content'));

    await waitFor(() => {
      expect(screen.getByText('Save Draft')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Save Draft'));

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith('/projects/proj-1/posts', expect.objectContaining({
        status: 'DRAFT'
      }));
      expect(alertMock).toHaveBeenCalledWith('Draft saved successfully!');
    });
  });
});
