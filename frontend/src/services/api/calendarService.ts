import { projectService } from './projectService';
import { postManagementService } from './postManagementService';
import { Post, Project } from '../../types';

export interface CalendarPost extends Post {
  projectName?: string;
}

export const calendarService = {
  /**
   * Fetches all scheduled, published, and dated posts across all projects in a workspace.
   */
  getWorkspaceCalendarPosts: async (workspaceId: string): Promise<CalendarPost[]> => {
    try {
      // 1. Get all projects for the workspace
      const projects: Project[] = await projectService.getProjects(workspaceId);
      
      if (!projects || projects.length === 0) {
        return [];
      }

      // 2. Fetch posts for each project concurrently
      const allPostsPromises = projects.map(async (project) => {
        try {
          const posts = await postManagementService.getPosts(project.id);
          return posts.map(p => ({
            ...p,
            projectName: project.name
          }));
        } catch (err) {
          console.warn(`Could not load posts for project ${project.id}:`, err);
          return [];
        }
      });
      
      const projectPostsArrays = await Promise.all(allPostsPromises);
      
      // 3. Flatten and return all posts that have a scheduled date or are published/scheduled
      const allPosts = projectPostsArrays.flat();
      return allPosts.filter((post: CalendarPost) => 
        Boolean(post.scheduled_for) || post.status === 'SCHEDULED' || post.status === 'PUBLISHED'
      );
    } catch (error) {
      console.error('Failed to aggregate workspace posts for calendar:', error);
      throw error;
    }
  },

  /**
   * Reschedules an already scheduled post to a new timestamp.
   */
  reschedulePost: async (
    projectId: string,
    postId: string,
    scheduledAtIso: string,
    timezone?: string
  ): Promise<Post> => {
    const tz = timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    return await postManagementService.reschedulePost(projectId, postId, scheduledAtIso, tz);
  },

  /**
   * Cancels the scheduled release of a post.
   */
  cancelSchedule: async (projectId: string, postId: string): Promise<Post> => {
    return await postManagementService.cancelSchedule(projectId, postId);
  },

  /**
   * Quickly creates, approves, and schedules a post directly from the calendar.
   */
  quickCreateAndSchedule: async (
    projectId: string,
    data: {
      title?: string;
      content: string;
      platform: string;
      scheduled_at: string;
      timezone?: string;
    }
  ): Promise<Post> => {
    const tz = data.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    
    // 1. Create post
    const created = await postManagementService.createPost(projectId, {
      title: data.title || undefined,
      content: data.content,
      platform: data.platform
    });

    // 2. Promote to approved state so scheduler accepts it
    await postManagementService.submitForReview(projectId, created.id);
    await postManagementService.approvePost(projectId, created.id);

    // 3. Schedule it
    return await postManagementService.schedulePost(projectId, created.id, data.scheduled_at, tz);
  }
};
