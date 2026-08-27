import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import styles from './PipelineProgress.module.css';

const agents = [
  { id: '01', name: 'Strategy Agent', description: 'Sets goal, audience, and format', status: 'waiting' },
  { id: '02', name: 'Trend Agent', description: 'Finds current trends and keywords', status: 'waiting' },
  { id: '03', name: 'Research Agent', description: 'Gathers facts and statistics', status: 'waiting' },
  { id: '04', name: 'Content Planner', description: 'Builds a logical outline', status: 'waiting' },
  { id: '05', name: 'Content Generator', description: 'Drafts the post', status: 'waiting' },
  { id: '06', name: 'Brand Voice Agent', description: 'Checks tone against your rules', status: 'waiting' },
  { id: '07', name: 'Fact Check Agent', description: 'Verifies every claim', status: 'waiting' },
  { id: '08', name: 'SEO Agent', description: 'Optimizes for discovery', status: 'waiting' },
  { id: '09', name: 'Hashtag Agent', description: 'Adds relevant tags', status: 'waiting' },
  { id: '10', name: 'Image Prompt Agent', description: 'Writes the visual brief', status: 'waiting' },
];

export function PipelineProgress() {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.liveRunBadge}>LIVE RUN</span>
        <PageHeader 
          title="Pipeline" 
          subtitle="Ten agents, run in order. Each one reads what the last one wrote." 
        />
      </div>
      
      <div className={styles.layout}>
        {/* Left Column: Agents List */}
        <div className={styles.agentsList}>
          {agents.map((agent) => (
            <div key={agent.id} className={styles.agentCard}>
              <div className={styles.agentNumber}>{agent.id}</div>
              <div className={styles.agentInfo}>
                <h3 className={styles.agentName}>{agent.name}</h3>
                <p className={styles.agentDescription}>{agent.description}</p>
              </div>
              <div className={styles.agentStatus}>
                <span className={styles.statusBadge}>{agent.status}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Right Column: Run Status */}
        <div className={styles.statusSidebar}>
          <div className={styles.statusCard}>
            <h3 className={styles.statusTitle}>Run status</h3>
            <p className={styles.statusText}>Idle — no run in progress.</p>
            <Button className={styles.runButton} fullWidth>
              Run pipeline
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
