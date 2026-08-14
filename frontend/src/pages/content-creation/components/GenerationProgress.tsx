import { useEffect, useState } from 'react';
import { Card, CardContent } from '../../../components/ui/Card';
import { Loader2, CheckCircle2, Circle } from 'lucide-react';

const STAGES = [
  'Preparing strategy',
  'Analyzing trends',
  'Researching',
  'Planning content',
  'Generating draft',
  'Checking brand voice',
  'Fact checking',
  'Optimizing',
  'Generating hashtags',
  'Preparing image prompt'
];

export function GenerationProgress() {
  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    // We simulate a 5 second generation process
    // There are 10 stages, so we advance every 500ms
    const interval = setInterval(() => {
      setCurrentStage(prev => {
        if (prev >= STAGES.length - 1) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <Card glass>
      <CardContent className="p-8">
        <div className="flex flex-col items-center justify-center mb-8">
          <Loader2 className="animate-spin text-primary mb-4" size={48} />
          <h2 className="text-xl font-bold">Generating Content...</h2>
          <p className="text-secondary">Please wait while the AI crafts your perfect post.</p>
        </div>

        <div className="max-w-md mx-auto grid grid-cols-1 gap-3">
          {STAGES.map((stage, index) => {
            const isCompleted = index < currentStage;
            const isCurrent = index === currentStage;
            
            return (
              <div 
                key={stage} 
                className={`flex items-center gap-3 transition-opacity duration-300 ${isCompleted || isCurrent ? 'opacity-100' : 'opacity-40'}`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="text-success" size={20} />
                ) : isCurrent ? (
                  <Loader2 className="animate-spin text-primary" size={20} />
                ) : (
                  <Circle className="text-secondary" size={20} />
                )}
                <span className={`text-sm ${isCurrent ? 'font-semibold text-primary' : isCompleted ? 'text-text-primary' : 'text-secondary'}`}>
                  {stage}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
