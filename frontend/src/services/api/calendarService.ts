import { projectService } from './projectService';
import { postManagementService } from './postManagementService';
import { Post } from '../../types';

export const calendarService = {
  /**
   * Fetches all scheduled and published posts across all projects in a workspace.
   */
  getWorkspaceCalendarPosts: async (workspaceId: string): Promise<Post[]> => {
    try {
      // 1. Get all projects for the workspace
      const projects = await projectService.getProjects(workspaceId);
      
      // 2. Fetch posts for each project concurrently
      const allPostsPromises = projects.map(project => 
        postManagementService.getPosts(project.id)
      );
      
      const projectPostsArrays = await Promise.all(allPostsPromises);
      
      // 3. Flatten and filter to only include posts that have a scheduled date or are published
      const allPosts = projectPostsArrays.flat();
      return allPosts.filter((post: Post) => 
        (post.status === 'SCHEDULED' || post.status === 'PUBLISHED') && post.scheduled_for
      );
    } catch (error) {
      console.error('Failed to aggregate workspace posts for calendar:', error);
      throw error;
    }
  }
};
