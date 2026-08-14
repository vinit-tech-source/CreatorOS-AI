import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PostList } from '../src/pages/posts/PostList';
import { PostDetails } from '../src/pages/posts/PostDetails';
import { postManagementService } from '../src/services/api/postManagementService';

vi.mock('../src/services/api/postManagementService', () => ({
  postManagementService: {
    getPosts: vi.fn(),
    getPost: vi.fn(),
    updatePost: vi.fn(),
    submitForReview: vi.fn(),
    approvePost: vi.fn(),
    rejectPost: vi.fn(),
    schedulePost: vi.fn(),
    cancelSchedule: vi.fn(),
  }
}));

// Mock react-router-dom params
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ workspaceId: 'ws-1', projectId: 'proj-1', postId: 'post-1' }),
    useNavigate: () => vi.fn()
  };
});

const mockPost = {
  id: 'post-1',
  project_id: 'proj-1',
  title: 'Test Post',
  content: 'Test Content',
  platform: 'X',
  status: 'DRAFT',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

describe('Post Management', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('PostList', () => {
    it('renders posts and supports filtering', async () => {
      const posts = [
        mockPost,
        { ...mockPost, id: 'post-2', title: 'Another Post', status: 'PUBLISHED', platform: 'LINKEDIN' }
      ];
      (postManagementService.getPosts as any).mockResolvedValue(posts);

      render(
        <BrowserRouter>
          <PostList />
        </BrowserRouter>
      );

      expect(screen.getByText('Loading posts...')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText('Test Post')).toBeInTheDocument();
        expect(screen.getByText('Another Post')).toBeInTheDocument();
      });

      // Filter by status
      const statusSelect = screen.getAllByRole('combobox')[0]; // Status filter
      fireEvent.change(statusSelect, { target: { value: 'PUBLISHED' } });

      await waitFor(() => {
        expect(screen.queryByText('Test Post')).not.toBeInTheDocument();
        expect(screen.getByText('Another Post')).toBeInTheDocument();
      });
    });
  });

  describe('PostDetails', () => {
    it('renders details and handles approval flow', async () => {
      // Start as DRAFT
      (postManagementService.getPost as any).mockResolvedValue(mockPost);
      
      render(
        <BrowserRouter>
          <PostDetails />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('Test Post')).toBeInTheDocument();
        // Should show Submit for Review
        expect(screen.getByText('Submit for Review')).toBeInTheDocument();
      });

      // Simulate Submit for Review
      (postManagementService.submitForReview as any).mockResolvedValue({ ...mockPost, status: 'PENDING_REVIEW' });
      fireEvent.click(screen.getByText('Submit for Review'));

      await waitFor(() => {
        expect(postManagementService.submitForReview).toHaveBeenCalledWith('proj-1', 'post-1');
      });

      // Rerender with PENDING_REVIEW state (simulated by updating getPost mock and manually triggering a re-render is tricky, so we'll just test the buttons appear when status is PENDING_REVIEW)
    });

    it('shows approve/reject for PENDING_REVIEW and scheduling for APPROVED', async () => {
      (postManagementService.getPost as any).mockResolvedValue({ ...mockPost, status: 'PENDING_REVIEW' });
      
      const { unmount } = render(
        <BrowserRouter>
          <PostDetails />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Approve')).toBeInTheDocument();
        expect(screen.getByText('Reject')).toBeInTheDocument();
      });

      unmount();

      (postManagementService.getPost as any).mockResolvedValue({ ...mockPost, status: 'APPROVED' });
      
      render(
        <BrowserRouter>
          <PostDetails />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Schedule Post')).toBeInTheDocument();
        expect(screen.getByText('Schedule')).toBeInTheDocument();
      });
    });

    it('requires confirmation for reject', async () => {
      (postManagementService.getPost as any).mockResolvedValue({ ...mockPost, status: 'PENDING_REVIEW' });
      
      render(
        <BrowserRouter>
          <PostDetails />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Reject')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Reject')); // Opens reject reason input

      const rejectInput = screen.getByPlaceholderText(/Explain what needs to be changed/i);
      fireEvent.change(rejectInput, { target: { value: 'Not good enough' } });

      const confirmSpy = vi.spyOn(window, 'confirm').mockImplementation(() => true);
      (postManagementService.rejectPost as any).mockResolvedValue({ ...mockPost, status: 'REJECTED' });

      fireEvent.click(screen.getByText('Confirm Reject'));

      await waitFor(() => {
        expect(confirmSpy).toHaveBeenCalled();
        expect(postManagementService.rejectPost).toHaveBeenCalledWith('proj-1', 'post-1', 'Not good enough');
      });
    });
  });
});
