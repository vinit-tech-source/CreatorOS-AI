import { useState } from 'react';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { Post } from '../../../types';


interface PostEditorProps {
  post: Post;
  onSave: (data: Partial<Post>) => Promise<void>;
  isSaving: boolean;
}

export function PostEditor({ post, onSave, isSaving }: PostEditorProps) {
  const [title, setTitle] = useState(post.title || '');
  const [content, setContent] = useState(post.content || '');

  const handleSave = () => {
    onSave({
      title,
      content,
    });
  };

  const isEditable = post.status === 'DRAFT' || post.status === 'REJECTED';

  if (!isEditable) {
    return (
      <Card glass>
        <CardHeader title="Post Content" subtitle={`Editing is disabled because post is ${post.status}`} />
        <CardContent>
          <div className="flex flex-col gap-4">
            <div>
              <p className="text-sm font-medium text-secondary mb-1">Title</p>
              <p className="p-3 bg-surface border border-border rounded-md text-sm">{post.title || 'Untitled'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-secondary mb-1">Content</p>
              <p className="p-3 bg-surface border border-border rounded-md text-sm whitespace-pre-wrap">{post.content}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card glass>
      <CardHeader title="Edit Post" subtitle="Modify the content of this draft" />
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

        <div className="flex justify-end mt-2">
          <Button 
            variant="primary" 
            onClick={handleSave} 
            isLoading={isSaving}
          >
            Save Changes
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
