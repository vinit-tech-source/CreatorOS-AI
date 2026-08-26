import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { Sparkles } from 'lucide-react';


import styles from './QuickActions.module.css';

export function QuickActions() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/create?q=${encodeURIComponent(query)}`);
    } else {
      navigate('/create');
    }
  };

  const suggestions = [
    "Create 5 LinkedIn posts about AI agents.",
    "Post one X thread every day about GenAI.",
    "Create Instagram content for my startup."
  ];

  return (
    <Card glass className="overflow-hidden border-primary/30 shadow-[0_0_20px_rgba(var(--color-primary-rgb),0.15)] relative">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent pointer-events-none" />
      <CardContent className="p-8 relative z-10">
        <div className="flex flex-col gap-4">
          <h2 className="text-2xl font-semibold text-primary">What do you want to create?</h2>
          
          <form onSubmit={handleCreate} className="flex flex-col gap-4">
            <textarea
              className={styles.textarea}
              rows={3}
              placeholder="Tell CreatorOS what you want to post..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            
            <div className="flex justify-between items-center">
              <div className={styles.suggestionsContainer}>
                {suggestions.map((suggestion, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setQuery(suggestion)}
                    className={styles.suggestionButton}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
              
              <Button type="submit" variant="primary" className="ml-4 whitespace-nowrap">
                <Sparkles size={16} className="mr-2" />
                Create Content
              </Button>
            </div>
          </form>
        </div>
      </CardContent>
    </Card>
  );
}
