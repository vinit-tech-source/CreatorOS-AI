import { useState } from 'react';
import { Input } from './Input';
import { Button } from './Button';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import styles from './CreateWorkspaceModal.module.css';

interface CreateWorkspaceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CreateWorkspaceModal({ isOpen, onClose }: CreateWorkspaceModalProps) {
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const { createWorkspace, isLoading, error } = useWorkspaceStore();
  const [localError, setLocalError] = useState<string | null>(null);

  if (!isOpen) return null;

  // Auto-generate slug from name
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value;
    setName(newName);
    
    // Only auto-update slug if user hasn't explicitly modified it to be completely different
    // Basically just lowercase, replace spaces with hyphens, remove non-alphanumeric
    const generatedSlug = newName
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
      
    setSlug(generatedSlug);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    try {
      await createWorkspace({ name, slug, description });
      // If successful, close modal and reset form
      onClose();
      setName('');
      setSlug('');
      setDescription('');
    } catch (err: any) {
      // Error is already handled and set in the store, but we catch here to prevent modal from closing
      setLocalError(err.message || 'Failed to create workspace');
    }
  };

  const displayError = localError || error;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>Create New Workspace</h2>
          <p className={styles.subtitle}>Set up a new organization for your team's projects.</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {displayError && (
            <div className={styles.errorBox}>
              {displayError}
            </div>
          )}

          <Input
            label="Workspace Name"
            value={name}
            onChange={handleNameChange}
            placeholder="Acme Corp"
            required
            autoFocus
          />

          <Input
            label="Workspace Slug"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder="acme-corp"
            required
          />

          <Input
            label="Description (Optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Main workspace for Acme's marketing team"
          />

          <div className={styles.footer}>
            <Button variant="ghost" onClick={onClose} type="button" disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" isLoading={isLoading}>
              Create Workspace
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
